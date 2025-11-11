#!/usr/bin/env python3
"""
POC - Geração de Imagens com Google Gemini/Imagen
Descrição: POC para gerar imagens usando Google Gemini/Imagen API
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import base64
import requests
import logging
from typing import Any, Dict, Optional
from pocs.template_poc import POCTemplate

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configurar logging
logger = logging.getLogger(__name__)


class GeminiImagePOC(POCTemplate):
    """POC para geração de imagens com Google Gemini/Imagen"""
    
    def __init__(self):
        """Inicializar gerador de imagens"""
        super().__init__()
        self.name = "Gemini Image Generation POC"
        self.api_key = None
        
        # Configurações padrão
        self.default_size = "1024x1024"
        self.default_quality = "standard"
        self.default_style = "vivid"
        
        # Note: Google Gemini não tem API de geração de imagens direta como DALL-E
        # Para produção, você precisaria usar Vertex AI Imagen ou outra solução
        # Este POC usa uma abordagem alternativa: Gemini para melhorar prompts
        # e então gerar imagem via outro serviço ou placeholder
    
    def setup(self) -> bool:
        """Configurar conexão com Google Gemini API"""
        try:
            logger.info("Configurando conexão com Google Gemini API...")
            
            if not GEMINI_AVAILABLE:
                logger.error("Biblioteca google-generativeai não instalada. Execute: poetry add google-generativeai")
                return False
            
            # Carregar API key do ambiente
            self.api_key = os.getenv('GEMINI_API_KEY')
            
            if not self.api_key:
                logger.error("GEMINI_API_KEY não encontrado nas variáveis de ambiente")
                return False
            
            # Configurar Gemini
            genai.configure(api_key=self.api_key)
            
            logger.info("Configuração do Gemini concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do Gemini: {e}")
            return False
    
    def _get_gemini_model(self):
        """Obter modelo Gemini disponível"""
        if not GEMINI_AVAILABLE or not self.api_key:
            return None
        
        # Lista de modelos válidos (sem v1beta, usando API v1)
        # Ordem: tentar modelos mais recentes primeiro
        model_names = [
            'gemini-1.5-flash',    # Versão mais rápida e amplamente disponível
            'gemini-1.5-pro',      # Versão mais avançada
            'gemini-pro'           # Modelo padrão (pode estar descontinuado)
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Retornar o modelo sem testar (o teste será feito na chamada real)
                logger.debug(f"Usando modelo Gemini: '{model_name}'")
                return model
            except Exception as e:
                logger.debug(f"Modelo '{model_name}' não disponível: {e}")
                continue
        
        logger.warning("Nenhum modelo Gemini disponível")
        return None
    
    def generate_hashtags(self, prompt: str, platform: str = "linkedin") -> str:
        """Gerar hashtags profissionais baseadas no tema usando Gemini"""
        try:
            model = self._get_gemini_model()
            
            if not model:
                # Fallback: criar hashtags básicas baseadas no tema
                return self._create_fallback_hashtags(prompt)
            
            platform_hashtag_instructions = {
                "linkedin": "5-8 hashtags profissionais e relevantes, sem emojis",
                "instagram": "8-12 hashtags misturando populares e específicas",
                "tiktok": "3-5 hashtags trending e específicas"
            }
            
            instruction = platform_hashtag_instructions.get(platform.lower(), platform_hashtag_instructions["linkedin"])
            
            hashtag_prompt = f"""
            Gere hashtags para um post sobre: {prompt}
            
            IMPORTANTE:
            - {instruction}
            - Seja específico e relevante ao tema
            - Use hashtags em português quando apropriado
            - Formato: #hashtag1 #hashtag2 #hashtag3 (separadas por espaço)
            - Retorne APENAS as hashtags, sem explicações ou texto adicional
            """
            
            response = model.generate_content(hashtag_prompt)
            hashtags = response.text.strip()
            
            # Limpar e formatar
            hashtags = hashtags.strip('"').strip("'").strip()
            
            # Garantir que começa com #
            lines = hashtags.split('\n')
            hashtag_list = []
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    hashtag_list.append(line.split()[0])  # Pegar apenas a primeira palavra se tiver espaço
                elif line and not line.startswith('#'):
                    # Adicionar # se não tiver
                    hashtag_list.append('#' + line.split()[0])
            
            result = ' '.join(hashtag_list[:12])  # Limitar a 12 hashtags
            logger.info(f"Hashtags geradas para {platform}")
            return result
            
        except Exception as e:
            # Não logar erro aqui - apenas retornar fallback silenciosamente
            logger.debug(f"Erro ao gerar hashtags com Gemini (usando fallback): {e}")
            return self._create_fallback_hashtags(prompt)
    
    def _create_fallback_hashtags(self, prompt: str) -> str:
        """Criar hashtags básicas quando Gemini não está disponível"""
        prompt_lower = prompt.lower()
        hashtags = []
        
        # Hashtags baseadas no tema
        if 'financeiro' in prompt_lower or 'mercado financeiro' in prompt_lower:
            hashtags = ['#mercadofinanceiro', '#financeiro', '#investimentos', '#economia', '#negócios', '#empreendedorismo']
        elif 'tecnologia' in prompt_lower or 'tech' in prompt_lower:
            hashtags = ['#tecnologia', '#inovação', '#digital', '#tech', '#transformaçãodigital', '#startup']
        elif 'negócios' in prompt_lower or 'business' in prompt_lower:
            hashtags = ['#negócios', '#business', '#empreendedorismo', '#sucesso', '#marketing', '#empresa']
        elif 'marketing' in prompt_lower:
            hashtags = ['#marketing', '#marketingdigital', '#publicidade', '#branding', '#comunicação', '#mídias']
        else:
            # Hashtags genéricas profissionais
            hashtags = ['#profissional', '#conteúdo', '#inovação', '#sucesso', '#motivação']
        
        return ' '.join(hashtags)
    
    def generate_post_text(self, prompt: str, platform: str = "linkedin") -> str:
        """Gerar texto profissional para post em rede social usando Gemini"""
        try:
            model = self._get_gemini_model()
            
            if not model:
                # Fallback: criar texto básico profissional
                return self._create_fallback_post_text(prompt)
            
            # Criar prompt específico para cada plataforma
            platform_prompts = {
                "linkedin": f"""
                Crie um texto profissional para um post no LinkedIn sobre: {prompt}
                
                IMPORTANTE:
                - Seja profissional e engajador
                - Use linguagem adequada para LinkedIn
                - Inclua insights valiosos ou dicas práticas
                - Texto deve ter entre 100-200 palavras
                - Comece com uma frase impactante
                - Use parágrafos curtos
                - Não inclua hashtags (elas serão adicionadas depois)
                
                Retorne APENAS o texto do post, sem explicações ou citações.
                """,
                "instagram": f"""
                Crie um texto envolvente para um post no Instagram sobre: {prompt}
                
                IMPORTANTE:
                - Seja criativo e visual
                - Use emojis de forma moderada e profissional
                - Texto deve ter entre 80-150 palavras
                - Torne o texto envolvente e interessante
                - Não inclua hashtags (elas serão adicionadas depois)
                
                Retorne APENAS o texto do post, sem explicações.
                """,
                "tiktok": f"""
                Crie um texto impactante e curto para um vídeo no TikTok sobre: {prompt}
                
                IMPORTANTE:
                - Seja direto e impactante
                - Texto deve ter entre 50-100 palavras
                - Use linguagem jovem mas profissional
                - Crie curiosidade e engajamento
                - Não inclua hashtags (elas serão adicionadas depois)
                
                Retorne APENAS o texto, sem explicações.
                """
            }
            
            generation_prompt = platform_prompts.get(platform.lower(), platform_prompts["linkedin"])
            
            response = model.generate_content(generation_prompt)
            post_text = response.text.strip()
            
            # Limpar o texto caso o Gemini tenha adicionado aspas ou formatação
            post_text = post_text.strip('"').strip("'").strip()
            
            # Remover linhas vazias excessivas
            lines = [line.strip() for line in post_text.split('\n') if line.strip()]
            post_text = '\n\n'.join(lines)
            
            logger.info(f"Texto profissional gerado para {platform}")
            return post_text
            
        except Exception as e:
            # Não logar erro aqui - apenas retornar fallback silenciosamente
            logger.debug(f"Erro ao gerar texto profissional com Gemini (usando fallback): {e}")
            return self._create_fallback_post_text(prompt)
    
    def _create_fallback_post_text(self, prompt: str) -> str:
        """Criar texto básico profissional quando Gemini não está disponível"""
        # Templates básicos baseados no tema
        templates = {
            "mercado financeiro": "💼 O mercado financeiro está em constante evolução. É essencial acompanhar as tendências e desenvolver uma estratégia sólida para navegar pelos desafios e oportunidades.\n\nSeja proativo, mantenha-se informado e construa seu conhecimento financeiro dia após dia.",
            "financeiro": "💰 Entender o universo financeiro é fundamental para tomar decisões inteligentes. Invista em conhecimento e esteja sempre atualizado com as melhores práticas do mercado.",
            "tecnologia": "🚀 A tecnologia transforma nosso dia a dia e abre novas possibilidades. Estar atualizado com as inovações tecnológicas é essencial para prosperar no mundo moderno.",
            "negócios": "📈 Empreender requer visão estratégica, resiliência e dedicação. O sucesso nos negócios vem da combinação de conhecimento, networking e execução consistente.",
        }
        
        prompt_lower = prompt.lower()
        for key, template in templates.items():
            if key in prompt_lower:
                return template
        
        # Template genérico
        return f"📌 Explorando o tema: {prompt}\n\nConhecimento e informação são as bases para o crescimento profissional. Mantenha-se atualizado e sempre em busca de novas oportunidades de aprendizado."
    
    def _optimize_search_query(self, prompt: str) -> str:
        """Otimizar query de busca para Pexels usando Gemini ou tradução manual"""
        try:
            model = self._get_gemini_model()
            optimized = None
            
            if model:
                try:
                    optimization_prompt = f"""
                    Converta o seguinte prompt em uma query de busca em inglês otimizada para buscar imagens profissionais relacionadas ao tema.
                    
                    Prompt: {prompt}
                    
                    IMPORTANTE:
                    - Retorne APENAS palavras-chave relevantes em inglês (2-5 palavras)
                    - Foque no tema principal
                    - Use termos comuns de busca em bancos de imagens
                    - Exemplo: "Empresa do mercado financeiro" → "financial company business"
                    - Exemplo: "Tecnologia inovadora" → "technology innovation"
                    
                    Retorne APENAS a query de busca, sem explicações.
                    """
                    
                    response = model.generate_content(optimization_prompt)
                    optimized = response.text.strip()
                    
                    # Limpar a resposta caso o Gemini tenha adicionado explicações
                    if len(optimized) > 50:
                        # Pegar apenas as primeiras palavras
                        optimized = ' '.join(optimized.split()[:5])
                    
                    # Validar se a resposta parece válida (contém palavras em inglês, não erro)
                    if optimized and len(optimized.split()) >= 2:
                        logger.info(f"Query otimizada pelo Gemini: {optimized}")
                        return optimized
                    else:
                        logger.warning("Resposta do Gemini inválida, usando tradução manual")
                except Exception as e:
                    logger.warning(f"Erro ao usar Gemini para otimizar query: {e}")
            
            # Fallback: tradução manual - SEMPRE executar se Gemini falhar
            logger.info("Usando tradução manual para otimizar query...")
            translations = {
                'mercado financeiro': ['financial', 'market', 'business'],
                'empresa do mercado financeiro': ['financial', 'company', 'business', 'corporate'],
                'empresa financeira': ['financial', 'company', 'business'],
                'mercado': ['financial', 'market'],
                'financeiro': ['financial', 'finance'],
                'empresa': ['company', 'business'],
                'empresa do': ['company', 'business'],
                'negócios': ['business', 'corporate'],
                'tecnologia': ['technology', 'innovation'],
                'tech': ['technology'],
                'marketing': ['marketing', 'advertising'],
                'design': ['design', 'creative'],
                'saúde': ['health', 'medical'],
                'educação': ['education', 'learning'],
                'inovação': ['innovation', 'technology'],
                'startup': ['startup', 'business'],
                'corporativo': ['corporate', 'business'],
                'profissional': ['professional', 'business']
            }
            
            prompt_lower = prompt.lower().strip()
            keywords = []
            
            # Buscar termos mais longos primeiro (para pegar "empresa do mercado financeiro" antes de termos menores)
            sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
            
            remaining_prompt = prompt_lower
            for pt_term, en_words in sorted_translations:
                if pt_term in remaining_prompt:
                    keywords.extend(en_words)
                    # Remover o termo encontrado para evitar duplicatas
                    remaining_prompt = remaining_prompt.replace(pt_term, '', 1)
                    logger.debug(f"Termo encontrado: '{pt_term}' → {en_words}")
            
            if keywords:
                # Remover duplicatas mantendo ordem
                unique_keywords = []
                seen = set()
                for kw in keywords:
                    if kw.lower() not in seen:
                        unique_keywords.append(kw.lower())
                        seen.add(kw.lower())
                
                # Limitar a 5 palavras-chave mais relevantes
                result = ' '.join(unique_keywords[:5])
                logger.info(f"✅ Query traduzida manualmente: '{result}'")
                return result
            
            # Se não encontrou tradução, tentar tradução simples palavra por palavra
            word_map = {
                'do': None, 'da': None, 'de': None, 'e': None, 'o': None, 'a': None, 'os': None, 'as': None,
                'empresa': 'company',
                'mercado': 'market',
                'financeiro': 'financial',
                'negócios': 'business',
                'tecnologia': 'technology',
                'inovação': 'innovation',
                'marketing': 'marketing'
            }
            
            words = prompt_lower.split()
            translated_words = []
            for w in words:
                translated = word_map.get(w)
                if translated:
                    translated_words.append(translated)
            
            if translated_words:
                result = ' '.join(translated_words[:5])
                logger.info(f"✅ Query traduzida palavra por palavra: '{result}'")
                return result
            
            # Se tudo falhar, retornar uma busca genérica baseada no contexto
            logger.warning(f"⚠️ Não foi possível traduzir '{prompt}'. Usando busca genérica.")
            # Nunca usar o prompt em português no Pexels
            return "business professional"
                
        except Exception as e:
            logger.warning(f"Erro ao otimizar query: {e}. Usando busca genérica.")
            # NUNCA retornar prompt em português - sempre usar fallback em inglês
            return "business professional"
    
    def generate_image(self, prompt: str, size: str = None, quality: str = None, style: str = None) -> Dict[str, Any]:
        """
        Gerar imagem usando Google Gemini/Imagen
        
        NOTA: O Google Gemini não possui uma API pública direta de geração de imagens como o DALL-E.
        Este método usa uma abordagem alternativa:
        1. Usa Gemini para melhorar/enriquecer o prompt
        2. Para produção, você precisaria integrar com Vertex AI Imagen ou outro serviço
        
        Para desenvolvimento/teste, retornamos um placeholder ou imagem gerada via outro método.
        """
        try:
            logger.info(f"Gerando imagem com prompt: {prompt}")
            
            # Usar configurações padrão se não especificadas
            size = size or self.default_size
            quality = quality or self.default_quality
            style = style or self.default_style
            
            # Passo 1: Usar Gemini para melhorar o prompt (opcional)
            # Se falhar, o sistema continua com o prompt original
            improved_prompt = prompt
            model = self._get_gemini_model()
            
            if model:
                try:
                    improvement_prompt = f"""
                    Melhore o seguinte prompt para geração de imagem, tornando-o mais detalhado e visual:
                    
                    Prompt original: {prompt}
                    
                    Retorne APENAS o prompt melhorado, sem explicações adicionais.
                    """
                    
                    response = model.generate_content(improvement_prompt)
                    improved_prompt = response.text.strip()
                    
                    logger.info(f"Prompt melhorado pelo Gemini: {improved_prompt}")
                except Exception as e:
                    logger.warning(f"Erro ao melhorar prompt com Gemini: {e}. Usando prompt original.")
                    improved_prompt = prompt
            
            # Passo 2: Gerar ou buscar imagem profissional relacionada ao tema
            image_bytes = None
            
            # Opção 1: Tentar buscar imagem do Pexels (gratuito, profissional)
            pexels_api_key = os.getenv('PEXELS_API_KEY')
            if pexels_api_key:
                try:
                    logger.info("Tentando buscar imagem relacionada ao tema no Pexels...")
                    
                    # Calcular variação baseada no timestamp para variar imagens
                    # Usa timestamp + hash do prompt para garantir variedade mesmo com mesmo tema
                    import time
                    import hashlib
                    
                    # Criar uma "assinatura" única baseada no prompt e timestamp
                    prompt_hash = int(hashlib.md5(prompt.lower().encode()).hexdigest()[:8], 16)
                    timestamp_seconds = int(time.time())
                    
                    # Combinar ambos para criar variação, mas que mude ao longo do tempo
                    variation_seed = (prompt_hash + timestamp_seconds) % 10  # Varia entre 0-9
                    
                    logger.info(f"Usando variação {variation_seed} para tema '{prompt}'")
                    
                    # Usar prompt original para busca (melhor para tradução)
                    image_bytes = self._search_image_from_pexels(prompt, size, variation_seed)
                    if image_bytes:
                        logger.info("✅ Imagem encontrada no Pexels")
                    else:
                        logger.warning("Nenhuma imagem encontrada no Pexels para este tema")
                except Exception as e:
                    logger.warning(f"Erro ao buscar imagem no Pexels: {e}")
            
            # Opção 2: Criar placeholder profissional relacionado ao tema
            if not image_bytes:
                logger.info("Gerando imagem placeholder profissional relacionada ao tema...")
                image_bytes = self._generate_placeholder_image(improved_prompt, size)
            
            # Passo 3: Gerar texto profissional para post
            post_text = None
            hashtags = None
            try:
                logger.info("Gerando texto profissional para post...")
                post_text = self.generate_post_text(prompt, "linkedin")
                
                logger.info("Gerando hashtags profissionais...")
                hashtags = self.generate_hashtags(prompt, "linkedin")
            except Exception as e:
                logger.warning(f"Erro ao gerar conteúdo de texto: {e}")
            
            logger.info("Imagem gerada com sucesso")
            return {
                "status": "success",
                "message": "Imagem gerada com sucesso",
                "data": {
                    "image_bytes": image_bytes,
                    "prompt": prompt,
                    "improved_prompt": improved_prompt,
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "revised_prompt": improved_prompt,  # Compatibilidade com código existente
                    "post_text": post_text,  # Texto profissional gerado
                    "hashtags": hashtags  # Hashtags profissionais geradas
                }
            }
                
        except Exception as e:
            logger.error(f"Erro na geração de imagem: {e}")
            return {
                "status": "error",
                "message": f"Erro ao gerar imagem: {str(e)}",
                "data": {}
            }
    
    def _search_image_from_pexels(self, prompt: str, size: str, image_variation: int = 0) -> Optional[bytes]:
        """
        Buscar imagem profissional relacionada ao tema no Pexels
        
        Args:
            prompt: Tema da busca
            size: Tamanho da imagem
            image_variation: Índice para variar a imagem (0 = primeira, 1 = segunda, etc)
        """
        try:
            pexels_api_key = os.getenv('PEXELS_API_KEY')
            if not pexels_api_key:
                return None
            
            # Usar Gemini para criar uma query de busca otimizada em inglês
            search_query = self._optimize_search_query(prompt)
            
            # Limitar tamanho da query para busca
            if len(search_query) > 100:
                search_query = search_query[:100]
            
            # Buscar imagem no Pexels
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": pexels_api_key
            }
            # Determinar orientação baseado no tamanho
            orientation = "square"
            if "x" in size:
                try:
                    width, height = map(int, size.split('x'))
                    if width > height:
                        orientation = "landscape"
                    elif height > width:
                        orientation = "portrait"
                except:
                    orientation = "square"
            
            # Buscar múltiplas imagens para permitir variação
            per_page = max(5, image_variation + 1)  # Buscar pelo menos o suficiente para a variação desejada
            
            params = {
                "query": search_query,
                "per_page": per_page,
                "orientation": orientation,
                "page": 1  # Sempre buscar da primeira página, mas variar qual imagem pegar
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                logger.info(f"Pexels retornou {len(photos)} imagens para a query: '{search_query}'")
                
                if photos:
                    # Variar qual imagem usar baseado em image_variation
                    # Usar módulo para garantir que não ultrapasse o array
                    photo_index = image_variation % len(photos)
                    photo = photos[photo_index]
                    
                    if image_variation > 0:
                        logger.info(f"Usando variação {photo_index + 1} de {len(photos)} imagens disponíveis")
                    photo_url = photo.get("src", {}).get("large2x") or \
                               photo.get("src", {}).get("large") or \
                               photo.get("src", {}).get("medium") or \
                               photo.get("src", {}).get("original")
                    
                    if photo_url:
                        # Baixar a imagem
                        img_response = requests.get(photo_url, timeout=15)
                        if img_response.status_code == 200:
                            # Redimensionar se necessário usando Pillow
                            try:
                                from PIL import Image
                                import io
                                
                                img = Image.open(io.BytesIO(img_response.content))
                                
                                # Redimensionar para o tamanho solicitado
                                target_width, target_height = map(int, size.split('x'))
                                img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                                
                                # Converter para bytes
                                img_byte_arr = io.BytesIO()
                                img_resized.save(img_byte_arr, format='PNG')
                                return img_byte_arr.getvalue()
                            except ImportError:
                                # Se Pillow não estiver disponível, retornar imagem original
                                return img_response.content
                            
            logger.warning("Nenhuma imagem encontrada no Pexels para o tema")
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao buscar imagem no Pexels: {e}")
            return None
    
    def _generate_placeholder_image(self, prompt: str, size: str) -> bytes:
        """
        Gerar imagem placeholder profissional relacionada ao tema
        Cria uma imagem visualmente atraente baseada nas palavras-chave do prompt
        """
        try:
            from PIL import Image, ImageDraw, ImageFont, ImageFilter
            import io
            
            width, height = map(int, size.split('x'))
            
            # Extrair palavras-chave principais do prompt
            keywords = prompt.lower().split()[:5]  # Pegar até 5 palavras principais
            main_keyword = keywords[0] if keywords else "conteúdo"
            
            # Criar gradiente de cores baseado no tema
            # Cores profissionais para diferentes temas
            color_schemes = {
                'financeiro': ['#1e3a5f', '#2d5aa0', '#4a90e2', '#87ceeb'],
                'mercado': ['#1e3a5f', '#2d5aa0', '#4a90e2', '#87ceeb'],  # Alias para financeiro
                'financeira': ['#1e3a5f', '#2d5aa0', '#4a90e2', '#87ceeb'],
                'tecnologia': ['#0f3460', '#16213e', '#533483', '#e94560'],
                'tech': ['#0f3460', '#16213e', '#533483', '#e94560'],
                'negócios': ['#2c3e50', '#34495e', '#3498db', '#2980b9'],
                'business': ['#2c3e50', '#34495e', '#3498db', '#2980b9'],
                'marketing': ['#c0392b', '#e74c3c', '#ec7063', '#f1948a'],
                'design': ['#8e44ad', '#9b59b6', '#bb8fce', '#d7bde2'],
                'saúde': ['#27ae60', '#2ecc71', '#58d68d', '#82e0aa'],
                'health': ['#27ae60', '#2ecc71', '#58d68d', '#82e0aa'],
                'educação': ['#f39c12', '#f4d03f', '#f7dc6f', '#f9e79f'],
                'education': ['#f39c12', '#f4d03f', '#f7dc6f', '#f9e79f'],
            }
            
            # Escolher esquema de cores baseado no prompt
            prompt_lower = prompt.lower()
            colors = ['#3498db', '#2ecc71', '#9b59b6', '#e74c3c']  # Default
            for key, scheme in color_schemes.items():
                if key in prompt_lower:
                    colors = scheme
                    break
            
            # Criar imagem com gradiente
            img = Image.new('RGB', (width, height), color=colors[0])
            draw = ImageDraw.Draw(img)
            
            # Desenhar gradiente circular ou retangular
            num_steps = 50
            center_x, center_y = width // 2, height // 2
            max_radius = int((width ** 2 + height ** 2) ** 0.5)
            
            for i in range(num_steps):
                alpha = i / num_steps
                # Interpolar entre cores
                color_idx = int(alpha * (len(colors) - 1))
                next_idx = min(color_idx + 1, len(colors) - 1)
                local_alpha = (alpha * (len(colors) - 1)) % 1
                
                # Converter hex para RGB
                def hex_to_rgb(h):
                    return tuple(int(h[j:j+2], 16) for j in (1, 3, 5))
                
                rgb1 = hex_to_rgb(colors[color_idx])
                rgb2 = hex_to_rgb(colors[next_idx])
                rgb = tuple(int(rgb1[k] * (1 - local_alpha) + rgb2[k] * local_alpha) for k in range(3))
                
                radius = int(max_radius * alpha)
                draw.ellipse(
                    [center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius],
                    fill=rgb, outline=None
                )
            
            # Adicionar texto estilizado
            try:
                # Tentar usar fonte maior se disponível
                font_size = min(width // 15, height // 15, 48)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                    except:
                        font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Texto principal (tema)
            main_text = main_keyword.upper()
            bbox = draw.textbbox((0, 0), main_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Adicionar sombra ao texto para melhor legibilidade
            shadow_offset = 2
            draw.text(
                ((width - text_width) // 2 + shadow_offset, (height - text_height) // 2 + shadow_offset),
                main_text, fill='#000000', font=font, align='center'
            )
            draw.text(
                ((width - text_width) // 2, (height - text_height) // 2),
                main_text, fill='#ffffff', font=font, align='center'
            )
            
            # Aplicar filtro de blur sutil para suavizar
            try:
                img = img.filter(ImageFilter.GaussianBlur(radius=1))
            except:
                pass
            
            # Converter para bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG', quality=95)
            img_byte_arr = img_byte_arr.getvalue()
            
            logger.info(f"Imagem placeholder profissional criada (tamanho: {width}x{height}, tema: {main_keyword})")
            return img_byte_arr
            
        except ImportError:
            # Se Pillow não estiver disponível, criar uma imagem mínima em bytes
            logger.warning("Pillow não disponível. Criando placeholder mínimo.")
            # Retornar uma imagem PNG mínima válida (1x1 pixel transparente)
            minimal_png = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            )
            return minimal_png
        except Exception as e:
            logger.error(f"Erro ao criar placeholder: {e}")
            raise
    
    def save_image(self, image_bytes: bytes, filename: str, output_dir: str = "generated_images") -> str:
        """Salvar imagem em arquivo"""
        try:
            # Criar diretório se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Caminho completo do arquivo
            filepath = os.path.join(output_dir, filename)
            
            # Salvar imagem
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"Imagem salva em: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao salvar imagem: {e}")
            return ""
    
    def run(self) -> Dict[str, Any]:
        """Executar geração de imagem de exemplo"""
        try:
            logger.info("Executando geração de imagem de exemplo...")
            
            # Prompt de exemplo
            test_prompt = "A futuristic robot creating digital art in a modern studio, high quality, detailed"
            
            # Gerar imagem
            result = self.generate_image(test_prompt)
            
            if result["status"] == "success":
                # Salvar imagem
                filename = f"generated_image_{int(os.urandom(4).hex(), 16)}.png"
                filepath = self.save_image(
                    result["data"]["image_bytes"], 
                    filename
                )
                
                if filepath:
                    result["data"]["filepath"] = filepath
                    result["data"]["filename"] = filename
                
                logger.info("Geração de imagem concluída com sucesso")
                return result
            else:
                logger.error(f"Falha na geração: {result['message']}")
                return result
            
        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def cleanup(self):
        """Limpar recursos"""
        try:
            logger.info("Limpando recursos do Gemini...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza do Gemini concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = GeminiImagePOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração do Gemini")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - Geração de Imagem Gemini:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            print(f"\nDetalhes da geração:")
            print(f"  Prompt: {result['data'].get('prompt', 'N/A')}")
            print(f"  Prompt melhorado: {result['data'].get('improved_prompt', 'N/A')}")
            print(f"  Tamanho: {result['data'].get('size', 'N/A')}")
            print(f"  Qualidade: {result['data'].get('quality', 'N/A')}")
            print(f"  Estilo: {result['data'].get('style', 'N/A')}")
            print(f"  Arquivo salvo: {result['data'].get('filepath', 'N/A')}")
        
        print("\n⚠️  NOTA IMPORTANTE:")
        print("O Google Gemini não possui uma API pública de geração de imagens como o DALL-E.")
        print("Este POC usa um placeholder. Para produção, considere:")
        print("  1. Usar Vertex AI Imagen (requer Google Cloud)")
        print("  2. Integrar com outro serviço de geração de imagens")
        print("  3. Usar Gemini apenas para melhorar prompts")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()

