# mvp_local.py
# MVP local: coleta notícias (RSS), cruza com X/Twitter (snscrape) + Google Trends, score e decisão.
# Também gera 3 blocos de conteúdo:
#   1) Atualidade (briefings dos Top N)
#   2) Evergreen (pautas educacionais alinhadas à marca)
#   3) Insights de Dados (IBOV, S&P500, USD/BRL)
#
# Uso:
#   python mvp_local.py --minutes 360 --top 15
#   python mvp_local.py --minutes 360 --top 15 --mock-social
#   python mvp_local.py --minutes 1440 --top 80 --no-brand-fit --post-cutoff 60 --watch-cutoff 45 --evergreen-k 7
#
# Saídas:
#   ./out/clusters.csv, ./out/social_signals.csv, ./out/decisions.csv, ./out/raw.json
#   ./out/briefs_news.csv, ./out/briefs_evergreen.csv, ./out/insights_data.csv

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
import yfinance as yf

# ---------------- Config ----------------
RSS_FEEDS = [
    # BR
    "https://valor.globo.com/rss/",                          # Valor Econômico (geral)
    "https://www.infomoney.com.br/ultimas-noticias/feed/",   # InfoMoney
    "https://g1.globo.com/dynamo/rss2.xml",                  # G1 geral
    "https://feeds.bbci.co.uk/portuguese/rss.xml",           # BBC Brasil
    "https://rss.uol.com.br/feed/noticias.xml",              # UOL Notícias (geral)
    # Global
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",         # WSJ Markets
    "http://feeds.reuters.com/reuters/businessNews",         # Reuters Business
    "https://www.cnbc.com/id/100003114/device/rss/rss.html"  # CNBC Finance
]

