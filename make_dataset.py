# mvp_backfill.py
# Coleta histórico "massivo" de notícias (GDELT Doc API + opcional NewsAPI),
# aplica filtros e scoring semelhantes ao mvp_local.py, e gera dataset TOP-K
# em labeling/to_label.csv (sem mexer no seu mvp_local.py original).
#
# Requisitos: requests, pandas, tqdm, vaderSentiment, python-dateutil
#
# Exemplos:
#   python mvp_backfill.py --from 2025-08-01 --to 2025-09-01 --top-k 10000
#   python mvp_backfill.py --from 2025-06-01 --to 2025-09-01 --domains valor.globo.com,infomoney.com.br,reuters.com,cnbc.com,wsj.com --top-k 10000

import os
import re
import math
import time
import json
import argparse
import hashlib
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

import requests
import pandas as pd
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dateutil import parser as dtparser

warnings.filterwarnings("ignore", category=UserWarning)

# =========================
# Config / Perfis de marca
# =========================
BRAND_PROFILE = {
    "planejamento_patrimonial": {
        "weight": 1.0,
        "kw": [
            "planejamento patrimonial","gestão patrimonial","proteção patrimonial","governança familiar",
            "holding familiar","sucessão","herança","testamento","trust","offshore","blindagem lícita",
            "estate planning","wealth planning","asset protection","family governance","trusts"
        ]
    },
    "preservacao_risco": {
        "weight": 0.9,
        "kw": ["preservação de patrimônio","segurança","estabilidade","diversificação","alocação",
               "gestão de risco","hedge","seguro patrimonial","volatilidade","proteção"]
    },
    "sucessao_legado": {
        "weight": 0.9,
        "kw": ["planejamento sucessório","legado","next-gen","educação financeira","transição geracional",
               "family office","fundos exclusivos","fip","fii"]
    },
    "fiscal_estrutural": {
        "weight": 0.75,
        "kw": ["tributação","impostos","reforma tributária","itcmd","ir","estruturação","custo fiscal",
               "eficiência fiscal","tax planning"]
    },
    "mercado_relevante": {
        "weight": 0.65,
        "kw": ["selic","copom","ipca","juros","inflação","câmbio","dólar","fed","ecb","treasury",
               "s&p 500","nasdaq","volatilidade","recessão","crescimento","guidance","resultado","dividendos"]
    },
    "impacto_filantropia_sustentavel": {
        "weight": 0.6,
        "kw": ["filantropia","impacto social","investimento sustentável","esg","projetos sociais",
               "fundos filantrópicos","endowment"]
    },
}
BRAND_NEGATIVE_KW = ["fofoca","celebridade","escândalo","polêmica vazia","crime bárbaro","clickbait","tabloide","viral inútil"]

# Autoridade por domínio (heurística)
DOMAIN_WEIGHTS = {
    "valor": 0.95, "infomoney": 0.90, "reuters": 0.98, "bloomberg": 0.98, "wsj": 0.90, "cnbc": 0.88,
    "bbc": 0.90, "ft": 0.96, "estadao": 0.88, "oglobo": 0.88, "folha": 0.86
}

# Ruído
CRIME_KW = ["assassinato","homicídio","homicidio","feminicídio","feminicidio","tiroteio","execução","executado",
            "estupr","estupro","latrocínio","latrocinio","tráfico","trafico","facada","bala perdida","agressão","agressao",
            "morto a tiros","morre após","corpo é encontrado"]
ACIDENTE_KW = ["acidente","colisão","colisao","capotagem","batida","engavetamento","cai de","queda de","desabamento","incêndio","incendio"]
TABLOIDE_KW = ["celebridade","fofoca","viralizou","influencer","reality","bbb"]
JORNAL_LOCAL_HINTS = ["vídeos:","videos:","jornal","edição","1ª edição","2ª edição","bom dia","eptv","jl1","jl2","df1"]

# Entidades simples
TICKER_PATTERNS = [re.compile(r"\b([A-Z]{4}\d)\.SA\b"), re.compile(r"\$([A-Z]{1,5})\b")]
TOPIC_KEYWORDS = {
    "selic","ipca","juros","inflação","inflacao","câmbio","cambio","dólar","dolar","fed","copom","cvm","sec",
    "balanço","balanco","guidance","dividendos","resultado","pil","gdp","payroll","petrobras","vale",
    "itau","ambev","magalu","b3","ibovespa","nasdaq","s&p500","opec"
}

