# make_dataset.py
# Gera um dataset unificado para rotulagem a partir de múltiplas execuções do mvp_local.py (out/)
# e de conteúdos extras (planilhas históricas, newsletters, posts, etc.).
#
# Saída: labeling/to_label.csv

import os
import re
import glob
import argparse
import hashlib
import warnings
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
from tqdm import tqdm

warnings.filterwarnings("ignore", category=UserWarning)

OUTPUT_PATH = "labeling/to_label.csv"
REQUIRED_DIRS = ["labeling"]

# ---- Colunas finais do dataset (ordem amigável para o app) ----
FINAL_COLS = [
    "uid", "source_kind", "origin_file",
    "cluster_id", "published_at", "headline", "summary", "urls", "sources",
    "topics", "tickers",
    # sinais e scores (quando vierem do MVP)
    "total", "decision",
    "freshness", "authority", "social_velocity", "engagement",
    "sentiment", "brand_fit", "novelty",
    "trends_interest", "trends_velocity",
]

# ---- Detectores de CSV "extra" (vários formatos) ----
EXTRA_SCHEMA_CANDIDATES = [
    # (descrição, mapeamento de colunas => padrão final)
    {
        "name": "newsletter_1",
        "map": {
            "title": "headline",
            "link": "urls",
            "date": "published_at",
            "source": "sources",
            "summary": "summary",
            "tags": "topics",
        }
    },
    {
        "name": "social_posts",
        "map": {
            "text": "headline",
            "url": "urls",
            "created_at": "published_at",
            "platform": "sources",
            "tags": "topics",
        }
    },
    {
        "name": "generic_news",
        "map": {
            "headline": "headline",
            "url": "urls",
            "published_at": "published_at",
            "source": "sources",
            "summary": "summary",
            "topics": "topics",
            "tickers": "tickers",
        }
    },
    # fallback mínimo (headline + url)
    {
        "name": "minimal",
        "map": {
            "headline": "headline",
            "url": "urls",
        }
    }
]

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def normalize_date(x: Any) -> Optional[str]:
    """Converte para ISO8601 (string) ou None."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    try:
        # tenta vários formatos
        ts = pd.to_datetime(x, utc=False, errors="coerce")
        if pd.isna(ts):
            return None
        # mantém sem timezone; app só exibe
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def read_csv_safely(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        try:
            return pd.read_csv(path, sep=";")
        except Exception:
            return pd.DataFrame()

def find_out_dirs(scan_root: str) -> List[str]:
    """
    Procura subpastas chamadas 'out' que tenham pelo menos 'clusters.csv'.
    Ex.: ./rodada_2025-09-20/out/, ./out/, ./historico/run1/out/
    """
    candidates = []
    pattern = os.path.join(scan_root, "**", "out")
    for d in glob.glob(pattern, recursive=True):
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "clusters.csv")):
            candidates.append(os.path.abspath(d))
    # inclui raiz/out se existir
    root_out = os.path.join(os.path.abspath(scan_root), "out")
    if os.path.exists(os.path.join(root_out, "clusters.csv")) and root_out not in candidates:
        candidates.append(root_out)
    return sorted(set(candidates))

def load_one_mvp_run(out_dir: str) -> pd.DataFrame:
    """
    Carrega e faz join de clusters.csv + decisions.csv + social_signals.csv de uma única execução do MVP.
    Retorna dataframe já parcialmente normalizado.
    """
    p_clusters = os.path.join(out_dir, "clusters.csv")
    p_decisions = os.path.join(out_dir, "decisions.csv")
    p_social = os.path.join(out_dir, "social_signals.csv")

    if not os.path.exists(p_clusters):
        return pd.DataFrame()

    dfc = read_csv_safely(p_clusters)
    dfd = read_csv_safely(p_decisions) if os.path.exists(p_decisions) else pd.DataFrame()
    dfs = read_csv_safely(p_social) if os.path.exists(p_social) else pd.DataFrame()

    # renomear algumas colunas conhecidas (robustez)
    ren_dfd = {
        "social_velocity": "social_velocity",
        "engagement": "engagement",
        "sentiment": "sentiment",
        "brand_fit": "brand_fit",
        "novelty": "novelty",
        "authority": "authority",
        "freshness": "freshness",
        "total": "total",
        "decision": "decision",
        "cluster_id": "cluster_id",
    }
    dfd = dfd.rename(columns=ren_dfd)

    # social_signals às vezes tem nomes ligeiramente diferentes
    ren_dfs = {
        "velocity_fused": "social_velocity",
        "engagement_twitter": "engagement",
        "trends_interest": "trends_interest",
        "trends_velocity": "trends_velocity",
    }
    dfs = dfs.rename(columns=ren_dfs)

    # join por cluster_id
    df = dfc.copy()
    if not dfd.empty:
        df = df.merge(dfd[["cluster_id","freshness","authority","social_velocity","engagement",
                           "sentiment","brand_fit","novelty","risk_penalty","total","decision"]],
                      on="cluster_id", how="left")
    if not dfs.empty:
        # mantém só as colunas que existem
        keep_cols = [c for c in ["cluster_id","social_velocity","engagement","trends_interest","trends_velocity"] if c in dfs.columns]
        if keep_cols:
            df = df.merge(dfs[keep_cols], on="cluster_id", how="left", suffixes=("", "_soc"))

    # normaliza tipos e campos base
    df["origin_file"] = os.path.abspath(out_dir)
    df["source_kind"] = "news"
    df["published_at"] = df["published_at"].apply(normalize_date)
    # summary pode não existir no clusters.csv; mantém vazio
    if "summary" not in df.columns:
        df["summary"] = ""

    # reduz para o conjunto padrão (o restante fica como NA)
    for col in FINAL_COLS:
        if col not in df.columns:
            df[col] = None

    return df[FINAL_COLS].copy()

def load_all_mvp_runs(out_dirs: List[str]) -> pd.DataFrame:
    frames = []
    for d in tqdm(out_dirs, desc="Lendo execuções do MVP"):
        df = load_one_mvp_run(d)
        if not df.empty:
            frames.append(df)
    if frames:
        big = pd.concat(frames, ignore_index=True)
    else:
        big = pd.DataFrame(columns=FINAL_COLS)

    # cria uid robusto (headline + first_url)
    def first_url(s: str) -> str:
        if not isinstance(s, str): return ""
        return s.split(" | ")[0].strip()
    big["urls"] = big["urls"].fillna("")
    big["headline"] = big["headline"].fillna("")
    big["uid"] = (big["headline"].astype(str) + "|" + big["urls"].apply(first_url)).apply(sha1)

    return big

def sniff_schema_and_map(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Tenta mapear um CSV "extra" para o esquema padrão. Retorna dataframe mapeado ou None.
    """
    cols = set(c.lower() for c in df.columns)
    for cand in EXTRA_SCHEMA_CANDIDATES:
        src_map = cand["map"]
        if all(src in cols for src in src_map.keys() if src not in ["tags"]):  # tags pode faltar
            # cria novo dataframe com nomes padrão
            nd = pd.DataFrame()
            for src, dst in src_map.items():
                # encontra coluna original independentemente de caixa
                matches = [c for c in df.columns if c.lower() == src]
                if matches:
                    nd[dst] = df[matches[0]]
                else:
                    nd[dst] = None
            return nd
    return None

