# label_app.py
# App Streamlit para rotular conteúdos (POST/WATCH/DROP) com dashboard e Gist/local como backend.
# Compatível com datasets gerados por mvp_local.py / mvp_backfill.py (labeling/to_label.csv).
#
# Requisitos: streamlit, pandas, requests, python-dateutil (opcional)
# Execução: streamlit run label_app.py

import os
import io
import json
import time
import hashlib
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional, Tuple

# =========================
# Config / Secrets
# =========================
st.set_page_config(page_title="Rotulagem — Angular", page_icon="✅", layout="wide", initial_sidebar_state="expanded")

APP_TITLE = "Rotulagem de Conteúdos — Angular"
DEFAULT_DATA_PATH = "labeling/to_label.csv"  # arquivo base que você gera
LOCAL_LABELS_PATH = "labeling/labels.csv"    # fallback local

# Secrets / env
APP_PASSWORD = st.secrets.get("APP_PASSWORD", os.environ.get("LABEL_APP_PASSWORD", ""))
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
GIST_ID = st.secrets.get("GIST_ID", os.environ.get("GIST_ID", ""))
GIST_FILENAME = st.secrets.get("GIST_FILENAME", os.environ.get("GIST_FILENAME", "labels.csv"))

# =========================
# Helpers (auth / storage)
# =========================
def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def require_login() -> bool:
    with st.sidebar:
        st.markdown("## 🔐 Acesso")
        if not APP_PASSWORD:
            st.warning("⚠️ Sem senha configurada (APP_PASSWORD). Defina em `st.secrets` ou variável de ambiente.")
            return True  # libera mesmo assim

        pwd = st.text_input("Senha", type="password")
        if "auth_ok" not in st.session_state:
            st.session_state.auth_ok = False

        if st.button("Entrar") or st.session_state.auth_ok:
            if st.session_state.auth_ok or pwd == APP_PASSWORD:
                st.session_state.auth_ok = True
                return True
            else:
                st.error("Senha incorreta.")
                return False
        return False

# ----- Storage: GitHub Gist -----
def gist_get_labels() -> Optional[pd.DataFrame]:
    if not (GITHUB_TOKEN and GIST_ID and GIST_FILENAME):
        return None
    try:
        r = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        files = data.get("files", {})
        if GIST_FILENAME in files and "content" in files[GIST_FILENAME]:
            txt = files[GIST_FILENAME]["content"]
            if txt.strip() == "":
                return pd.DataFrame(columns=["uid","label","timestamp","reviewer","comment","tags"])
            return pd.read_csv(io.StringIO(txt))
        else:
            return pd.DataFrame(columns=["uid","label","timestamp","reviewer","comment","tags"])
    except Exception as e:
        st.sidebar.warning(f"Gist: não consegui ler ({e}). Usando fallback local.")
        return None

def gist_save_labels(df: pd.DataFrame) -> bool:
    if not (GITHUB_TOKEN and GIST_ID and GIST_FILENAME):
        return False
    try:
        csv_text = df.to_csv(index=False)
        payload = {"files": {GIST_FILENAME: {"content": csv_text}}}
        r = requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            data=json.dumps(payload),
            timeout=15
        )
        r.raise_for_status()
        return True
    except Exception as e:
        st.sidebar.warning(f"Gist: não consegui salvar ({e}).")
        return False

# ----- Storage: Local -----
def local_get_labels() -> pd.DataFrame:
    os.makedirs(os.path.dirname(LOCAL_LABELS_PATH), exist_ok=True)
    if os.path.exists(LOCAL_LABELS_PATH):
        try:
            return pd.read_csv(LOCAL_LABELS_PATH)
        except Exception:
            pass
    return pd.DataFrame(columns=["uid","label","timestamp","reviewer","comment","tags"])

def local_save_labels(df: pd.DataFrame) -> bool:
    try:
        os.makedirs(os.path.dirname(LOCAL_LABELS_PATH), exist_ok=True)
        df.to_csv(LOCAL_LABELS_PATH, index=False)
        return True
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar localmente: {e}")
        return False

