# mvp_local.py
# MVP local: coleta notícias (RSS), cruza com X/Twitter (snscrape) + Google Trends, score e decisão.
# Uso:
#   python mvp_local.py --minutes 360 --top 15
#   python mvp_local.py --minutes 360 --top 15 --mock-social
# Saídas:
#   ./out/clusters.csv, ./out/social_signals.csv, ./out/decisions.csv, ./out/raw.json

import os, re, math, json, hashlib, argparse, subprocess, sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dateutil import parser as dtparser

import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
from pytrends.request import TrendReq

# ---------------- Config ----------------
RSS_FEEDS = [
    # BR
    "https://valor.globo.com/rss/",                          # Valor Econômico (geral)
    "https://www.infomoney.com.br/ultimas-noticias/feed/",   # InfoMoney
    "https://g1.globo.com/dynamo/rss2.xml",                 # G1 geral
    "https://feeds.bbci.co.uk/portuguese/rss.xml",          # BBC Brasil
    "https://rss.uol.com.br/feed/noticias.xml",
    # Global
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",         # WSJ Markets
    "http://feeds.reuters.com/reuters/businessNews",         # Reuters Business
    "https://www.cnbc.com/id/100003114/device/rss/rss.html"  # CNBC Finance
]
BRAND_PROFILE = {
    "planejamento_patrimonial": {
        "weight": 1.0,
        "kw": [
            # pt
            "planejamento patrimonial", "gestão patrimonial", "proteção patrimonial",
            "governança familiar", "holding familiar", "sucessão", "herança",
            "testamento", "trust", "offshore", "blindagem lícita",
            # en
            "estate planning", "wealth planning", "asset protection", "family governance", "trusts"
        ]
    },
    "preservacao_risco": {
        "weight": 0.9,
        "kw": [
            "preservação de patrimônio", "segurança", "estabilidade",
            "diversificação", "alocação", "gestão de risco", "hedge",
            "seguro patrimonial", "volatilidade", "proteção"
        ]
    },
    "sucessao_legado": {
        "weight": 0.9,
        "kw": [
            "planejamento sucessório", "legado", "next-gen", "educação financeira",
            "transição geracional", "family office", "fundos exclusivos", "fip", "fii"
        ]
    },
    "fiscal_estrutural": {
        "weight": 0.75,
        "kw": [
            "tributação", "impostos", "reforma tributária", "itcmd", "ir", "estruturação",
            "custo fiscal", "eficiência fiscal", "tax planning"
        ]
    },
    "mercado_relevante": {
        "weight": 0.65,
        "kw": [
            # macro/mercado com impacto nos clientes HNWI
            "selic", "copom", "ipca", "juros", "inflação", "câmbio", "dólar",
            "fed", "ecb", "treasury", "s&p 500", "nasdaq", "volatilidade",
            "recessão", "crescimento", "guidance", "resultado", "dividendos"
        ]
    },
    "impacto_filantropia_sustentavel": {
        "weight": 0.6,
        "kw": [
            "filantropia", "impacto social", "investimento sustentável",
            "esg", "projetos sociais", "fundos filantrópicos", "endowment"
        ]
    },
}

# Palavras/assuntos a penalizar (não conversam com o posicionamento/tom)
BRAND_NEGATIVE_KW = [
    "fofoca", "celebridade", "escândalo", "polêmica vazia", "crime bárbaro",
    "clickbait", "tabloide", "viral inútil"
]
# BRAND_WHITELIST = set()

DOMAIN_WEIGHTS = {
    "valor": 0.95, "infomoney": 0.90, "reuters": 0.98, "bloomberg": 0.98,
    "wsj": 0.90, "cnbc": 0.88
}

OUT_DIR = "out"

# ---------------- Utils ----------------

def _text_bag(*parts: str) -> str:
    txt = " ".join(p for p in parts if p)
    # normaliza acentuação leve (simples) e caixa
    txt = txt.lower()
    # variantes simples de símbolos
    txt = txt.replace("&", "and").replace("’", "'")
    return txt

