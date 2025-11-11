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
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger_env = logging.getLogger(__name__)
    logger_env.info(f"Arquivo .env carregado de: {env_path}")
else:
    # Tentar carregar do diretório atual também
    load_dotenv()
    logger_env = logging.getLogger(__name__)
    logger_env.warning(f"Arquivo .env não encontrado em: {env_path}")

# Adicionar o diretório pai ao path para importar as POCs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocs.ai_generation.gemini_image_poc import GeminiImagePOC
from pocs.storage.aws_s3_poc import AWSS3POC
from pocs.metrics.social_metrics_poc import SocialMetricsPOC
from pocs.tiktok_poc import TikTokUploadPOC
from pocs.instagram_poc import InstagramUploadPOC
from pocs.linkedin_poc import LinkedInUploadPOC

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
        # Gemini Image POC
        gemini_poc = GeminiImagePOC()
        if not gemini_poc.setup():
            st.error("Erro ao configurar Gemini POC")
            return None, None, None, None, None, None
        
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
        if not tiktok_poc.setup():
            st.warning("TikTok não configurado - verifique TIKTOK_ACCESS_TOKEN e TIKTOK_OPEN_ID no .env")
            tiktok_poc = None
        
        instagram_poc = InstagramUploadPOC()
        if not instagram_poc.setup():
            st.warning("Instagram não configurado")
            instagram_poc = None
        
        linkedin_poc = LinkedInUploadPOC()
        if not linkedin_poc.setup():
            st.warning("LinkedIn não configurado")
            linkedin_poc = None
        
        return gemini_poc, s3_poc, metrics_poc, tiktok_poc, instagram_poc, linkedin_poc
        
    except Exception as e:
        st.error(f"Erro ao inicializar POCs: {e}")
        return None, None, None, None, None, None