def load_labels() -> Tuple[pd.DataFrame, str]:
    df = gist_get_labels()
    if df is not None:
        st.sidebar.info("📦 Armazenando no GitHub Gist (persistente).")
        return df, "gist"
    st.sidebar.info("💾 Armazenando localmente (pode ser efêmero na nuvem).")
    return local_get_labels(), "local"

def save_labels(df: pd.DataFrame, backend: str) -> None:
    if backend == "gist":
        ok = gist_save_labels(df)
        if not ok:
            local_save_labels(df)
    else:
        local_save_labels(df)

# ----- Dataset loader -----
@st.cache_data(show_spinner=False)
def read_csv_safely(path_or_buf) -> pd.DataFrame:
    try:
        return pd.read_csv(path_or_buf)
    except Exception:
        try:
            return pd.read_csv(path_or_buf, sep=";")
        except Exception:
            return pd.DataFrame()

def load_base_csv() -> pd.DataFrame:
    st.sidebar.markdown("## 📚 Base de conteúdos")
    src = st.sidebar.radio("Fonte da base:", ["Arquivo do repositório", "Upload manual"], index=0)
    if src == "Upload manual":
        up = st.sidebar.file_uploader("Envie um CSV com colunas mínimas (headline, urls, ...)", type=["csv"])
        if up is not None:
            df = read_csv_safely(up)
            if not df.empty:
                st.sidebar.success(f"Carregado (upload): {len(df)} linhas")
                return df
            st.sidebar.error("Erro ao ler CSV enviado.")
    # fallback: arquivo do repo
    if not os.path.exists(DEFAULT_DATA_PATH):
        st.sidebar.error(f"Não encontrei {DEFAULT_DATA_PATH}. Gere com seu pipeline (mvp_local/backfill).")
        return pd.DataFrame()
    df = read_csv_safely(DEFAULT_DATA_PATH)
    if df.empty:
        st.sidebar.error(f"Erro ao ler {DEFAULT_DATA_PATH}.")
    else:
        st.sidebar.success(f"Carregado (repo): {len(df)} linhas")
    return df

# =========================
# UI Bits
# =========================
def page_header():
    st.markdown(
        """
        <style>
        .big-btn button {font-size:1.05rem; padding:0.6rem 0.4rem; border-radius:12px;}
        .label-pill {display:inline-block; padding:2px 8px; border-radius:999px; font-size:0.85rem; margin-right:6px;}
        .pill-post {background:#e8f7ee; color:#087443; border:1px solid #b8ebcd;}
        .pill-watch{background:#fff7e6; color:#986c09; border:1px solid #ffe0a3;}
        .pill-drop {background:#fde8e8; color:#9b1c1c; border:1px solid #f7b4b4;}
        .meta {color:#666; font-size:0.9rem;}
        .small {font-size:0.9rem;}
        </style>
        """,
        unsafe_allow_html=True
    )

def pretty_label_tag(label: str) -> str:
    if str(label).upper() == "POST":  return '<span class="label-pill pill-post">POSTAR</span>'
    if str(label).upper() == "WATCH": return '<span class="label-pill pill-watch">MONITORAR</span>'
    if str(label).upper() == "DROP":  return '<span class="label-pill pill-drop">NÃO POSTAR</span>'
    return ""