def brand_fit_score(headline: str, entities: Dict[str, List[str]]) -> float:
    """
    Retorna score 0..1 com base no BRAND_PROFILE.
    Soma ponderada (cap 1.0), + penalização se bater palavras negativas.
    """
    bag = _text_bag(headline, " ".join(entities.get("topics", [])), " ".join(entities.get("tickers", [])))
    score = 0.0
    for cat, cfg in BRAND_PROFILE.items():
        w = cfg.get("weight", 0.5)
        if any(kw.lower() in bag for kw in cfg.get("kw", [])):
            score += w
    # normaliza (cap em 1.0)
    score = min(1.0, score)

    # penalização simples para assuntos desalinhados
    if any(neg in bag for neg in BRAND_NEGATIVE_KW):
        score *= 0.7  # -30%
    return score
def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)

def now_utc():
    return datetime.now(timezone.utc)

def parse_dt(s: str) -> Optional[datetime]:
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
    u = re.sub(r"(\?|#).*", "", u)  # remove query/fragment
    return u.lower().rstrip("/")

def domain_from_url(u: str) -> str:
    m = re.search(r"https?://([^/]+)/", u + "/")
    if not m: return ""
    host = m.group(1).lower()
    host = host.replace("www.", "")
    return host

def domain_weight_from_source(url: str, title: str) -> float:
    host = domain_from_url(url)
    for k, v in DOMAIN_WEIGHTS.items():
        if k in host:
            return v
    # fallback por heurística de reputação mínima
    return 0.6

def hours_since(dt: datetime) -> float:
    return max(0.0, (now_utc() - dt).total_seconds() / 3600.0)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

# ---------------- Data classes ----------------
@dataclass
class Article:
    title: str
    url: str
    source: str
    published_at: datetime
    summary: str

@dataclass
class Cluster:
    id: str
    headline: str
    published_at: datetime
    urls: List[str]
    sources: List[str]
    titles: List[str]
    entities: Dict[str, List[str]]

@dataclass
class SocialSignals:
    cluster_id: str
    volume: int
    engagement_rate: float
    velocity: float
    sentiment_mean: float
    sentiment_var: float
    trends_interest: float          # 0..1 (média recente normalizada)
    trends_velocity: float          # 0..1 (aceleração)
    sample: List[Dict[str, Any]]    # pequenas amostras (X/Twitter)
    trends_topics: List[str]        # palavras consultadas no Trends

@dataclass
class ScoreBreakdown:
    cluster_id: str
    freshness: float
    authority: float
    social_velocity: float
    engagement: float
    sentiment: float
    brand_fit: float
    novelty: float
    risk_penalty: float
    total: float
    decision: str

# ---------------- 1) Ingestão RSS ----------------
def fetch_rss(minutes_back: int) -> List[Article]:
    cutoff = now_utc() - timedelta(minutes=minutes_back)
    arts: List[Article] = []
    for feed in RSS_FEEDS:
        d = feedparser.parse(feed)
        for e in d.entries:
            title = (e.title or "").strip()
            link = (getattr(e, "link", "") or "").strip()
            summary = (getattr(e, "summary", "") or "").strip()
            # published
            published = None
            for cand in ["published", "updated", "created"]:
                if getattr(e, cand, None):
                    published = parse_dt(getattr(e, cand))
                    if published: break
            if not published:
                # fallback: agora
                published = now_utc()
            if published < cutoff:
                continue
            src = domain_from_url(link) or "unknown"
            arts.append(Article(title=title, url=link, source=src, published_at=published, summary=summary))
    return arts

# ---------------- 2) Deduplicação/Clusters ----------------
def fingerprint(article: Article) -> str:
    canon = f"{canonical_url(article.url)}|{article.title[:140]}|{article.source}"
    return hashlib.md5(canon.encode()).hexdigest()