def load_extras(extra_dir: str) -> pd.DataFrame:
    """
    Lê todos os CSVs sob extra_dir/ e tenta mapear para o padrão. Marca como source_kind='other'.
    """
    if not extra_dir or not os.path.isdir(extra_dir):
        return pd.DataFrame(columns=FINAL_COLS)

    csvs = glob.glob(os.path.join(extra_dir, "**", "*.csv"), recursive=True)
    frames = []
    for path in tqdm(csvs, desc="Lendo extras"):
        raw = read_csv_safely(path)
        if raw.empty:
            continue
        mapped = sniff_schema_and_map(raw)
        if mapped is None:
            # tentativa best-effort
            mapped = pd.DataFrame()
            mapped["headline"] = raw.get("headline", raw.get("title", raw.get("text", "")))
            mapped["urls"] = raw.get("urls", raw.get("url", ""))
            mapped["published_at"] = raw.get("published_at", raw.get("date",""))
            mapped["sources"] = raw.get("sources", raw.get("source",""))
            mapped["summary"] = raw.get("summary", "")
            mapped["topics"] = raw.get("topics", raw.get("tags", ""))
            mapped["tickers"] = raw.get("tickers", "")

        # normalizações
        mapped["published_at"] = mapped["published_at"].apply(normalize_date)
        mapped["origin_file"] = os.path.abspath(path)
        mapped["source_kind"] = "other"

        # adiciona colunas ausentes
        for col in FINAL_COLS:
            if col not in mapped.columns:
                mapped[col] = None

        frames.append(mapped[FINAL_COLS].copy())

    if frames:
        big = pd.concat(frames, ignore_index=True)
    else:
        big = pd.DataFrame(columns=FINAL_COLS)

    # uid
    big["urls"] = big["urls"].fillna("")
    big["headline"] = big["headline"].fillna("")
    big["uid"] = (big["headline"].astype(str) + "|" + big["urls"].astype(str)).apply(sha1)
    return big

