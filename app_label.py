import os
import io
import json
import time
import base64
import hashlib
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# =========================
# Config / Secrets
# =========================
APP_TITLE = "Rotulagem de Conteúdos — Angular"
DEFAULT_DATA_PATH = "labeling/to_label.csv"  # arquivo base que você gera
LOCAL_LABELS_PATH = "labeling/labels.csv"    # fallback local

# Backends de armazenamento:
# 1) GitHub Gist (persistente) — defina em st.secrets:
#    APP_PASSWORD = "sua_senha"
#    GITHUB_TOKEN = "ghp_xxx"
#    GIST_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#    GIST_FILENAME = "labels.csv"
# 2) Local (fallback) — funciona localmente; na nuvem é efêmero

APP_PASSWORD = st.secrets.get("APP_PASSWORD", os.environ.get("LABEL_APP_PASSWORD", ""))

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
GIST_ID = st.secrets.get("GIST_ID", os.environ.get("GIST_ID", ""))
GIST_FILENAME = st.secrets.get("GIST_FILENAME", os.environ.get("GIST_FILENAME", "labels.csv"))

# =========================
# Helpers
# =========================
def require_login():
    st.title(APP_TITLE)
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

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def load_base_csv() -> pd.DataFrame:
    """Carrega a base de conteúdos. Tenta o arquivo padrão do repo; permite upload manual."""
    st.sidebar.subheader("Base de conteúdos")
    src = st.sidebar.radio("Fonte da base:", ["Arquivo do repositório", "Upload manual"], index=0)
    if src == "Upload manual":
        up = st.sidebar.file_uploader("Envie um CSV com colunas mínimas (headline, urls, ...)", type=["csv"])
        if up is not None:
            try:
                df = pd.read_csv(up)
                st.sidebar.success(f"Carregado (upload): {len(df)} linhas")
                return df
            except Exception as e:
                st.sidebar.error(f"Erro ao ler CSV: {e}")
    # fallback: arquivo do repo
    if not os.path.exists(DEFAULT_DATA_PATH):
        st.sidebar.error(f"Não encontrei {DEFAULT_DATA_PATH}. Gere com make_dataset.py.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(DEFAULT_DATA_PATH)
        st.sidebar.success(f"Carregado (repo): {len(df)} linhas")
        return df
    except Exception as e:
        st.sidebar.error(f"Erro ao ler {DEFAULT_DATA_PATH}: {e}")
        return pd.DataFrame()

# ----- GitHub Gist backend -----
def gist_get_labels() -> pd.DataFrame:
    if not (GITHUB_TOKEN and GIST_ID and GIST_FILENAME):
        return None
    try:
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}",
                         headers={"Authorization": f"token {GITHUB_TOKEN}"}, timeout=15)
        r.raise_for_status()
        data = r.json()
        files = data.get("files", {})
        if GIST_FILENAME in files and "content" in files[GIST_FILENAME]:
            txt = files[GIST_FILENAME]["content"]
            if txt.strip() == "":
                return pd.DataFrame(columns=["uid","label","timestamp","reviewer","comment","tags"])
            return pd.read_csv(io.StringIO(txt))
        else:
            # cria vazio
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
        r = requests.patch(f"https://api.github.com/gists/{GIST_ID}",
                           headers={"Authorization": f"token {GITHUB_TOKEN}"},
                           data=json.dumps(payload), timeout=15)
        r.raise_for_status()
        return True
    except Exception as e:
        st.sidebar.warning(f"Gist: não consegui salvar ({e}).")
        return False

# ----- Local backend -----
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

def load_labels() -> pd.DataFrame:
    df = gist_get_labels()
    if df is not None:
        st.sidebar.info("📦 Armazenando no GitHub Gist (persistente).")
        return df
    st.sidebar.info("💾 Armazenando localmente (pode ser efêmero na nuvem).")
    return local_get_labels()

def save_labels(df: pd.DataFrame) -> None:
    ok = gist_save_labels(df)
    if not ok:
        local_save_labels(df)