def make_clusters(arts: List[Article]) -> List[Cluster]:
    buckets: Dict[str, List[Article]] = {}
    for a in arts:
        buckets.setdefault(fingerprint(a), []).append(a)
    clusters: List[Cluster] = []
    for fp, group in buckets.items():
        chosen = max(group, key=lambda x: x.published_at)
        clusters.append(Cluster(
            id=fp,
            headline=chosen.title,
            published_at=chosen.published_at,
            urls=[a.url for a in group],
            sources=[a.source for a in group],
            titles=[a.title for a in group],
            entities=extract_entities(" ".join([a.title for a in group]))
        ))
    return clusters

# ---------------- 3) Entidades (regras simples) ----------------
TICKER_PATTERNS = [
    re.compile(r"\b([A-Z]{4}\d)\.SA\b"),      # PETR4.SA, VALE3.SA etc.
    re.compile(r"\$([A-Z]{1,5})\b"),          # $NVDA, $TSLA
]
TOPIC_KEYWORDS = {
    "selic", "ipca", "juros", "inflação", "inflacao", "câmbio", "cambio",
    "dólar", "dolar", "fed", "copom", "cvm", "sec", "balanço", "balanco",
    "guidance", "dividendos", "resultado", "pil", "gdp", "payroll", "petrobras",
    "vale", "itau", "ambev", "magalu", "b3", "ibovespa", "nasdaq", "s&p500", "opec"
}
def extract_entities(text: str) -> Dict[str, List[str]]:
    text_low = text.lower()
    tickers = set()
    for pat in TICKER_PATTERNS:
        for m in pat.findall(text):
            tickers.add(m.lower() if isinstance(m, str) else m[0].lower())
    topics = {w for w in TOPIC_KEYWORDS if w in text_low}
    caps = set(re.findall(r"\b[A-Z]{2,6}\b", text))  # heurística simples
    return {
        "tickers": sorted(tickers),
        "topics": sorted(topics),
        "caps": sorted(caps)
    }

# ---------------- 4) Sinais: Twitter (snscrape) ----------------
def have_cmd(cmd: str) -> bool:
    try:
        subprocess.run([sys.executable, "-m", cmd, "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def build_query(cluster: Cluster, minutes_back: int) -> str:
    tokens = re.findall(r"[a-zA-Z0-9$\.]{3,}", cluster.headline)
    tokens = [t for t in tokens if not t.isdigit()]
    extra = cluster.entities.get("tickers", []) + cluster.entities.get("topics", [])
    q = " ".join(tokens[:6] + extra[:4])
    since = (now_utc() - timedelta(minutes=minutes_back)).date().isoformat()
    return f'{q} lang:pt since:{since}'

def fetch_social_twitter(cluster: Cluster, minutes_back: int, mock: bool=False):
    if mock:
        import random
        return {
            "volume": random.randint(0, 120),
            "velocity": random.uniform(0, 1),
            "engagement": random.uniform(0, 0.5),
            "sentiment_mean": random.uniform(-0.4, 0.4),
            "sentiment_var": 0.1,
            "sample": []
        }

    if not have_cmd("snscrape"):
        print("Aviso: snscrape não encontrado. Use --mock-social ou instale: pip install snscrape")
        return {"volume": 0, "velocity": 0.0, "engagement": 0.0,
                "sentiment_mean": 0.0, "sentiment_var": 0.0, "sample": []}

    query = build_query(cluster, minutes_back)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "snscrape", "--jsonl", "twitter-search", query],
            capture_output=True, text=True, timeout=60
        )
        lines = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
    except Exception:
        lines = []

    analyzer = SentimentIntensityAnalyzer()
    sentiments, timestamps, sample = [], [], []
    for item in lines[:120]:
        content = item.get("content") or ""
        date_str = item.get("date")
        ts = parse_dt(date_str) if date_str else None
        if ts: timestamps.append(ts)
        vs = analyzer.polarity_scores(content)
        sentiments.append(vs["compound"])
        sample.append({
            "date": date_str,
            "user": (item.get("user") or {}).get("username"),
            "likeCount": item.get("likeCount"),
            "retweetCount": item.get("retweetCount"),
            "content": content[:200]
        })

    volume = len(lines)
    if lines:
        engagement = sum([(l.get("likeCount", 0) or 0) + (l.get("retweetCount", 0) or 0) for l in lines]) / (len(lines) * 100.0)
    else:
        engagement = 0.0

    now = now_utc()
    last2 = sum(1 for t in timestamps if (now - t).total_seconds() <= 2*3600)
    last6 = sum(1 for t in timestamps if (now - t).total_seconds() <= 6*3600)
    velocity = 0.0 if last6 == 0 else clamp(last2 / last6, 0, 1)

    if sentiments:
        sent_mean = sum(sentiments)/len(sentiments)
        sent_var = sum((s - sent_mean)**2 for s in sentiments)/len(sentiments)
    else:
        sent_mean, sent_var = 0.0, 0.0

    return {
        "volume": volume,
        "velocity": velocity,
        "engagement": engagement,
        "sentiment_mean": sent_mean,
        "sentiment_var": sent_var,
        "sample": sample[:10]
    }