def drop_already_labeled(df: pd.DataFrame, labels_path: Optional[str]) -> pd.DataFrame:
    if not labels_path or not os.path.exists(labels_path):
        return df
    try:
        lab = pd.read_csv(labels_path)
        if "uid" not in lab.columns:
            return df
        before = len(df)
        df = df[~df["uid"].isin(lab["uid"].astype(str))]
        removed = before - len(df)
        print(f"Removidos {removed} itens já rotulados (baseada em {labels_path}).")
        return df
    except Exception:
        return df

def sample_balance(df: pd.DataFrame, max_rows: int) -> pd.DataFrame:
    """
    Amostra até max_rows mantendo diversidade temporal e de origem.
    Estratégia:
      - prioridade para 'news'
      - mantém mistura por mês e source_kind
    """
    if max_rows <= 0 or len(df) <= max_rows:
        return df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    # bucket por ano-mês
    df["_ym"] = pd.to_datetime(df["published_at"], errors="coerce").dt.strftime("%Y-%m")
    df["_ym"] = df["_ym"].fillna("unknown")
    # cota por (source_kind, ym)
    buckets = []
    per_bucket = max(50, max_rows // 40)  # heurística: até 40 buckets
    for (kind, ym), g in df.groupby(["source_kind", "_ym"]):
        g = g.sample(n=min(len(g), per_bucket), random_state=42)
        buckets.append(g)
    mixed = pd.concat(buckets, ignore_index=True).drop_duplicates("uid")
    if len(mixed) > max_rows:
        mixed = mixed.sample(n=max_rows, random_state=42)
    mixed = mixed.drop(columns=["_ym"], errors="ignore")
    return mixed.sample(frac=1.0, random_state=123).reset_index(drop=True)

def ensure_dirs():
    for d in REQUIRED_DIRS:
        os.makedirs(d, exist_ok=True)

def main():
    ap = argparse.ArgumentParser(description="Gera labeling/to_label.csv unificando saídas do MVP e CSVs extras.")
    ap.add_argument("--scan-root", default=".", help="Raiz para procurar subpastas com 'out/'.")
    ap.add_argument("--extra-dir", default=None, help="Diretório com CSVs extras (posts, newsletters, etc.).")
    ap.add_argument("--exclude-labeled", default=None, help="CSV com labels existentes (para excluir do dataset).")
    ap.add_argument("--max-rows", type=int, default=50000, help="Limite de linhas na saída (amostragem balanceada).")
    args = ap.parse_args()

    ensure_dirs()

    # 1) Carrega todas execuções do MVP encontradas
    out_dirs = find_out_dirs(args.scan_root)
    if not out_dirs:
        print("⚠️ Nenhuma pasta 'out' encontrada. Rode o mvp_local.py antes, ou aponte --scan-root corretamente.")
    df_mvp = load_all_mvp_runs(out_dirs)
    print(f"[MVP] Itens carregados: {len(df_mvp)}")

    # 2) Carrega extras
    df_extra = load_extras(args.extra_dir) if args.extra_dir else pd.DataFrame(columns=FINAL_COLS)
    print(f"[EXTRAS] Itens carregados: {len(df_extra)}")

    # 3) Unifica
    base = pd.concat([df_mvp, df_extra], ignore_index=True)
    if base.empty:
        print("⚠️ Base vazia. Nada a salvar.")
        return

    # 4) Dedup por UID (headline + url)
    base = base.drop_duplicates("uid")

    # 5) Excluir já rotulados (opcional)
    base = drop_already_labeled(base, args.exclude_labeled)

    # 6) Amostragem balanceada (se passar do limite)
    base = sample_balance(base, args.max_rows)

    # 7) Ordena por data desc (quando houver)
    base["__ts"] = pd.to_datetime(base["published_at"], errors="coerce")
    base = base.sort_values(["__ts","source_kind"], ascending=[False, True]).drop(columns=["__ts"])

    # 8) Garante todas as colunas finais
    for c in FINAL_COLS:
        if c not in base.columns:
            base[c] = None
    base = base[FINAL_COLS + [c for c in base.columns if c not in FINAL_COLS]]  # preserva extras no fim

    # 9) Salva
    base.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"✅ Dataset salvo em {OUTPUT_PATH} (linhas: {len(base)})")
    print("   Colunas-chave:", ", ".join(FINAL_COLS))

if __name__ == "__main__":
    main()
