#!/usr/bin/env python3
"""
Interface Streamlit - Sistema de Automação de Conteúdo
Descrição: Interface web para aprovação e publicação de conteúdo gerado por IA
Autor: Gerador de Conteúdo
Data: 2024
"""

import streamlit as st
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go

# Adicionar o diretório pai ao path para importar as POCs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocs.ai_generation.openai_image_poc import OpenAIImagePOC
from pocs.storage.aws_s3_poc import AWSS3POC
from pocs.metrics.social_metrics_poc import SocialMetricsPOC
from pocs.tiktok_poc import TikTokUploadPOC
from pocs.instagram_poc import InstagramUploadPOC

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Sistema de Automação de Conteúdo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = []
if 'published_posts' not in st.session_state:
    st.session_state.published_posts = []
if 'metrics_data' not in st.session_state:
    st.session_state.metrics_data = []

def initialize_pocs():
    """Inicializar POCs"""
    try:
        # OpenAI Image POC
        openai_poc = OpenAIImagePOC()
        if not openai_poc.setup():
            st.error("Erro ao configurar OpenAI POC")
            return None, None, None, None, None
        
        # AWS S3 POC
        s3_poc = AWSS3POC()
        if not s3_poc.setup():
            st.warning("AWS S3 não configurado - usando armazenamento local")
            s3_poc = None
        
        # Social Metrics POC
        metrics_poc = SocialMetricsPOC()
        if not metrics_poc.setup():
            st.warning("Métricas não configuradas")
            metrics_poc = None
        
        # Social Media POCs
        tiktok_poc = TikTokUploadPOC()
        instagram_poc = InstagramUploadPOC()
        
        return openai_poc, s3_poc, metrics_poc, tiktok_poc, instagram_poc
        
    except Exception as e:
        st.error(f"Erro ao inicializar POCs: {e}")
        return None, None, None, None, None

def generate_content(openai_poc, prompt: str, size: str, quality: str, style: str):
    """Gerar conteúdo usando IA"""
    try:
        with st.spinner("Gerando conteúdo..."):
            result = openai_poc.generate_image(prompt, size, quality, style)
            
            if result["status"] == "success":
                # Salvar imagem localmente
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
                filepath = openai_poc.save_image(
                    result["data"]["image_bytes"], 
                    filename,
                    "generated_images"
                )
                
                if filepath:
                    content_data = {
                        "id": timestamp,
                        "prompt": prompt,
                        "revised_prompt": result["data"].get("revised_prompt", prompt),
                        "size": size,
                        "quality": quality,
                        "style": style,
                        "filepath": filepath,
                        "filename": filename,
                        "created_at": datetime.now().isoformat(),
                        "status": "pending_approval"
                    }
                    
                    st.session_state.generated_content.append(content_data)
                    return content_data
                else:
                    st.error("Erro ao salvar imagem")
                    return None
            else:
                st.error(f"Erro na geração: {result['message']}")
                return None
                
    except Exception as e:
        st.error(f"Erro na geração de conteúdo: {e}")
        return None

def upload_to_storage(s3_poc, filepath: str, filename: str):
    """Upload para armazenamento em nuvem ou local"""
    if s3_poc:
        # Usar S3 se configurado
        try:
            s3_key = f"content/{filename}"
            result = s3_poc.upload_file(filepath, s3_key, "image/png")
            
            if result["status"] == "success":
                return result["data"]["public_url"]
            else:
                st.error(f"Erro no upload S3: {result['message']}")
                return None
                
        except Exception as e:
            st.error(f"Erro no upload S3: {e}")
            return None
    else:
        # Usar armazenamento local
        try:
            # Para redes sociais que precisam de URL pública, 
            # você pode usar ngrok ou outro serviço
            local_url = f"file://{os.path.abspath(filepath)}"
            st.info(f"Arquivo salvo localmente: {filepath}")
            st.info("Para Instagram, você precisará hospedar em um servidor público ou usar ngrok")
            return local_url
        except Exception as e:
            st.error(f"Erro no armazenamento local: {e}")
            return None