# ---------------- 4b) Sinais: Google Trends ----------------
def _minutes_to_timeframe(minutes_back: int) -> str:
    # Mapeia janela em minutos para timeframes aceitos pelo Trends
    if minutes_back <= 60:
        return "now 1-H"
    if minutes_back <= 240:
        return "now 4-H"
    if minutes_back <= 1440:
        return "now 1-d"
    if minutes_back <= 4320:
        return "now 7-d"
    return "today 1-m"

def _pick_trends_keywords(cluster: Cluster) -> List[str]:
    # Prioriza tickers (sem sufixo .sa e sem $), depois tópicos; limita 1–3 termos
    kws: List[str] = []
    for t in cluster.entities.get("tickers", []):
        t = t.replace(".sa", "").replace("$", "").upper()
        if len(t) >= 3:
            kws.append(t)
    # tópicos em pt
    for tp in cluster.entities.get("topics", []):
        if len(kws) >= 3: break
        kws.append(tp)
    # fallback com 1-2 tokens não numéricos da manchete
    if not kws:
        tokens = [w.lower() for w in re.findall(r"[a-zA-Záéíóúâêôãõç$\.]{3,}", cluster.headline)]
        tokens = [t for t in tokens if not t.isdigit()]
        kws = tokens[:2]
    # garante pelo menos 1 termo
    return kws[:3] if kws else ["mercado financeiro"]

def fetch_trends(cluster: Cluster, minutes_back: int) -> Dict[str, Any]:
    try:
        pytrends = TrendReq(hl="pt-BR", tz=-180)  # America/Recife ~ UTC-3
        timeframe = _minutes_to_timeframe(minutes_back)
        kws = _pick_trends_keywords(cluster)

        # Sem palavras? retorna zerado
        if not kws:
            return {"interest": 0.0, "velocity": 0.0, "topics": []}

        pytrends.build_payload(kws, timeframe=timeframe, geo="BR")  # global; ajuste para "BR" se quiser
        df = pytrends.interest_over_time()
        if df is None or df.empty:
            return {"interest": 0.0, "velocity": 0.0, "topics": kws}

        # Calcula média recente vs base
        # pega últimos 25% como "recente" e 75% anterior como "base"
        n = len(df)
        cut = max(1, int(n * 0.75))
        recent = df.iloc[cut:n].drop(columns=["isPartial"], errors="ignore") if "isPartial" in df.columns else df.iloc[cut:n]
        base = df.iloc[:cut].drop(columns=["isPartial"], errors="ignore") if "isPartial" in df.columns else df.iloc[:cut]

        if recent.empty or base.empty:
            return {"interest": 0.0, "velocity": 0.0, "topics": kws}

        # interesse: média dos termos (última janela), normalizado 0..1
        recent_mean = recent.mean().mean() / 100.0  # Trends é 0..100
        base_mean = base.mean().mean() / 100.0

        # velocity: aceleração (tanh do ganho relativo) -> 0..1
        gain = (recent_mean - base_mean) / (base_mean + 1e-9)
        velocity = clamp(0.5 + math.tanh(gain) * 0.5, 0.0, 1.0)

        return {"interest": float(clamp(recent_mean, 0, 1)), "velocity": float(velocity), "topics": kws}
    except Exception:
        # Em qualquer erro (quota/instabilidade), retorna zerado
        return {"interest": 0.0, "velocity": 0.0, "topics": []}