# Saídas
OUT_DIR = "backfill_out"
DATASET_PATH = "labeling/to_label.csv"
REQUIRED_DIRS = ["labeling", OUT_DIR]

# =========================
# Utils / entidades / score
# =========================
def ensure_dirs():
    for d in REQUIRED_DIRS:
        os.makedirs(d, exist_ok=True)

def now_utc():
    return datetime.now(timezone.utc)

def parse_dt_any(s: str) -> Optional[datetime]:
    try:
        d = dtparser.parse(s)
        if not d.tzinfo:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None

def canonical_url(u: str) -> str:
    if not u: return ""
    u = u.strip()
    u = re.sub(r"(\?|#).*", "", u)
    return u.lower().rstrip("/")

def domain_from_url(u: str) -> str:
    m = re.search(r"https?://([^/]+)/", u + "/")
    if not m: return ""
    host = m.group(1).lower().replace("www.", "")
    return host

def short_host(host: str) -> str:
    h = host.replace(".com.br","").replace(".com","").replace(".globo","")
    parts = h.split(".")
    return parts[-1] if parts else h

def domain_weight(url: str) -> float:
    host = domain_from_url(url)
    sh = short_host(host)
    for k, v in DOMAIN_WEIGHTS.items():
        if k in host or k == sh:
            return v
    return 0.60

def _any_in(text: str, kws: List[str]) -> bool:
    t = text.lower()
    return any(k in t for k in kws)

def noise_penalty(headline: str) -> float:
    t = headline.lower()
    score = 0.0
    if _any_in(t, CRIME_KW):     score += 0.6
    if _any_in(t, ACIDENTE_KW):  score += 0.4
    if _any_in(t, TABLOIDE_KW):  score += 0.3
    if _any_in(t, JORNAL_LOCAL_HINTS): score += 0.4
    return min(1.0, score)

def extract_entities(text: str) -> Dict[str, List[str]]:
    text_low = text.lower()
    tickers = set()
    for pat in TICKER_PATTERNS:
        for m in pat.findall(text):
            tickers.add(m.lower() if isinstance(m, str) else m[0].lower())
    topics = {w for w in TOPIC_KEYWORDS if w in text_low}
    caps = set(re.findall(r"\b[A-Z]{2,6}\b", text))
    return {"tickers": sorted(tickers), "topics": sorted(topics), "caps": sorted(caps)}

def brand_fit_score(headline: str, entities: Dict[str, List[str]]) -> float:
    def _bag(*parts: str) -> str:
        return " ".join(p for p in parts if p).lower()
    bag = _bag(headline, " ".join(entities.get("topics", [])), " ".join(entities.get("tickers", [])))
    score = 0.0
    for _, cfg in BRAND_PROFILE.items():
        w = cfg.get("weight", 0.5)
        if any(kw.lower() in bag for kw in cfg.get("kw", [])):
            score += w
    score = min(1.0, score)
    if any(neg in bag for neg in BRAND_NEGATIVE_KW):
        score *= 0.7
    return score

def freshness_from_age(age_hours: float, tau_hours: float) -> float:
    # frescor para histórico: tau mais alto, menos punitivo
    return math.exp(-age_hours / tau_hours)

@dataclass
class Row:
    cluster_id: str
    published_at: datetime
    headline: str
    url: str
    source: str
    entities: Dict[str, List[str]]
    sentiment: float
    authority: float
    brand_fit: float
    freshness: float
    novelty: float
    engagement: float
    social_velocity: float
    total: float
    decision: str

def fingerprint(title: str, url: str) -> str:
    canon = f"{canonical_url(url)}|{title[:160]}"
    return hashlib.md5(canon.encode()).hexdigest()

def novelty_against_recent(tokens: set, memory: List[set]) -> float:
    def jac(a: set, b: set):
        u = len(a | b)
        return 0.0 if u == 0 else len(a & b)/u
    sim = max([jac(tokens, rh) for rh in memory], default=0.0)
    return 1 - sim