# ===== Brand Profile (Angular Partners) =====
BRAND_PROFILE = {
    "planejamento_patrimonial": {
        "weight": 1.0,
        "kw": [
            "planejamento patrimonial", "gestão patrimonial", "proteção patrimonial",
            "governança familiar", "holding familiar", "sucessão", "herança",
            "testamento", "trust", "offshore", "blindagem lícita",
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

DOMAIN_WEIGHTS = {
    "valor": 0.95, "infomoney": 0.90, "reuters": 0.98, "bloomberg": 0.98,
    "wsj": 0.90, "cnbc": 0.88
}

OUT_DIR = "out"

# --------- Regras de exclusão precoce (skip) ----------
SKIP_PATTERNS = [
    r"^vídeos?:", r"^videos?:", r"^\s*jornal\s", r"^\s*bom dia\s", r"^\s*eptv\s",
    r"^\s*jl1\s", r"^\s*df1\s", r"^\s*jl2\s", r"^\s*jornal anhanguera"
]
SKIP_KEYWORDS = [
    "vídeos:", "videos:", "ao vivo", "edição", "1ª edição", "2ª edição", "programa",
    "telejornal", "coletânea", "resumo do dia", "agenda cultural"
]

# --------- Penalidade de ruído ----------
CRIME_KW = [
    "assassinato", "homicídio", "homicidio", "feminicídio", "feminicidio",
    "tiroteio", "execução", "executado", "estupr", "estupro", "latrocínio",
    "latrocinio", "tráfico", "trafico", "facada", "bala perdida",
    "agrediu", "agressão", "agressao", "morto a tiros", "morre após", "corpo é encontrado",
]
ACIDENTE_KW = [
    "acidente", "colisão", "colisao", "capotagem", "batida", "engavetamento",
    "cai de", "queda de", "desabamento", "incêndio", "incendio",
]
TABLOIDE_KW = [
    "celebridade", "fofoca", "viralizou", "influencer", "reality", "bbb",
]
JORNAL_LOCAL_HINTS = [
    "vídeos:", "videos:", "jornal", "edição", "1ª edição", "2ª edição", "bom dia", "eptv", "jl1", "jl2", "df1"
]
LOW_SIGNAL_SECTIONS = {
    "g1.globo.com": ["/acre/", "/al/", "/am/", "/ap/", "/ba/", "/ce/", "/df/", "/es/", "/go/", "/ma/",
                     "/mg/", "/ms/", "/mt/", "/pa/", "/pb/", "/pe/", "/pi/", "/pr/", "/rj/", "/rn/",
                     "/ro/", "/rr/", "/rs/", "/sc/", "/se/", "/sp/"],
    "uol.com.br":   ["/cotidiano/", "/policia/", "/carros/", "/entretenimento/"],
    "folha.uol.com.br": ["/cotidiano/", "/esporte/"],
}

# ---------------- Utils ----------------
def _text_bag(*parts: str) -> str:
    txt = " ".join(p for p in parts if p)
    txt = txt.lower()
    txt = txt.replace("&", "and").replace("’", "'")
    return txt

def brand_fit_score(headline: str, entities: Dict[str, List[str]]) -> float:
    bag = _text_bag(headline, " ".join(entities.get("topics", [])), " ".join(entities.get("tickers", [])))
    score = 0.0
    for _, cfg in BRAND_PROFILE.items():
        w = cfg.get("weight", 0.5)
        if any(kw.lower() in bag for kw in cfg.get("kw", [])):
            score += w
    score = min(1.0, score)
    if any(neg in bag for neg in BRAND_NEGATIVE_KW):
        score *= 0.7
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
    u = re.sub(r"(\?|#).*", "", u)
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
    return 0.6

def hours_since(dt: datetime) -> float:
    return max(0.0, (now_utc() - dt).total_seconds() / 3600.0)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def _any_in(text: str, kws: List[str]) -> bool:
    t = text.lower()
    return any(k in t for k in kws)

def _path_from_url(url: str) -> str:
    m = re.search(r"https?://[^/]+(/.*)$", url)
    return m.group(1) if m else "/"

def noise_penalty(headline: str, source_host: str, url: str) -> float:
    """0..1 (0 = sem ruído; 1 = ruído pesado)"""
    t = headline.lower()
    score = 0.0
    if _any_in(t, CRIME_KW):     score += 0.6
    if _any_in(t, ACIDENTE_KW):  score += 0.4
    if _any_in(t, TABLOIDE_KW):  score += 0.3
    if _any_in(t, JORNAL_LOCAL_HINTS): score += 0.4
    path = _path_from_url(url).lower()
    for dom, sections in LOW_SIGNAL_SECTIONS.items():
        if dom in source_host:
            if any(path.startswith(sec) for sec in sections):
                score += 0.3
                break
    return min(1.0, score)

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
    trends_interest: float
    trends_velocity: float
    sample: List[Dict[str, Any]]
    trends_topics: List[str]

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

            # skip duro por padrão textual
            title_lc = title.lower()
            if any(re.search(pat, title_lc) for pat in SKIP_PATTERNS):
                continue
            if any(k in title_lc for k in SKIP_KEYWORDS):
                continue

            # published
            published = None
            for cand in ["published", "updated", "created"]:
                if getattr(e, cand, None):
                    published = parse_dt(getattr(e, cand))
                    if published: break
            if not published:
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
    re.compile(r"\b([A-Z]{4}\d)\.SA\b"),
    re.compile(r"\$([A-Z]{1,5})\b"),
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
    caps = set(re.findall(r"\b[A-Z]{2,6}\b", text))
    return {"tickers": sorted(tickers), "topics": sorted(topics), "caps": sorted(caps)}

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
    return {"volume": volume, "velocity": velocity, "engagement": engagement,
            "sentiment_mean": sent_mean, "sentiment_var": sent_var, "sample": sample[:10]}

# ---------------- 4b) Sinais: Google Trends ----------------
def _minutes_to_timeframe(minutes_back: int) -> str:
    if minutes_back <= 60: return "now 1-H"
    if minutes_back <= 240: return "now 4-H"
    if minutes_back <= 1440: return "now 1-d"
    if minutes_back <= 4320: return "now 7-d"
    return "today 1-m"

def _pick_trends_keywords(cluster: Cluster) -> List[str]:
    kws: List[str] = []
    for t in cluster.entities.get("tickers", []):
        t = t.replace(".sa", "").replace("$", "").upper()
        if len(t) >= 3: kws.append(t)
    for tp in cluster.entities.get("topics", []):
        if len(kws) >= 3: break
        kws.append(tp)
    if not kws:
        tokens = [w.lower() for w in re.findall(r"[a-zA-Záéíóúâêôãõç$\.]{3,}", cluster.headline)]
        tokens = [t for t in tokens if not t.isdigit()]
        kws = tokens[:2]
    return kws[:3] if kws else ["mercado financeiro"]

def fetch_trends(cluster: Cluster, minutes_back: int) -> Dict[str, Any]:
    try:
        pytrends = TrendReq(hl="pt-BR", tz=-180)  # América/Recife ~ UTC-3
        timeframe = _minutes_to_timeframe(minutes_back)
        kws = _pick_trends_keywords(cluster)
        if not kws:
            return {"interest": 0.0, "velocity": 0.0, "topics": []}
        pytrends.build_payload(kws, timeframe=timeframe, geo="BR")
        df = pytrends.interest_over_time()
        if df is None or df.empty:
            return {"interest": 0.0, "velocity": 0.0, "topics": kws}
        n = len(df)
        cut = max(1, int(n * 0.75))
        recent = df.iloc[cut:n].drop(columns=["isPartial"], errors="ignore") if "isPartial" in df.columns else df.iloc[cut:n]
        base = df.iloc[:cut].drop(columns=["isPartial"], errors="ignore") if "isPartial" in df.columns else df.iloc[:cut]
        if recent.empty or base.empty:
            return {"interest": 0.0, "velocity": 0.0, "topics": kws}
        recent_mean = recent.mean().mean() / 100.0
        base_mean = base.mean().mean() / 100.0
        gain = (recent_mean - base_mean) / (base_mean + 1e-9)
        velocity = clamp(0.5 + math.tanh(gain) * 0.5, 0.0, 1.0)
        return {"interest": float(clamp(recent_mean, 0, 1)), "velocity": float(velocity), "topics": kws}
    except Exception:
        return {"interest": 0.0, "velocity": 0.0, "topics": []}

# ---------------- 4c) Combinar sinais (Twitter + Trends) ----------------
def fuse_signals(cluster: Cluster, minutes_back: int, mock_social: bool=False) -> SocialSignals:
    tw = fetch_social_twitter(cluster, minutes_back, mock=mock_social)
    tr = fetch_trends(cluster, minutes_back)
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

def compute_score(cluster: Cluster, social: SocialSignals, recent_heads: List[set], *,
                  no_brand_fit: bool=False, post_cutoff: float=70.0, watch_cutoff: float=50.0) -> ScoreBreakdown:
    h = hours_since(cluster.published_at)
    f = freshness(h)
    a = domain_weight_from_source(cluster.urls[0] if cluster.urls else "", cluster.headline)
    sv = clamp(social.velocity)
    eng = clamp(social.engagement_rate)
    sent = 1 - abs(social.sentiment_mean)
    # brand-fit
    if no_brand_fit:
        entities = cluster.entities
        bf = 0.8 if (entities.get("topics") or entities.get("tickers")) else 0.3
    else:
        bf = brand_fit_score(cluster.headline, cluster.entities)
    tokens = set(re.findall(r"[a-z0-9$\.]{2,}", cluster.headline.lower()))
    nov = novelty_against_recent(tokens, recent_heads)
    risk_penalty = 0.85

    total = 100 * (0.20*f + 0.15*a + 0.20*sv + 0.10*eng + 0.15*bf + 0.10*nov + 0.10*sent) * risk_penalty

    # penalização de ruído (crime/local/tabloide/seção regional)
    host = domain_from_url(cluster.urls[0] if cluster.urls else "")
    pen = noise_penalty(cluster.headline, host, cluster.urls[0] if cluster.urls else "")
    quality_penalty = 1.0 - 0.4 * pen  # até -40%
    total *= quality_penalty

    decision = "POST" if total >= post_cutoff else ("WATCH" if total >= watch_cutoff else "DROP")
    return ScoreBreakdown(cluster.id, f, a, sv, eng, sent, bf, nov, risk_penalty, total, decision)

# ---------------- 6) Conteúdo (Atualidade / Evergreen / Insights) ----------------
def make_news_briefs(df_scores: pd.DataFrame, df_clusters: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Gera briefings curtos para os TOP N por score (POST/WATCH)."""
    top = df_scores.sort_values("total", ascending=False).head(top_n).merge(df_clusters, on="cluster_id", how="left")
    rows = []
    for _, r in top.iterrows():
        angle = []
        if r["brand_fit"] >= 0.8: angle.append("alto alinhamento com a marca")
        if r["social_velocity"] >= 0.5: angle.append("tendência em redes/trends")
        if r["authority"] >= 0.9: angle.append("fonte de alta autoridade")
        rows.append({
            "published_at": r["published_at"],
            "decision": r["decision"],
            "headline": r["headline"],
            "source": (r["sources"] or "").split(" | ")[0],
            "urls": r["urls"],
            "why_now": "; ".join(angle) or "relevância moderada",
            "hook_suggested": f"Por que isso importa: {r['topics'] or 'impacto potencial na carteira e no planejamento.'}",
            "cta_suggested": "Fale com a Angular para entender impactos no seu plano patrimonial."
        })
    return pd.DataFrame(rows)

EVERGREEN_LIBRARY = [
    ("Planejamento sucessório em 5 passos", "sucessão; herança; governança familiar; testamento; holding"),
    ("Como proteger seu patrimônio em ciclos de alta de juros", "selic; risco; hedge; diversificação; renda fixa"),
    ("Trust e offshore: quando fazem sentido", "trust; offshore; compliance; tributação internacional"),
    ("Governança para famílias empresárias", "conselho; protocolo familiar; sucessão; legado"),
    ("Filantropia estratégica e endowments", "impacto; esg; doações; fundos patrimoniais"),
]

def make_evergreen_suggestions(trends_hot: List[str], k: int = 5) -> pd.DataFrame:
    """Sugere K pautas evergreen, priorizando BRAND_PROFILE + termos que apareceram no Trends recente."""
    # palavras da marca (achatadas)
    brand_words = set()
    for cfg in BRAND_PROFILE.values():
        for kw in cfg.get("kw", []):
            brand_words.add(kw.lower())

    def score_row(title: str, tags: str) -> float:
        tbag = (title + " " + tags).lower()
        s = 0.0
        if any(w in tbag for w in brand_words): s += 1.0
        if any((th or "").lower() in tbag for th in trends_hot): s += 0.5
        return s

    scored = []
    for title, tags in EVERGREEN_LIBRARY:
        scored.append((score_row(title, tags), title, tags))
    scored.sort(reverse=True)
    picks = scored[:k]
    return pd.DataFrame([{"title": t, "tags": tg, "why": "alinhado à marca e/ou tendências recentes"} for _, t, tg in picks])

DEFAULT_TICKERS = {
    "IBOV": "^BVSP",        # Ibovespa
    "S&P500": "^GSPC",
    "USD/BRL": "BRL=X",
}

def fetch_series(ticker: str, days: int = 30) -> pd.Series:
    df = yf.download(ticker, period=f"{days}d", interval="1d", progress=False)
    if df is None or df.empty: return pd.Series(dtype=float)
    return df["Close"]

def summarize_series(name: str, ticker: str) -> Dict[str, Any]:
    s = fetch_series(ticker, days=35)
    if s.empty:
        return {"name": name, "ticker": ticker, "last": None, "d1": None, "mtd": None, "d30": None}
    s = s.dropna()
    last = float(s.iloc[-1])
    prev = float(s.iloc[-2]) if len(s) > 1 else last
    d1 = (last/prev - 1.0) * 100.0
    # MTD: do primeiro pregão do mês até agora (~p/ séries diárias)
    today = s.index[-1]
    month_mask = (s.index.month == today.month) & (s.index.year == today.year)
    sm = s[month_mask]
    mtd = (last / float(sm.iloc[0]) - 1.0)*100.0 if len(sm) > 0 else None
    # ~21 pregões
    s21 = s.iloc[-21:] if len(s) >= 21 else s
    d21 = (last / float(s21.iloc[0]) - 1.0)*100.0 if len(s21) > 0 else None
    return {"name": name, "ticker": ticker, "last": round(last, 2),
            "d1_%": round(d1, 2),
            "mtd_%": round(mtd, 2) if mtd is not None else None,
            "aprox_21d_%": round(d21, 2) if d21 is not None else None}

def make_data_insights(extra_tickers: Dict[str, str] = None) -> pd.DataFrame:
    tk = dict(DEFAULT_TICKERS)
    if extra_tickers: tk.update(extra_tickers)
    rows = [summarize_series(n, t) for n, t in tk.items()]
    return pd.DataFrame(rows)

# ---------------- 7) Orquestração / CLI ----------------
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
    ap.add_argument("--no-brand-fit", action="store_true", help="Ignora perfil de marca no brand_fit (modo geral)")
    ap.add_argument("--post-cutoff", type=float, default=70.0, help="Corte para decisão POST")
    ap.add_argument("--watch-cutoff", type=float, default=50.0, help="Corte para decisão WATCH")
    ap.add_argument("--evergreen-k", type=int, default=5, help="Qtd de pautas evergreen sugeridas")
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
        sb = compute_score(c, s, recent_heads,
                           no_brand_fit=args.no_brand_fit,
                           post_cutoff=args.post_cutoff,
                           watch_cutoff=args.watch_cutoff)
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

    # Debug opcional com penalidade de ruído
    print("\n[DEBUG] Fatores (Top 10) com penalidade de ruído:")
    dbg = df_scores.head(10).merge(df_clusters, on="cluster_id", how="left")
    def _pen_for_row(r):
        first_url = (r["urls"] or "").split(" | ")[0]
        return noise_penalty(r["headline"], domain_from_url(first_url), first_url)
    dbg["noise_pen"] = dbg.apply(_pen_for_row, axis=1)
    print(dbg[["total","decision","brand_fit","social_velocity","engagement","noise_pen","headline"]]
          .to_string(index=False, max_colwidth=70))

    # ======== Bloco 1: Atualidade (briefings) ========
    briefs = make_news_briefs(df_scores, df_clusters, top_n=args.top)
    briefs_path = os.path.join(OUT_DIR, "briefs_news.csv")
    briefs.to_csv(briefs_path, index=False)
    print(f"\n[Conteúdo/Atualidade] Briefings salvos em: {briefs_path}")

    # ======== Bloco 2: Evergreen (educação/autoridade) ========
    trends_hot = []
    try:
        for s in socials:
            for t in (s.trends_topics or []):
                if isinstance(t, str):
                    trends_hot.append(t.lower())
        trends_hot = list({t for t in trends_hot if t})
    except Exception:
        trends_hot = []
    evergreen = make_evergreen_suggestions(trends_hot, k=args.evergreen_k)
    evergreen_path = os.path.join(OUT_DIR, "briefs_evergreen.csv")
    evergreen.to_csv(evergreen_path, index=False)
    print(f"[Conteúdo/Evergreen] Sugestões salvas em: {evergreen_path}")

    # ======== Bloco 3: Insights de Dados (mercado) ========
    insights = make_data_insights()
    insights_path = os.path.join(OUT_DIR, "insights_data.csv")
    insights.to_csv(insights_path, index=False)
    print(f"[Conteúdo/Insights] Resumo de mercado salvo em: {insights_path}")

    print("\nArquivos gerados em ./out:")
    print(" - clusters.csv            (manchetes, fontes, entidades)")
    print(" - social_signals.csv      (Twitter + Trends: volume, velocity_fused, sentimento, interesse/aceleração)")
    print(" - decisions.csv           (score breakdown e decisão)")
    print(" - raw.json                (dump completo para debug)")
    print(" - briefs_news.csv         (briefings de atualidade prontos p/ post)")
    print(" - briefs_evergreen.csv    (pautas educacionais sugeridas)")
    print(" - insights_data.csv       (snapshot IBOV / S&P500 / USD-BRL)")
    print("\nDicas:")
    print(" • Trends usa timeframe automático baseado em --minutes (ex.: now 4-H).")
    print(" • GEO do Trends está 'BR' — mude em fetch_trends() se quiser global.")
    print(" • Para testar sem X/Twitter: use --mock-social.")
    print(" • Use --no-brand-fit para modo geral; ajuste --post-cutoff/--watch-cutoff para calibrar agressividade.")

if __name__ == "__main__":
    main()