# ---------------- 4c) Combinar sinais (Twitter + Trends) ----------------
def fuse_signals(cluster: Cluster, minutes_back: int, mock_social: bool=False) -> SocialSignals:
    tw = fetch_social_twitter(cluster, minutes_back, mock=mock_social)
    tr = fetch_trends(cluster, minutes_back)

    # Combinações simples:
    # - velocity_final: mix Twitter/Trends
    velocity_final = clamp(0.7 * tw["velocity"] + 0.3 * tr["velocity"], 0.0, 1.0)

    return SocialSignals(
        cluster_id=cluster.id,
        volume=int(tw["volume"]),
        engagement_rate=float(tw["engagement"]),
        velocity=float(velocity_final),
        sentiment_mean=float(tw["sentiment_mean"]),
        sentiment_var=float(tw["sentiment_var"]),
        trends_interest=float(tr["interest"]),
        trends_velocity=float(tr["velocity"]),
        sample=tw["sample"],
        trends_topics=tr["topics"]
    )

# ---------------- 5) Scoring ----------------
def freshness(hours: float, tau=6.0) -> float:
    return math.exp(-hours / tau)

def novelty_against_recent(headline_tokens: set, recent_heads: List[set]) -> float:
    def jac(a: set, b: set):
        u = len(a | b)
        return 0.0 if u == 0 else len(a & b)/u
    sim = max([jac(headline_tokens, rh) for rh in recent_heads], default=0.0)
    return 1 - sim

def compute_score(cluster: Cluster, social: SocialSignals, recent_heads: List[set]) -> ScoreBreakdown:
    h = hours_since(cluster.published_at)
    f = freshness(h)
    a = domain_weight_from_source(cluster.urls[0] if cluster.urls else "", cluster.headline)
    sv = clamp(social.velocity)                 # 0-1 (já fundido com Trends)
    eng = clamp(social.engagement_rate)         # ~0-0.5
    sent = 1 - abs(social.sentiment_mean)       # evita extremos
    bf = brand_fit_score(cluster.headline, cluster.entities)
    tokens = set(re.findall(r"[a-z0-9$\.]{2,}", cluster.headline.lower()))
    nov = novelty_against_recent(tokens, recent_heads)
    risk_penalty = 0.85  # ajustável via regras

    total = 100 * (0.20*f + 0.15*a + 0.20*sv + 0.10*eng + 0.15*bf + 0.10*nov + 0.10*sent) * risk_penalty
    decision = "POST" if total >= 70 else ("WATCH" if total >= 50 else "DROP")
    return ScoreBreakdown(cluster.id, f, a, sv, eng, sent, bf, nov, risk_penalty, total, decision)