# =========================
# App
# =========================
def main():
    if not require_login():
        st.stop()

    st.markdown("### Guia de rotulagem")
    st.markdown("""
**POSTAR**: fato verificável e útil à audiência (impacta carteira/planejamento/governança), fonte confiável.  
**MONITORAR**: potencial de pauta (rumor forte, dado precoce ou incompleto).  
**NÃO POSTAR**: policial/local/fofoca, repetido, irrelevante ou fonte fraca.
""")

    # Carrega base
    df = load_base_csv()
    if df.empty:
        st.stop()

    # Normaliza/garante UID
    if "cluster_id" in df.columns:
        df["uid"] = df["cluster_id"].astype(str)
    else:
        # cria uid a partir do conteúdo
        df["uid"] = (df.get("headline","").astype(str) + "|" + df.get("urls","").astype(str)).apply(sha1)

    # Carrega labels existentes
    labels = load_labels()

    # Quem está rotulando?
    with st.sidebar:
        reviewer = st.text_input("Seu nome (será salvo no rótulo):", value="revisor")
        show_labeled = st.checkbox("Mostrar já rotulados", value=False)
        only_unlabeled = st.checkbox("Apenas não rotulados", value=True)

    # Junta para saber o status
    merged = df.merge(labels[["uid","label"]], on="uid", how="left")
    if only_unlabeled:
        pool = merged[merged["label"].isna()].copy()
    else:
        pool = merged.copy()

    st.sidebar.write(f"Total na base: **{len(df)}** | Não rotulados: **{len(merged['label'].isna())}**")

    # Navegação simples
    if "idx" not in st.session_state: st.session_state.idx = 0
    def next_item(): st.session_state.idx = (st.session_state.idx + 1) % max(1, len(pool))
    def prev_item(): st.session_state.idx = (st.session_state.idx - 1) % max(1, len(pool))

    if len(pool) == 0:
        st.success("Nada para rotular agora. ✅")
        if show_labeled and not only_unlabeled and not labels.empty:
            st.dataframe(labels.merge(df, on="uid", how="left").sort_values("timestamp", ascending=False))
        st.stop()

    row = pool.iloc[st.session_state.idx]

    # Layout
    cA, cB = st.columns([2,1])
    with cA:
        st.markdown(f"### {row.get('headline','(sem título)')}")
        st.caption(f"{row.get('published_at','')} • {row.get('sources','')}")
        if row.get("urls"):
            for u in str(row["urls"]).split(" | "):
                st.write(f"🔗 {u}")
        if row.get("summary"):
            st.write(row["summary"])

        # Entidades / temas
        st.write("**Entidades/Temas:**",
                 (row.get("tickers") or ""), " | ", (row.get("topics") or ""))

    with cB:
        st.subheader("Sinais (se houver)")
        for col in ["total","freshness","authority","social_velocity",
                    "engagement","brand_fit","novelty","trends_interest","sentiment"]:
            if col in row:
                try:
                    st.write(f"{col}:", round(float(row[col]), 3))
                except Exception:
                    st.write(f"{col}:", row[col])

    st.divider()
    comment = st.text_area("Comentário (opcional)", key="comment_box", placeholder="Por que sim/não? Qual o ângulo?")
    tags = st.text_input("Etiquetas (opcional, separadas por vírgula)", key="tags_box")

    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,2])
    def submit_label(label_value: str):
        nonlocal labels
        uid = row["uid"]
        ts = int(time.time())
        rec = {"uid": uid, "label": label_value, "timestamp": ts,
               "reviewer": reviewer or "revisor", "comment": comment, "tags": tags}
        # substitui se já existia
        labels = labels[labels["uid"] != uid]
        labels = pd.concat([labels, pd.DataFrame([rec])], ignore_index=True)
        save_labels(labels)
        # limpa inputs
        st.session_state.comment_box = ""
        st.session_state.tags_box = ""
        next_item()

    if c1.button("✅ Postar (1)", use_container_width=True): submit_label("POST")
    if c2.button("👀 Monitorar (2)", use_container_width=True): submit_label("WATCH")
    if c3.button("🗑️ Não postar (3)", use_container_width=True): submit_label("DROP")
    if c4.button("⏭️ Pular (N)", use_container_width=True): next_item()

    # Atalhos de teclado
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
      if (e.key === '1') { window.parent.document.querySelectorAll('button')[0]?.click(); }
      if (e.key === '2') { window.parent.document.querySelectorAll('button')[1]?.click(); }
      if (e.key === '3') { window.parent.document.querySelectorAll('button')[2]?.click(); }
      if (e.key.toLowerCase() === 'n') { window.parent.document.querySelectorAll('button')[3]?.click(); }
    });
    </script>
    """, unsafe_allow_html=True)

    st.divider()
    if show_labeled and not labels.empty:
        st.subheader("Últimos rótulos")
        st.dataframe(labels.merge(df, on="uid", how="left").sort_values("timestamp", ascending=False).head(30))

if __name__ == "__main__":
    main()