def publish_to_social_media(platform: str, content_data: Dict, tiktok_poc, instagram_poc):
    """Publicar em rede social"""
    try:
        if platform == "tiktok" and tiktok_poc:
            # Configurar vídeo para TikTok (você precisaria converter imagem para vídeo)
            result = tiktok_poc.run()
        elif platform == "instagram" and instagram_poc:
            # Configurar para Instagram
            result = instagram_poc.run()
        else:
            return {"status": "error", "message": f"Plataforma {platform} não configurada"}
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    """Função principal da interface"""
    
    # Cabeçalho
    st.markdown('<h1 class="main-header">🚀 Sistema de Automação de Conteúdo</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Menu")
    page = st.sidebar.selectbox(
        "Escolha uma página:",
        ["🏠 Dashboard", "🎨 Gerar Conteúdo", "✅ Aprovar Conteúdo", "📊 Métricas", "⚙️ Configurações"]
    )
    
    # Inicializar POCs
    openai_poc, s3_poc, metrics_poc, tiktok_poc, instagram_poc = initialize_pocs()
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🎨 Gerar Conteúdo":
        show_content_generation(openai_poc, s3_poc)
    elif page == "✅ Aprovar Conteúdo":
        show_content_approval(tiktok_poc, instagram_poc, s3_poc)
    elif page == "📊 Métricas":
        show_metrics_dashboard(metrics_poc)
    elif page == "⚙️ Configurações":
        show_settings()

def show_dashboard():
    """Mostrar dashboard principal"""
    st.header("📊 Dashboard Principal")
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Conteúdo Gerado",
            value=len(st.session_state.generated_content),
            delta=None
        )
    
    with col2:
        approved_count = len([c for c in st.session_state.generated_content if c.get("status") == "approved"])
        st.metric(
            label="Conteúdo Aprovado",
            value=approved_count,
            delta=None
        )
    
    with col3:
        published_count = len(st.session_state.published_posts)
        st.metric(
            label="Posts Publicados",
            value=published_count,
            delta=None
        )
    
    with col4:
        total_views = sum([post.get("views", 0) for post in st.session_state.published_posts])
        st.metric(
            label="Total de Visualizações",
            value=total_views,
            delta=None
        )
    
    # Gráfico de atividade
    if st.session_state.generated_content:
        st.subheader("📈 Atividade Recente")
        
        # Preparar dados para o gráfico
        dates = []
        counts = []
        
        for content in st.session_state.generated_content:
            date = datetime.fromisoformat(content["created_at"]).date()
            if date not in dates:
                dates.append(date)
                counts.append(1)
            else:
                idx = dates.index(date)
                counts[idx] += 1
        
        if dates and counts:
            fig = px.bar(
                x=dates, 
                y=counts,
                title="Conteúdo Gerado por Dia",
                labels={"x": "Data", "y": "Quantidade"}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Conteúdo recente
    st.subheader("🆕 Conteúdo Recente")
    if st.session_state.generated_content:
        recent_content = sorted(
            st.session_state.generated_content, 
            key=lambda x: x["created_at"], 
            reverse=True
        )[:5]
        
        for content in recent_content:
            with st.expander(f"Conteúdo {content['id']} - {content['status']}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if os.path.exists(content["filepath"]):
                        st.image(content["filepath"], width=200)
                
                with col2:
                    st.write(f"**Prompt:** {content['prompt']}")
                    st.write(f"**Status:** {content['status']}")
                    st.write(f"**Criado em:** {content['created_at']}")
    else:
        st.info("Nenhum conteúdo gerado ainda.")

def show_content_generation(openai_poc, s3_poc):
    """Mostrar página de geração de conteúdo"""
    st.header("🎨 Gerar Conteúdo com IA")
    
    if not openai_poc:
        st.error("OpenAI não configurado. Verifique as configurações.")
        return
    
    # Formulário de geração
    with st.form("content_generation_form"):
        st.subheader("📝 Configurações de Geração")
        
        prompt = st.text_area(
            "Prompt para geração:",
            placeholder="Descreva a imagem que você quer gerar...",
            height=100
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            size = st.selectbox(
                "Tamanho:",
                ["1024x1024", "1024x1792", "1792x1024"],
                index=0
            )
        
        with col2:
            quality = st.selectbox(
                "Qualidade:",
                ["standard", "hd"],
                index=0
            )
        
        with col3:
            style = st.selectbox(
                "Estilo:",
                ["vivid", "natural"],
                index=0
            )
        
        submitted = st.form_submit_button("🚀 Gerar Conteúdo")
        
        if submitted and prompt:
            content_data = generate_content(openai_poc, prompt, size, quality, style)
            
            if content_data:
                st.success("Conteúdo gerado com sucesso!")
                
                # Mostrar resultado
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(content_data["filepath"], caption="Imagem Gerada")
                
                with col2:
                    st.write("**Detalhes:**")
                    st.write(f"**Prompt:** {content_data['prompt']}")
                    st.write(f"**Prompt Revisado:** {content_data['revised_prompt']}")
                    st.write(f"**Tamanho:** {content_data['size']}")
                    st.write(f"**Qualidade:** {content_data['quality']}")
                    st.write(f"**Estilo:** {content_data['style']}")
                    st.write(f"**Status:** {content_data['status']}")
                
                # Upload para S3 se configurado
                if s3_poc:
                    with st.spinner("Fazendo upload para armazenamento em nuvem..."):
                        public_url = upload_to_storage(
                            s3_poc, 
                            content_data["filepath"], 
                            content_data["filename"]
                        )
                        if public_url:
                            st.success(f"Upload concluído: {public_url}")
                            content_data["public_url"] = public_url
        elif submitted and not prompt:
            st.error("Por favor, insira um prompt para gerar o conteúdo.")

def show_content_approval(tiktok_poc, instagram_poc, s3_poc):
    """Mostrar página de aprovação de conteúdo"""
    st.header("✅ Aprovar e Publicar Conteúdo")
    
    # Filtrar conteúdo pendente
    pending_content = [c for c in st.session_state.generated_content if c.get("status") == "pending_approval"]
    
    if not pending_content:
        st.info("Nenhum conteúdo pendente de aprovação.")
        return
    
    for content in pending_content:
        with st.expander(f"Conteúdo {content['id']} - Aguardando Aprovação"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if os.path.exists(content["filepath"]):
                    st.image(content["filepath"], width=300)
            
            with col2:
                st.write("**Prompt:**", content["prompt"])
                st.write("**Prompt Revisado:**", content["revised_prompt"])
                st.write("**Criado em:**", content["created_at"])
                
                # Formulário de aprovação
                with st.form(f"approval_form_{content['id']}"):
                    st.subheader("📝 Detalhes da Publicação")
                    
                    # Descrição personalizada
                    custom_description = st.text_area(
                        "Descrição do post:",
                        value=content["revised_prompt"],
                        height=100
                    )
                    
                    # Hashtags
                    hashtags = st.text_input(
                        "Hashtags:",
                        placeholder="#ai #arte #digital"
                    )
                    
                    # Plataformas
                    st.subheader("🌐 Plataformas")
                    col_tiktok, col_instagram, col_linkedin = st.columns(3)
                    
                    with col_tiktok:
                        publish_tiktok = st.checkbox("TikTok", key=f"tiktok_{content['id']}")
                    
                    with col_instagram:
                        publish_instagram = st.checkbox("Instagram", key=f"instagram_{content['id']}")
                    
                    with col_linkedin:
                        publish_linkedin = st.checkbox("LinkedIn", key=f"linkedin_{content['id']}")
                    
                    # Botões de ação
                    col_approve, col_reject = st.columns(2)
                    
                    with col_approve:
                        approve = st.form_submit_button("✅ Aprovar e Publicar", type="primary")
                    
                    with col_reject:
                        reject = st.form_submit_button("❌ Rejeitar")
                    
                    if approve:
                        # Atualizar status
                        content["status"] = "approved"
                        content["custom_description"] = custom_description
                        content["hashtags"] = hashtags
                        content["approved_at"] = datetime.now().isoformat()
                        
                        # Publicar nas plataformas selecionadas
                        published_platforms = []
                        
                        if publish_tiktok:
                            result = publish_to_social_media("tiktok", content, tiktok_poc, instagram_poc)
                            if result["status"] == "success":
                                published_platforms.append("tiktok")
                        
                        if publish_instagram:
                            result = publish_to_social_media("instagram", content, tiktok_poc, instagram_poc)
                            if result["status"] == "success":
                                published_platforms.append("instagram")
                        
                        if publish_linkedin:
                            result = publish_to_social_media("linkedin", content, tiktok_poc, instagram_poc)
                            if result["status"] == "success":
                                published_platforms.append("linkedin")
                        
                        # Adicionar aos posts publicados
                        if published_platforms:
                            post_data = {
                                "content_id": content["id"],
                                "platforms": published_platforms,
                                "published_at": datetime.now().isoformat(),
                                "description": custom_description,
                                "hashtags": hashtags
                            }
                            st.session_state.published_posts.append(post_data)
                            
                            st.success(f"Conteúdo publicado em: {', '.join(published_platforms)}")
                        else:
                            st.warning("Conteúdo aprovado, mas não foi possível publicar em nenhuma plataforma.")
                        
                        st.rerun()
                    
                    if reject:
                        content["status"] = "rejected"
                        content["rejected_at"] = datetime.now().isoformat()
                        st.warning("Conteúdo rejeitado.")
                        st.rerun()

def show_metrics_dashboard(metrics_poc):
    """Mostrar dashboard de métricas"""
    st.header("📊 Dashboard de Métricas")
    
    if not metrics_poc:
        st.warning("Métricas não configuradas. Configure os tokens de acesso nas configurações.")
        return
    
    # Coletar métricas
    if st.button("🔄 Atualizar Métricas"):
        with st.spinner("Coletando métricas..."):
            # Preparar posts para coleta de métricas
            posts_to_analyze = []
            for post in st.session_state.published_posts:
                for platform in post["platforms"]:
                    posts_to_analyze.append({
                        "platform": platform,
                        "post_id": f"example_{platform}_id"  # Você substituiria pelos IDs reais
                    })
            
            if posts_to_analyze:
                result = metrics_poc.collect_all_metrics(posts_to_analyze)
                
                if result["status"] == "success":
                    st.session_state.metrics_data = result["data"]["individual_metrics"]
                    st.success("Métricas atualizadas com sucesso!")
                else:
                    st.error(f"Erro ao coletar métricas: {result['message']}")
            else:
                st.info("Nenhum post publicado para analisar.")
    
    # Mostrar métricas
    if st.session_state.metrics_data:
        st.subheader("📈 Métricas por Post")
        
        for metrics in st.session_state.metrics_data:
            if metrics["status"] == "success":
                data = metrics["data"]
                platform = metrics["platform"].upper()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(f"{platform} - Likes", data.get("likes", 0))
                
                with col2:
                    st.metric(f"{platform} - Comentários", data.get("comments", 0))
                
                with col3:
                    st.metric(f"{platform} - Compartilhamentos", data.get("shares", 0))
                
                with col4:
                    st.metric(f"{platform} - Visualizações", data.get("views", 0))
        
        # Gráfico de performance
        st.subheader("📊 Performance por Plataforma")
        
        platforms = []
        likes = []
        comments = []
        shares = []
        views = []
        
        for metrics in st.session_state.metrics_data:
            if metrics["status"] == "success":
                data = metrics["data"]
                platforms.append(metrics["platform"].upper())
                likes.append(data.get("likes", 0))
                comments.append(data.get("comments", 0))
                shares.append(data.get("shares", 0))
                views.append(data.get("views", 0))
        
        if platforms:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Likes", x=platforms, y=likes))
            fig.add_trace(go.Bar(name="Comentários", x=platforms, y=comments))
            fig.add_trace(go.Bar(name="Compartilhamentos", x=platforms, y=shares))
            fig.add_trace(go.Bar(name="Visualizações", x=platforms, y=views))
            
            fig.update_layout(
                title="Métricas por Plataforma",
                xaxis_title="Plataforma",
                yaxis_title="Quantidade",
                barmode="group"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma métrica disponível. Publique conteúdo e clique em 'Atualizar Métricas'.")

def show_settings():
    """Mostrar página de configurações"""
    st.header("⚙️ Configurações")
    
    st.subheader("🔑 Chaves de API")
    
    # OpenAI
    with st.expander("OpenAI"):
        st.text_input("OPENAI_API_KEY", type="password", help="Chave da API do OpenAI")
        st.info("Necessário para geração de imagens com DALL-E")
    
    # AWS S3
    with st.expander("AWS S3"):
        st.text_input("AWS_ACCESS_KEY_ID", type="password")
        st.text_input("AWS_SECRET_ACCESS_KEY", type="password")
        st.text_input("S3_BUCKET_NAME")
        st.text_input("AWS_REGION", value="us-east-1")
        st.info("Necessário para armazenamento em nuvem")
    
    # TikTok
    with st.expander("TikTok"):
        st.text_input("TIKTOK_ACCESS_TOKEN", type="password")
        st.text_input("TIKTOK_OPEN_ID")
        st.info("Necessário para publicação no TikTok")
    
    # Instagram
    with st.expander("Instagram"):
        st.text_input("INSTAGRAM_ACCESS_TOKEN", type="password")
        st.text_input("INSTAGRAM_ACCOUNT_ID")
        st.info("Necessário para publicação no Instagram")
    
    # LinkedIn
    with st.expander("LinkedIn"):
        st.text_input("LINKEDIN_ACCESS_TOKEN", type="password")
        st.info("Necessário para publicação no LinkedIn")
    
    st.subheader("📁 Armazenamento")
    
    if st.button("🗑️ Limpar Dados da Sessão"):
        st.session_state.generated_content = []
        st.session_state.published_posts = []
        st.session_state.metrics_data = []
        st.success("Dados da sessão limpos!")
    
    st.subheader("ℹ️ Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Conteúdo na Sessão", len(st.session_state.generated_content))
        st.metric("Posts Publicados", len(st.session_state.published_posts))
    
    with col2:
        st.metric("Métricas Coletadas", len(st.session_state.metrics_data))
        st.metric("Versão", "1.0.0")

if __name__ == "__main__":
    main()