def normalize_uid(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "uid" not in df.columns:
        if "cluster_id" in df.columns:
            df["uid"] = df["cluster_id"].astype(str)
        else:
            df["uid"] = (df.get("headline","").astype(str) + "|" + df.get("urls","").astype(str)).apply(sha1)
    return df

def coerce_dt(s):
    try:
        return pd.to_datetime(s, errors="coerce")
    except Exception:
        return pd.NaT

# =========================
# Pages
# =========================
def page_labeling(df: pd.DataFrame, labels: pd.DataFrame, backend: str):
    page_header()
    st.title("📝 Rotular conteúdos")

    # --- RESET CONTROLADO (precisa acontecer ANTES de criar os widgets)
    if st.session_state.get("reset_fields", False):
        st.session_state["comment_box"] = ""
        st.session_state["tags_box"] = ""
        st.session_state["reset_fields"] = False

    # --- Inicializa estados (uma vez) ANTES dos widgets
    if "comment_box" not in st.session_state:
        st.session_state["comment_box"] = ""
    if "tags_box" not in st.session_state:
        st.session_state["tags_box"] = ""

    df = normalize_uid(df)

    # Merge status
    merged = df.merge(labels[["uid","label","timestamp","reviewer"]], on="uid", how="left")

    # Sidebar filters
    with st.sidebar:
        st.markdown("## 🔎 Filtros")
        search = st.text_input("Buscar (título/temas/URL)")
        only_unlabeled = st.checkbox("Apenas não rotulados", value=True)
        show_labeled = st.checkbox("Mostrar também rotulados", value=False)
        # Data range
        df["_dt"] = merged["published_at"].apply(coerce_dt)
        min_dt, max_dt = (pd.to_datetime("2000-01-01"), pd.to_datetime("today"))
        if df["_dt"].notna().any():
            min_dt, max_dt = df["_dt"].min(), df["_dt"].max()
        date_range = st.date_input(
            "Intervalo de datas",
            value=(
                min_dt.date() if pd.notna(min_dt) else datetime(2000,1,1).date(),
                max_dt.date() if pd.notna(max_dt) else datetime.today().date()
            )
        )
        source_filter = st.multiselect(
            "Fonte", sorted(list({str(x).split(" | ")[0] for x in merged.get("sources", []) if pd.notna(x)}))
        )
        reviewer = st.text_input("Seu nome (será salvo no rótulo):", value="revisor")

    # Apply filters
    pool = merged.copy()
    if search:
        s = search.lower()
        pool = pool[
            pool.get("headline","").astype(str).str.lower().str.contains(s) |
            pool.get("topics","").astype(str).str.lower().str.contains(s) |
            pool.get("urls","").astype(str).str.lower().str.contains(s)
        ]
    if date_range and len(date_range) == 2:
        dt0, dt1 = pd.to_datetime(str(date_range[0])), pd.to_datetime(str(date_range[1])) + pd.Timedelta(days=1)
        pool["_dt"] = pool["published_at"].apply(coerce_dt)
        pool = pool[(pool["_dt"] >= dt0) & (pool["_dt"] < dt1)]
    if source_filter:
        pool = pool[pool.get("sources","").astype(str).str.split(" \| ").str[0].isin(source_filter)]
    if only_unlabeled:
        pool = pool[pool["label"].isna()]
    elif not show_labeled:
        pass  # mostra todos, mas dá prioridade aos não rotulados

    # Counters
    total_base = len(df)
    total_unlabeled = (merged["label"].isna()).sum()
    st.sidebar.write(f"Total na base: **{total_base}**")
    st.sidebar.write(f"Não rotulados: **{total_unlabeled}**")
    st.sidebar.progress(0 if total_base == 0 else (total_base - total_unlabeled)/total_base)

    if len(pool) == 0:
        st.success("Nada para rotular com esses filtros. ✅")
        return

    # Navigation state
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    st.session_state.idx = max(0, min(st.session_state.idx, len(pool)-1))

    def next_item():
        st.session_state.idx = (st.session_state.idx + 1) % max(1, len(pool))

    def prev_item():
        st.session_state.idx = (st.session_state.idx - 1) % max(1, len(pool))

    row = pool.iloc[st.session_state.idx]

    # Content pane
    left, right = st.columns([2.2, 1])
    with left:
        st.markdown(f"### {row.get('headline','(sem título)')}")
        meta_source = (row.get("sources","") or "").split(" | ")[0]
        st.markdown(f'<span class="meta">{row.get("published_at","")} • {meta_source}</span>', unsafe_allow_html=True)

        if row.get("urls"):
            for u in str(row["urls"]).split(" | "):
                st.write(f"🔗 {u}")

        if str(row.get("summary","")).strip():
            st.markdown("**Resumo**")
            st.write(row["summary"])

        # Entities
        st.markdown("**Entidades/Temas**")
        st.write((row.get("tickers") or ""), " | ", (row.get("topics") or ""))

        st.markdown("---")
        st.markdown("**Comentário (opcional)**")
        comment = st.text_area(
            "Por que sim/não? Qual o ângulo?",
            key="comment_box",
            placeholder="Opcional…"
        )
        tags = st.text_input(
            "Etiquetas (opcional, separadas por vírgula)",
            key="tags_box"
        )

        st.markdown("#### Ações")
        c1, c2, c3, c4, c5 = st.columns([1,1,1,1,2])
        def submit_label(label_value: str):
            uid = row["uid"]
            ts = int(time.time())
            rec = {
                "uid": uid,
                "label": label_value.upper(),
                "timestamp": ts,
                "reviewer": reviewer or "revisor",
                "comment": st.session_state.get("comment_box", "") or "",
                "tags": st.session_state.get("tags_box", "") or ""
            }
            # replace if exists
            lab = labels.copy()
            if "uid" in lab.columns:
                lab = lab[lab["uid"] != uid]
            lab = pd.concat([lab, pd.DataFrame([rec])], ignore_index=True)
            save_labels(lab, backend)

            # refresh cache-less variable
            st.session_state.labels_df = lab

            # Limpeza na PRÓXIMA execução + avança item
            st.session_state["reset_fields"] = True
            next_item()

            st.toast("Rótulo salvo!", icon="✅")
            st.rerun()

        with c1:
            if st.button("✅ Postar (1)", use_container_width=True):
                submit_label("POST")
        with c2:
            if st.button("👀 Monitorar (2)", use_container_width=True):
                submit_label("WATCH")
        with c3:
            if st.button("🗑️ Não postar (3)", use_container_width=True):
                submit_label("DROP")
        with c4:
            if st.button("⏭️ Pular (N)", use_container_width=True):
                next_item()
                st.rerun()
        with c5:
            st.write("")
            st.write("")
            st.button("⏮️ Anterior", on_click=prev_item)

        st.caption("Atalhos: **1** = Postar, **2** = Monitorar, **3** = Não postar, **N** = Pular")

        # Keyboard shortcuts
        st.markdown("""
        <script>
        document.addEventListener('keydown', function(e) {
          const btns = window.parent.document.querySelectorAll('button');
          if (e.key === '1') { btns[0]?.click(); }
          if (e.key === '2') { btns[1]?.click(); }
          if (e.key === '3') { btns[2]?.click(); }
          if (e.key.toLowerCase() === 'n') { btns[3]?.click(); }
        });
        </script>
        """, unsafe_allow_html=True)

    with right:
        st.subheader("Sinais")
        # Mostrar números se existirem
        cols = ["total","freshness","authority","social_velocity","engagement","brand_fit","novelty","trends_interest","sentiment"]
        for c in cols:
            if c in pool.columns:
                try:
                    v = round(float(row[c]), 3)
                except Exception:
                    v = row[c]
                st.metric(c, v)
        st.markdown("---")
        # Status do item
        current_label = row.get("label")
        if pd.notna(current_label):
            st.markdown("**Status atual:** " + pretty_label_tag(current_label), unsafe_allow_html=True)
        else:
            st.markdown("**Status atual:** *não rotulado*")

def page_dashboard(df: pd.DataFrame, labels: pd.DataFrame):
    page_header()
    st.title("📊 Dashboard")

    df = normalize_uid(df)
    # Merge
    merged = df.merge(labels, on="uid", how="left", suffixes=("", "_lab"))

    # KPIs
    total = len(df)
    labeled = merged["label"].notna().sum()
    unlabeled = total - labeled
    pct = (labeled/total*100) if total else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de notícias", f"{total:,}".replace(",","."))
    k2.metric("Avaliadas", f"{labeled:,}".replace(",","."))
    k3.metric("Não avaliadas", f"{unlabeled:,}".replace(",","."))
    k4.metric("% concluído", f"{pct:.1f}%")

    st.markdown("---")
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("Timeline (itens/dia)")
        merged["_dt"] = pd.to_datetime(merged["published_at"], errors="coerce").dt.date
        ts = merged.groupby("_dt")["uid"].count().sort_index()
        st.line_chart(ts)

        st.subheader("Top fontes")
        sources = merged.get("sources","").astype(str).str.split(" \| ").str[0]
        top_sources = sources.value_counts().head(15)
        st.bar_chart(top_sources)

    with c2:
        st.subheader("Distribuição de rótulos")
        label_map = {"POST":"Postar","WATCH":"Monitorar","DROP":"Não postar"}
        pie_df = merged["label"].map(label_map).fillna("Sem rótulo").value_counts()
        st.bar_chart(pie_df)

        st.subheader("Qualidade (média dos sinais)")
        signal_cols = ["total","freshness","authority","brand_fit","novelty","sentiment"]
        sig = {}
        for c in signal_cols:
            if c in merged.columns:
                try:
                    sig[c] = pd.to_numeric(merged[c], errors="coerce").mean()
                except Exception:
                    pass
        if sig:
            st.dataframe(pd.DataFrame.from_dict(sig, orient="index", columns=["média"]).round(3))
        else:
            st.caption("Sem colunas de sinais disponíveis.")

    st.markdown("---")
    st.subheader("Últimos rótulos")
    if labels.empty:
        st.info("Nenhum rótulo salvo ainda.")
    else:
        tmp = labels.merge(df, on="uid", how="left")
        tmp["ts"] = pd.to_datetime(tmp["timestamp"], unit="s", errors="coerce")
        tmp = tmp.sort_values("ts", ascending=False)[["ts","reviewer","label","headline","sources","published_at","urls","comment","tags"]].head(30)
        st.dataframe(tmp, use_container_width=True)

def page_settings():
    page_header()
    st.title("⚙️ Configurações")
    st.markdown("""
    **Backends suportados**  
    - GitHub Gist (persistente): defina `GITHUB_TOKEN`, `GIST_ID`, `GIST_FILENAME` e `APP_PASSWORD` em `st.secrets` ou variáveis de ambiente.  
    - Local (fallback): salva em `labeling/labels.csv`. Em servidores na nuvem pode ser efêmero.
    """)
    st.markdown("### Variáveis atuais")
    st.code(json.dumps({
        "DATA_PATH": DEFAULT_DATA_PATH,
        "LOCAL_LABELS_PATH": LOCAL_LABELS_PATH,
        "APP_PASSWORD?": bool(APP_PASSWORD),
        "GITHUB_TOKEN?": bool(GITHUB_TOKEN),
        "GIST_ID": GIST_ID[:6] + "..." if GIST_ID else "",
        "GIST_FILENAME": GIST_FILENAME
    }, indent=2), language="json")

# =========================
# Main
# =========================
def main():
    st.markdown(f"## {APP_TITLE}")

    if not require_login():
        st.stop()

    # Load base + labels
    df = load_base_csv()
    if df.empty:
        st.stop()

    labels_df, backend = load_labels()
    # Keep labels in session to avoid overwriting between interactions
    if "labels_df" not in st.session_state:
        st.session_state.labels_df = labels_df
    else:
        # If backend has newer version (rare), you could reconcile aqui.
        pass

    # Pages
    with st.sidebar:
        st.markdown("## 🧭 Navegação")
        page = st.radio("", ["Rotular", "Dashboard", "Configurações"], index=0)

    if page == "Rotular":
        page_labeling(df, st.session_state.labels_df, backend)
    elif page == "Dashboard":
        page_dashboard(df, st.session_state.labels_df)
    else:
        page_settings()

if __name__ == "__main__":
    main()