# ---------------- 6) Orquestração / CLI ----------------
def _json_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, set):
        return list(o)
    return str(o)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=360, help="Janela de coleta de notícias (minutos)")
    ap.add_argument("--top", type=int, default=15, help="Quantos clusters mostrar")
    ap.add_argument("--mock-social", action="store_true", help="Simula sinais sociais (sem snscrape)")
    args = ap.parse_args()

    ensure_out()

    print(f"\n[1/5] Coletando RSS (últimos {args.minutes} min)...")
    arts = fetch_rss(args.minutes)
    print(f"  -> {len(arts)} artigos brutos")

    print("[2/5] Deduplicando por clusters...")
    clusters = make_clusters(arts)
    print(f"  -> {len(clusters)} clusters")

    recent_heads = [set(re.findall(r"[a-z0-9$\.]{2,}", c.headline.lower())) for c in clusters]

    socials: List[SocialSignals] = []
    scores: List[ScoreBreakdown] = []

    print("[3/5] Buscando sinais: X/Twitter + Google Trends...")
    for c in tqdm(clusters):
        sig = fuse_signals(c, args.minutes, mock_social=args.mock_social)
        socials.append(sig)

    print("[4/5] Calculando scores...")
    for c, s in zip(clusters, socials):
        sb = compute_score(c, s, recent_heads)
        scores.append(sb)

    # ------- Saídas (CSV/JSON) -------
    print("[5/5] Salvando saídas em ./out ...")

    # clusters.csv
    df_clusters = pd.DataFrame([{
        "cluster_id": c.id,
        "headline": c.headline,
        "published_at": c.published_at.isoformat(),
        "urls": " | ".join(c.urls),
        "sources": " | ".join(c.sources),
        "tickers": " ".join(c.entities.get("tickers", [])),
        "topics": " ".join(c.entities.get("topics", [])),
    } for c in clusters])
    df_clusters.to_csv(os.path.join(OUT_DIR, "clusters.csv"), index=False)

    # social_signals.csv (inclui Trends)
    df_social = pd.DataFrame([{
        "cluster_id": s.cluster_id,
        "volume_twitter": s.volume,
        "engagement_twitter": round(s.engagement_rate, 4),
        "velocity_fused": round(s.velocity, 4),
        "sentiment_mean": round(s.sentiment_mean, 4),
        "sentiment_var": round(s.sentiment_var, 4),
        "trends_interest": round(s.trends_interest, 4),
        "trends_velocity": round(s.trends_velocity, 4),
        "trends_topics": " | ".join(s.trends_topics or []),
        "sample_users": " | ".join({(x.get('user') or '') for x in s.sample if x.get('user')}),
    } for s in socials])
    df_social.to_csv(os.path.join(OUT_DIR, "social_signals.csv"), index=False)

    # decisions.csv
    df_scores = pd.DataFrame([{
        "cluster_id": sb.cluster_id,
        "freshness": round(sb.freshness, 4),
        "authority": round(sb.authority, 4),
        "social_velocity": round(sb.social_velocity, 4),
        "engagement": round(sb.engagement, 4),
        "sentiment": round(sb.sentiment, 4),
        "brand_fit": round(sb.brand_fit, 4),
        "novelty": round(sb.novelty, 4),
        "risk_penalty": round(sb.risk_penalty, 4),
        "total": round(sb.total, 2),
        "decision": sb.decision
    } for sb in scores]).sort_values("total", ascending=False)
    df_scores.to_csv(os.path.join(OUT_DIR, "decisions.csv"), index=False)

    # raw.json (debug completo)
    raw = {
        "clusters": [asdict(c) for c in clusters],
        "socials": [asdict(s) for s in socials],
        "scores": [asdict(sb) for sb in scores]
    }
    with open(os.path.join(OUT_DIR, "raw.json"), "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2, default=_json_default)

    # Console: Top N
    print("\n==== TOP por score ====")
    top = df_scores.head(args.top).merge(df_clusters, on="cluster_id", how="left")
    top["sources"] = top["sources"].str.split(" | ").str[0]
    top["published_at"] = top["published_at"].str.slice(0, 19).str.replace("T", " ", regex=False)
    print(top[["total","decision","published_at","sources","headline"]].to_string(index=False, max_colwidth=80))

    print("\nArquivos gerados em ./out:")
    print(" - clusters.csv            (manchetes, fontes, entidades)")
    print(" - social_signals.csv      (Twitter + Trends: volume, velocity_fused, sentimento, interesse/aceleração)")
    print(" - decisions.csv           (score breakdown e decisão)")
    print(" - raw.json                (dump completo para debug)")
    print("\nDicas:")
    print(" • Trends usa timeframe automático baseado em --minutes (ex.: now 4-H).")
    print(" • Ajuste GEO do Trends em fetch_trends() para 'BR' se quiser só Brasil.")
    print(" • Para testar sem X/Twitter: use --mock-social (Trends continua ativo).")

if __name__ == "__main__":
    main()