def compute_score_row(headline: str, url: str, published_at: datetime,
                      sent: float, entities: Dict[str, List[str]],
                      recent_tokens: List[set],
                      tau_hours: float,
                      post_cutoff: float,
                      watch_cutoff: float) -> Row:
    age_h = max(0.0, (now_utc() - published_at).total_seconds()/3600.0)
    f = freshness_from_age(age_h, tau_hours)
    a = domain_weight(url)
    sv = 0.0  # sem Twitter histórico
    eng = 0.0
    sent_comp = 1 - abs(sent)
    bf = brand_fit_score(headline, entities)
    tokens = set(re.findall(r"[a-z0-9$\.]{2,}", headline.lower()))
    nov = novelty_against_recent(tokens, recent_tokens)
    base = 100 * (0.20*f + 0.18*a + 0.00*sv + 0.08*eng + 0.22*bf + 0.15*nov + 0.17*sent_comp)

    # penalidade de ruído
    pen = noise_penalty(headline)
    total = base * (1.0 - 0.4*pen)

    decision = "POST" if total >= post_cutoff else ("WATCH" if total >= watch_cutoff else "DROP")
    return Row(
        cluster_id=fingerprint(headline, url),
        published_at=published_at,
        headline=headline,
        url=url,
        source=domain_from_url(url),
        entities=entities,
        sentiment=sent_comp,
        authority=a,
        brand_fit=bf,
        freshness=f,
        novelty=nov,
        engagement=eng,
        social_velocity=sv,
        total=total,
        decision=decision
    )

# =========================
# Coleta: GDELT (principal)
# =========================
GDELT_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"