def generate_content(gemini_poc, prompt: str, size: str, quality: str, style: str):
    """Gerar conteúdo usando IA"""
    try:
        # Adicionar variação ao prompt para evitar imagens repetidas
        import random
        import time
        variations = [
            "versão única",
            "perspectiva diferente",
            "estilo único",
            "abordagem criativa",
            "conceito inovador"
        ]
        variation = random.choice(variations)
        timestamp = int(time.time())
        varied_prompt = f"{prompt}, {variation}, timestamp {timestamp}"
        
        with st.spinner("Gerando conteúdo..."):
            result = gemini_poc.generate_image(varied_prompt, size, quality, style)
            
            if result["status"] == "success":
                # Salvar imagem localmente
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
                filepath = gemini_poc.save_image(
                    result["data"]["image_bytes"], 
                    filename,
                    "generated_images"
                )
                
                if filepath:
                    # Não gerar texto e hashtags aqui - será gerado na aba de aprovação quando necessário
                    content_data = {
                        "id": timestamp,
                        "prompt": prompt,
                        "revised_prompt": result["data"].get("revised_prompt", result["data"].get("improved_prompt", prompt)),
                        "post_text": "",  # Será gerado na aprovação
                        "hashtags": "",  # Será gerado na aprovação
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
                # Mensagem de erro mais clara
                error_msg = result.get('message', 'Erro desconhecido')
                if 'GEMINI_API_KEY' in error_msg or 'chave' in error_msg.lower() or 'key' in error_msg.lower():
                    st.error(f"❌ {error_msg}")
                    st.warning("💡 **Solução:** Verifique se a chave API do Gemini está correta no arquivo `.env` na raiz do projeto.")
                    st.info("📝 Obtenha sua chave em: https://aistudio.google.com/app/apikey")
                else:
                    st.error(f"❌ Erro na geração: {error_msg}")
                return None
                
    except Exception as e:
        st.error(f"Erro na geração de conteúdo: {e}")
        logger.exception("Exceção ao gerar conteúdo")
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

def publish_to_social_media(platform: str, content_data: Dict, tiktok_poc, instagram_poc, linkedin_poc):
    """Publicar em rede social"""
    try:
        if platform == "tiktok" and tiktok_poc:
            # Para TikTok, aceitar tanto vídeo quanto imagem
            # Se for imagem, será convertida automaticamente em vídeo curto
            # No modo Sandbox, sempre usar GitHub Pages com PULL_FROM_URL
            filepath = content_data.get("filepath")
            public_url = content_data.get("public_url")
            
            # Verificar se é imagem ou vídeo pela extensão
            is_image = False
            is_video = False
            
            if filepath:
                ext = os.path.splitext(filepath)[1].lower()
                is_image = ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']
                is_video = ext in ['.mp4', '.mov', '.webm', '.avi']
            
            # Configurar título e descrição
            if content_data.get("custom_description"):
                tiktok_poc.video_title = content_data["custom_description"][:100]  # TikTok limita título
                tiktok_poc.video_description = content_data["custom_description"]
            
            # TikTok no modo Sandbox precisa usar GitHub Pages
            # O tiktok_poc.run() já detecta automaticamente e faz upload para GitHub Pages se necessário
            # Mas se já tiver public_url (S3), podemos usar diretamente se for do GitHub Pages
            # Caso contrário, usar filepath local que será enviado para GitHub Pages automaticamente
            
            # Tentar publicar
            if public_url:
                # Verificar se URL é do GitHub Pages (ideal para Sandbox)
                if 'github.io' in public_url.lower() or 'githubusercontent.com' in public_url.lower():
                    # URL já está no GitHub Pages - perfeito para Sandbox
                    if public_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        result = tiktok_poc.run(image_url=public_url)
                    else:
                        result = tiktok_poc.run(video_url=public_url)
                else:
                    # URL de S3 ou outro serviço - para Sandbox, melhor usar filepath local
                    # para que o sistema faça upload para GitHub Pages automaticamente
                    if filepath:
                        if is_image:
                            result = tiktok_poc.run(image_path=filepath)
                        elif is_video:
                            result = tiktok_poc.run(video_path=filepath)
                        else:
                            return {"status": "error", "message": "Formato de arquivo não suportado para TikTok (use MP4, JPG, PNG, etc)"}
                    else:
                        # Se não tem filepath, tentar usar a URL mesmo (pode funcionar se o domínio estiver verificado)
                        if public_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                            result = tiktok_poc.run(image_url=public_url)
                        else:
                            result = tiktok_poc.run(video_url=public_url)
            elif filepath:
                # Verificar se o arquivo existe antes de tentar publicar
                if not os.path.exists(filepath):
                    # Tentar caminho absoluto
                    abs_filepath = os.path.abspath(filepath)
                    if os.path.exists(abs_filepath):
                        filepath = abs_filepath
                    else:
                        return {"status": "error", "message": f"Arquivo não encontrado: {filepath}. Verifique se a imagem foi gerada corretamente."}
                
                # Usar filepath local - o sistema automaticamente faz upload para GitHub Pages e usa PULL_FROM_URL
                if is_image:
                    result = tiktok_poc.run(image_path=filepath)
                elif is_video:
                    result = tiktok_poc.run(video_path=filepath)
                else:
                    return {"status": "error", "message": "Formato de arquivo não suportado para TikTok (use MP4, JPG, PNG, etc)"}
            else:
                return {"status": "error", "message": "Nenhum arquivo ou URL disponível para TikTok"}
        elif platform == "instagram" and instagram_poc:
            # Configurar para Instagram
            result = instagram_poc.run()
        elif platform == "linkedin" and linkedin_poc:
            # Publicar no LinkedIn
            # Prioridade: custom_description > post_text > revised_prompt > prompt
            text = content_data.get("custom_description") or \
                   content_data.get("post_text") or \
                   content_data.get("revised_prompt") or \
                   content_data.get("prompt", "")
            hashtags = content_data.get("hashtags", "")
            
            # Combinar texto e hashtags
            post_text = f"{text}\n\n{hashtags}" if hashtags else text
            
            # Obter URL da imagem se disponível
            image_url = content_data.get("public_url") or content_data.get("filepath")
            
            # Tentar configurar se ainda não estiver configurado
            if not linkedin_poc.access_token:
                if not linkedin_poc.setup():
                    return {"status": "error", "message": "LinkedIn não configurado. Configure o token no arquivo .env"}
            
            result = linkedin_poc.run(text=post_text, image_url=image_url)
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
        ["🏠 Dashboard", "🎨 Gerar Conteúdo", "✅ Aprovar Conteúdo", "📤 Upload TikTok", "📊 Métricas", "⚙️ Configurações"]
    )
    
    # Inicializar POCs
    gemini_poc, s3_poc, metrics_poc, tiktok_poc, instagram_poc, linkedin_poc = initialize_pocs()
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🎨 Gerar Conteúdo":
        show_content_generation(gemini_poc, s3_poc)
    elif page == "✅ Aprovar Conteúdo":
        show_content_approval(tiktok_poc, instagram_poc, linkedin_poc, s3_poc)
    elif page == "📤 Upload TikTok":
        show_tiktok_manual_upload(tiktok_poc)
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

def show_content_generation(gemini_poc, s3_poc):
    """Mostrar página de geração de conteúdo"""
    st.header("🎨 Gerar Conteúdo com IA")
    
    if not gemini_poc:
        st.error("Gemini não configurado. Verifique as configurações.")
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
            content_data = generate_content(gemini_poc, prompt, size, quality, style)
            
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
                
                # Upload para armazenamento (S3 ou GitHub Pages para TikTok)
                # Para TikTok no modo Sandbox, será usado GitHub Pages automaticamente ao publicar
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
                else:
                    # Sem S3 configurado - TikTok usará GitHub Pages automaticamente ao publicar
                    st.info("💡 Para TikTok: O sistema fará upload automático para GitHub Pages ao publicar (modo Sandbox)")
        elif submitted and not prompt:
            st.error("Por favor, insira um prompt para gerar o conteúdo.")

def show_content_approval(tiktok_poc, instagram_poc, linkedin_poc, s3_poc):
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
                    
                    # Gerar texto e hashtags apenas se não existirem
                    if not content.get("post_text") or not content.get("hashtags"):
                        with st.spinner("Gerando texto profissional e hashtags..."):
                            # Buscar o gemini_poc da sessão ou inicializar
                            from pocs.ai_generation.gemini_image_poc import GeminiImagePOC
                            gemini_poc = GeminiImagePOC()
                            if gemini_poc.setup():
                                if not content.get("post_text"):
                                    try:
                                        content["post_text"] = gemini_poc.generate_post_text(content.get("prompt", ""), "linkedin")
                                    except Exception as e:
                                        logger.warning(f"Erro ao gerar texto: {e}")
                                        content["post_text"] = content.get("revised_prompt", content.get("prompt", ""))
                                
                                if not content.get("hashtags"):
                                    try:
                                        content["hashtags"] = gemini_poc.generate_hashtags(content.get("prompt", ""), "linkedin")
                                    except Exception as e:
                                        logger.warning(f"Erro ao gerar hashtags: {e}")
                                        content["hashtags"] = ""
                    
                    # Descrição personalizada (usar texto profissional gerado por padrão)
                    default_text = content.get("post_text") or content.get("revised_prompt", content.get("prompt", ""))
                    custom_description = st.text_area(
                        "Descrição do post:",
                        value=default_text,
                        height=150,
                        help="Texto profissional. Você pode editar antes de publicar."
                    )
                    
                    # Hashtags (usar hashtags geradas por padrão)
                    default_hashtags = content.get("hashtags", "")
                    hashtags = st.text_input(
                        "Hashtags:",
                        value=default_hashtags,
                        placeholder="#ai #arte #digital",
                        help="Hashtags profissionais. Você pode editar antes de publicar."
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
                            with st.spinner("📤 Publicando no TikTok (modo Sandbox - usando GitHub Pages)..."):
                                result = publish_to_social_media("tiktok", content, tiktok_poc, instagram_poc, linkedin_poc)
                                if result["status"] == "success":
                                    published_platforms.append("tiktok")
                                    st.success("✅ Publicado no TikTok com sucesso!")
                                elif result["status"] == "pending":
                                    published_platforms.append("tiktok")
                                    st.warning("⏳ Upload iniciado - o TikTok está processando o vídeo. Verifique sua conta em alguns minutos.")
                                else:
                                    st.error(f"❌ Erro ao publicar no TikTok: {result.get('message', 'Erro desconhecido')}")
                        
                        if publish_instagram:
                            result = publish_to_social_media("instagram", content, tiktok_poc, instagram_poc, linkedin_poc)
                            if result["status"] == "success":
                                published_platforms.append("instagram")
                        
                        if publish_linkedin:
                            result = publish_to_social_media("linkedin", content, tiktok_poc, instagram_poc, linkedin_poc)
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

def show_tiktok_manual_upload(tiktok_poc):
    """Mostrar página de upload manual do TikTok"""
    st.header("📤 Upload Manual - TikTok")
    
    if not tiktok_poc:
        st.error("❌ TikTok não está configurado. Verifique as configurações:")
        st.warning("""
        **Variáveis necessárias no arquivo `.env`:**
        - `TIKTOK_ACCESS_TOKEN` - Token de acesso do TikTok
        - `TIKTOK_OPEN_ID` - ID aberto do TikTok
        - `GITHUB_TOKEN` (opcional) - Para upload automático ao GitHub Pages
        - `GITHUB_REPO` (opcional) - Repositório do GitHub Pages (ex: usuario/repositorio)
        
        Para obter os tokens, execute:
        ```bash
        poetry run python scripts/get_tiktok_token.py
        ```
        """)
        return
    
    st.info("💡 **Dica:** Faça upload de um vídeo local e ele será automaticamente enviado para o TikTok via GitHub Pages (modo Sandbox)")
    
    with st.form("tiktok_manual_upload_form"):
        st.subheader("📁 Selecionar Vídeo")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Escolha um vídeo para publicar no TikTok",
            type=['mp4', 'mov', 'avi', 'webm'],
            help="Formatos suportados: MP4, MOV, AVI, WEBM. Tamanho recomendado: até 287MB"
        )
        
        st.subheader("📝 Detalhes da Publicação")
        
        # Título e descrição
        video_title = st.text_input(
            "Título do vídeo:",
            value="Post automático via API",
            max_chars=100,
            help="Máximo de 100 caracteres"
        )
        
        video_description = st.text_area(
            "Descrição do vídeo:",
            value="Vídeo publicado automaticamente via API do TikTok",
            height=150,
            help="Descrição completa do vídeo"
        )
        
        # Privacidade
        privacy_options = {
            "SELF_ONLY": "Apenas eu (Recomendado para Sandbox)",
            "PUBLIC_TO_EVERYONE": "Público (requer aprovação)"
        }
        privacy_level = st.selectbox(
            "Nível de privacidade:",
            options=list(privacy_options.keys()),
            format_func=lambda x: privacy_options[x],
            help="No modo Sandbox, use 'SELF_ONLY'"
        )
        
        # Botão de envio
        submitted = st.form_submit_button("🚀 Publicar no TikTok", type="primary")
        
        if submitted:
            if not uploaded_file:
                st.error("❌ Por favor, selecione um vídeo para fazer upload")
            else:
                # Salvar arquivo temporário
                import tempfile
                temp_dir = tempfile.mkdtemp()
                temp_video_path = os.path.join(temp_dir, uploaded_file.name)
                
                try:
                    # Salvar arquivo
                    with open(temp_video_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"✅ Vídeo carregado: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")
                    
                    # Configurar TikTok POC
                    tiktok_poc.video_title = video_title
                    tiktok_poc.video_description = video_description
                    tiktok_poc.privacy_level = privacy_level
                    
                    # Publicar
                    with st.spinner("📤 Publicando no TikTok (modo Sandbox - usando GitHub Pages)..."):
                        result = tiktok_poc.run(video_path=temp_video_path)
                    
                    if result["status"] == "success":
                        st.success("✅ Publicado no TikTok com sucesso!")
                        if "data" in result:
                            data = result["data"]
                            st.json({
                                "publish_id": data.get("publish_id", "N/A"),
                                "status": data.get("status", "N/A"),
                                "video_id": data.get("video_id", "N/A"),
                                "share_url": data.get("share_url", "N/A"),
                                "item_id": data.get("item_id", "N/A")
                            })
                    elif result["status"] == "pending":
                        st.warning("⏳ Upload iniciado - o TikTok está processando o vídeo. Verifique sua conta em alguns minutos.")
                        if "data" in result:
                            st.info(f"**Publish ID:** {result['data'].get('publish_id', 'N/A')}")
                    else:
                        error_msg = result.get('message', 'Erro desconhecido')
                        st.error(f"❌ Erro ao publicar: {error_msg}")
                        
                        # Mensagens de ajuda específicas
                        if "access token" in error_msg.lower() or "401" in error_msg:
                            st.warning("""
                            **Token inválido ou expirado!**
                            
                            Para obter novos tokens:
                            1. Execute: `poetry run python scripts/get_tiktok_token.py`
                            2. Siga as instruções para autorizar
                            3. Adicione os tokens ao arquivo `.env`
                            4. Reinicie a interface Streamlit
                            """)
                        elif "domain" in error_msg.lower() or "verification" in error_msg.lower():
                            st.warning("""
                            **Problema de verificação de domínio!**
                            
                            Verifique:
                            1. Se o domínio está verificado no TikTok Developer Portal
                            2. Se o arquivo `.txt` de verificação está no GitHub Pages
                            3. Se a URL do GitHub Pages está correta no `.env`
                            """)
                except Exception as e:
                    st.error(f"❌ Erro ao processar vídeo: {str(e)}")
                    logger.exception("Erro ao fazer upload manual do TikTok")
                finally:
                    # Limpar arquivo temporário
                    try:
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                        if os.path.exists(temp_dir):
                            os.rmdir(temp_dir)
                    except:
                        pass

def show_settings():
    """Mostrar página de configurações"""
    st.header("⚙️ Configurações")
    
    st.subheader("🔑 Chaves de API")
    
    # Google Gemini
    with st.expander("Google Gemini"):
        st.text_input("GEMINI_API_KEY", type="password", help="Chave da API do Google Gemini")
        st.info("Necessário para geração de imagens com Gemini/Imagen")
        st.info("📝 Obtenha sua chave em: https://aistudio.google.com/app/apikey")
    
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

    st.markdown("---")
    st.markdown("### 📄 Documentos Legais")
    st.markdown("""
    - [Termos de Serviço](https://niceasvini.github.io/termos.html)
    - [Política de Privacidade](https://niceasvini.github.io/privacidade.html)
    """)

if __name__ == "__main__":
    main()