def gdelt_fetch(start: datetime, end: datetime, query: Optional[str], maxrecords: int = 250) -> List[Dict[str, Any]]:
    """
    Busca artigos na janela [start, end] (UTC). Retorna lista com metadados.
    """
    params = {
        "format": "json",
        "maxrecords": str(maxrecords),
        "sort": "DateDesc",
        "startdatetime": start.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end.strftime("%Y%m%d%H%M%S")
    }
    if query:
        params["query"] = query
    try:
        r = requests.get(GDELT_ENDPOINT, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("articles", []) or []
    except Exception:
        return []

def build_query(domains: List[str], languages: List[str], free_text: Optional[str]) -> str:
    parts = []
    if domains:
        doms = [d.strip() for d in domains if d.strip()]
        if doms:
            parts.append(" OR ".join([f'domain:{d}' for d in doms]))
    if languages:
        # troque 'lang:' por 'sourcelang:' e aceite nomes
        langs = " OR ".join([f'sourcelang:{l.strip().capitalize()}' for l in languages if l.strip()])
        parts.append(f"({langs})")
    if free_text:
        parts.append(f"({free_text})")
    return " AND ".join(parts) if parts else ""


# =========================
# Coleta: NewsAPI (opcional)
# =========================
NEWSAPI_URL = "https://newsapi.org/v2/everything"

def newsapi_fetch(start: datetime, end: datetime, domains: List[str], query: Optional[str], api_key: str, page: int = 1, page_size: int = 100):
    params = {
        "from": start.isoformat(timespec="seconds"),
        "to": end.isoformat(timespec="seconds"),
        "language": "pt",
        "sortBy": "publishedAt",
        "page": page,
        "pageSize": page_size,
        "apiKey": api_key
    }
    if domains:
        params["domains"] = ",".join(domains)
    if query:
        params["q"] = query
    try:
        r = requests.get(NEWSAPI_URL, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"articles": []}

# =========================
# Orquestração
# =========================
def main():
    ap = argparse.ArgumentParser(description="Backfill histórico massivo com GDELT (+ opcional NewsAPI) e TOP-K dataset.")
    ap.add_argument("--from", dest="from_date", required=True, help="Data inicial (YYYY-MM-DD).")
    ap.add_argument("--to", dest="to_date", required=True, help="Data final (YYYY-MM-DD).")
    ap.add_argument("--step-minutes", type=int, default=60, help="Janela de varredura (minutos) para GDELT.")
    ap.add_argument("--domains", type=str, default="",
                    help="Lista de domínios (vírgula) para focar (ex.: valor.globo.com,infomoney.com.br,reuters.com).")
    ap.add_argument("--languages", type=str, default="por,eng", help="Códigos de idioma GDELT (ex.: por,eng).")
    ap.add_argument("--query", type=str, default="", help="Texto livre adicional (ex.: (juros OR selic))")
    ap.add_argument("--sleep-ms", type=int, default=400, help="Intervalo (ms) entre chamadas GDELT (evitar rate limit).")
    ap.add_argument("--freshness-tau-days", type=float, default=90.0, help="Tau da função de frescor (histórico).")
    ap.add_argument("--post-cutoff", type=float, default=70.0)
    ap.add_argument("--watch-cutoff", type=float, default=50.0)
    ap.add_argument("--top-k", type=int, default=10000, help="Quantidade de itens finais no dataset.")
    ap.add_argument("--use-newsapi", action="store_true", help="Habilita NewsAPI se NEWSAPI_KEY estiver setada.")
    ap.add_argument("--newsapi-query", type=str, default="", help="Query NewsAPI (se habilitado).")
    args = ap.parse_args()

    ensure_dirs()
    analyzer = SentimentIntensityAnalyzer()

    start_date = datetime.fromisoformat(args.from_date).replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat(args.to_date).replace(tzinfo=timezone.utc)
    step = timedelta(minutes=args.step_minutes)
    tau_h = args.freshness_tau_days * 24.0

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    languages = [l.strip() for l in args.languages.split(",") if l.strip()]
    gdelt_q = build_query(domains, languages, args.query if args.query else None)

    rows: List[Row] = []
    tokens_memory: List[set] = []

    # --------- GDELT sweep ---------
    print(f"[GDELT] Varredura {start_date.isoformat()} → {end_date.isoformat()} | passo={step} | query='{gdelt_q or '*'}'")
    t = start_date
    pbar = tqdm(total=int((end_date - start_date)/step) + 1)
    while t < end_date:
        window_end = min(end_date, t + step)
        arts = gdelt_fetch(t, window_end, gdelt_q, maxrecords=250)
        for a in arts:
            title = (a.get("title") or "").strip()
            url = (a.get("url") or "").strip()
            if not title or not url:
                continue
            # filtro básico por domínio, se foi passado explicitamente
            if domains:
                host = domain_from_url(url)
                if not any(d in host for d in domains):
                    continue

            # published datetime
            dt = parse_dt_any(a.get("seendate") or a.get("publishedDate") or a.get("publishedAt") or "")
            if not dt:
                # fallback: tenta do body if present
                dt = window_end

            entities = extract_entities(title)
            sent = analyzer.polarity_scores(title)["compound"]

            row = compute_score_row(
                headline=title,
                url=url,
                published_at=dt,
                sent=sent,
                entities=entities,
                recent_tokens=tokens_memory,
                tau_hours=tau_h,
                post_cutoff=args.post_cutoff,
                watch_cutoff=args.watch_cutoff
            )
            rows.append(row)
            # memória leve para novelty
            tokens_memory.append(set(re.findall(r"[a-z0-9$\.]{2,}", title.lower())))
            if len(tokens_memory) > 5000:
                tokens_memory = tokens_memory[-5000:]
        pbar.update(1)
        t = window_end
        time.sleep(args.sleep_ms/1000.0)
    pbar.close()

    # --------- NewsAPI opcional ---------
    if args.use_newsapi and os.getenv("NEWSAPI_KEY"):
        key = os.getenv("NEWSAPI_KEY")
        print("[NewsAPI] Coleta adicional…")
        page = 1
        while True:
            resp = newsapi_fetch(start_date, end_date, domains, args.newsapi_query, key, page=page, page_size=100)
            arts = resp.get("articles", []) or []
            if not arts:
                break
            for a in arts:
                title = (a.get("title") or "").strip()
                url = (a.get("url") or "").strip()
                if not title or not url:
                    continue
                dt = parse_dt_any(a.get("publishedAt") or "")
                if not dt:
                    continue
                entities = extract_entities(title)
                sent = analyzer.polarity_scores(title)["compound"]
                row = compute_score_row(
                    headline=title, url=url, published_at=dt, sent=sent, entities=entities,
                    recent_tokens=tokens_memory, tau_hours=tau_h,
                    post_cutoff=args.post_cutoff, watch_cutoff=args.watch_cutoff
                )
                rows.append(row)
                tokens_memory.append(set(re.findall(r"[a-z0-9$\.]{2,}", title.lower())))
                if len(tokens_memory) > 5000:
                    tokens_memory = tokens_memory[-5000:]
            page += 1
            # NewsAPI tem rate-limit também; ajuste se necessário
            time.sleep(0.3)

    if not rows:
        print("⚠️ Nenhuma notícia coletada no intervalo/fonte escolhidos.")
        return

    # --------- Dedup e seleção TOP-K ---------
    print(f"[Coleta] Total bruto: {len(rows)} itens")
    # Dedup por (title+url) fingerprint
    dedup_map: Dict[str, Row] = {}
    for r in rows:
        dedup_map[r.cluster_id] = r  # keep last (scores parecidos, tanto faz)
    items = list(dedup_map.values())
    print(f"[Dedup] Após dedup: {len(items)}")

    # Ordena por score + decisão + freshness + data
    order_map = {"POST": 2, "WATCH": 1, "DROP": 0}
    items.sort(key=lambda x: (
        x.total,
        order_map.get(x.decision, -1),
        x.freshness,
        x.published_at
    ), reverse=True)

    if args.top_k > 0 and len(items) > args.top_k:
        items = items[:args.top_k]
    print(f"[Seleção] Mantidos TOP-K: {len(items)}")

    # --------- Salvar CSVs auxiliares + dataset ---------
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.DataFrame([{
        "cluster_id": r.cluster_id,
        "published_at": r.published_at.isoformat(),
        "headline": r.headline,
        "url": r.url,
        "source": r.source,
        "topics": " ".join(r.entities.get("topics", [])),
        "tickers": " ".join(r.entities.get("tickers", [])),
        "freshness": round(r.freshness, 4),
        "authority": round(r.authority, 4),
        "social_velocity": round(r.social_velocity, 4),
        "engagement": round(r.engagement, 4),
        "sentiment": round(r.sentiment, 4),
        "brand_fit": round(r.brand_fit, 4),
        "novelty": round(r.novelty, 4),
        "total": round(r.total, 2),
        "decision": r.decision
    } for r in items])

    # Auxiliares (mantém como antes)
    df.to_csv(os.path.join(OUT_DIR, "historical_top.csv"), index=False)
    df_dec = df[[
        "cluster_id","freshness","authority","social_velocity",
        "engagement","sentiment","brand_fit","novelty","total","decision"
    ]]
    df_dec.to_csv(os.path.join(OUT_DIR, "decisions.csv"), index=False)

    # ===== Dataset labeling/to_label.csv =====
    # Monta no mesmo esquema que o app espera (campos principais)
    ensure_dirs()
    new_df = pd.DataFrame({
        "uid": df["cluster_id"],
        "source_kind": "news",
        "origin_file": os.path.abspath(os.path.join(OUT_DIR, "historical_top.csv")),
        "cluster_id": df["cluster_id"],
        # published_at no formato "YYYY-MM-DD HH:MM:SS"
        "published_at": df["published_at"].str.replace("T", " ", regex=False).str.slice(0, 19),
        "headline": df["headline"],
        "summary": "",  # sem resumo no GDELT / NewsAPI
        "urls": df["url"],
        "sources": df["source"],
        "topics": df["topics"],
        "tickers": df["tickers"],
        "total": df["total"],
        "decision": df["decision"],
        "freshness": df["freshness"],
        "authority": df["authority"],
        "social_velocity": df["social_velocity"],
        "engagement": df["engagement"],
        "sentiment": df["sentiment"],
        "brand_fit": df["brand_fit"],
        "novelty": df["novelty"],
        "trends_interest": None,
        "trends_velocity": None
    })

    # === Mescla com o dataset existente (sem perder dados) ===
    merged: pd.DataFrame
    if os.path.exists(DATASET_PATH):
        try:
            old_df = pd.read_csv(DATASET_PATH)
        except Exception:
            old_df = pd.DataFrame()

        # Garante mesmas colunas entre old e new (preenche com None quando faltar)
        for col in new_df.columns:
            if col not in old_df.columns:
                old_df[col] = None
        for col in old_df.columns:
            if col not in new_df.columns:
                new_df[col] = None

        merged = pd.concat([old_df[new_df.columns], new_df], ignore_index=True)
    else:
        merged = new_df.copy()

    # Normaliza published_at para data, quando possível
    def _to_dt(x):
        try:
            return pd.to_datetime(x, errors="coerce")
        except Exception:
            return pd.NaT

    if "published_at" in merged.columns:
        merged["_dt"] = merged["published_at"].apply(_to_dt)
    else:
        merged["_dt"] = pd.NaT

    # 1) remove duplicatas exatas por (headline, urls)
    if {"headline", "urls"}.issubset(merged.columns):
        merged = merged.drop_duplicates(subset=["headline", "urls"], keep="last")

    # 2) dedup por uid (mantém o mais recente por published_at)
    if "uid" in merged.columns:
        merged = merged.sort_values(by=["uid", "_dt"], na_position="last").drop_duplicates(subset=["uid"], keep="last")

    # limpa coluna auxiliar
    merged = merged.drop(columns=["_dt"], errors="ignore")

    # Escrita atômica
    tmp_path = DATASET_PATH + ".tmp"
    merged.to_csv(tmp_path, index=False, encoding="utf-8")
    os.replace(tmp_path, DATASET_PATH)

    print(f"✅ Dataset atualizado/mesclado em {DATASET_PATH} (linhas: {len(merged)})")
    print(f"   Auxiliar salvo em {os.path.join(OUT_DIR,'historical_top.csv')}")

if __name__ == "__main__":
    main()
