#!/usr/bin/env python3
"""
TikTok POC - Upload de Vídeo
Descrição: POC para fazer upload automático de vídeos no TikTok
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import requests
import json
import logging
import tempfile
import subprocess
import shutil
from typing import Any, Dict
from pocs.template_poc import POCTemplate

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TikTokUploadPOC(POCTemplate):
    """POC para upload de vídeos no TikTok"""
    
    def __init__(self):
        """Inicializar uploader do TikTok"""
        super().__init__()
        self.name = "TikTok Upload POC"
        self.access_token = None
        self.open_id = None
        self.base_url = "https://open.tiktokapis.com"
        
        # Configurações do vídeo de teste
        self.video_path = None
        self.video_title = "Teste de upload automático"
        self.video_description = "Vídeo de teste enviado via API do TikTok"
        self.privacy_level = "SELF_ONLY"  # SELF_ONLY é obrigatório para Sandbox
        
        # Configurações do GitHub Pages (para Sandbox - PULL_FROM_URL)
        self.github_pages_url = os.getenv('GITHUB_PAGES_URL', 'https://niceasvini.github.io')
        self.use_github_pages = os.getenv('USE_GITHUB_PAGES', 'true').lower() == 'true'
        self.github_token = os.getenv('GITHUB_TOKEN')  # Opcional: para upload automático
        self.github_repo = os.getenv('GITHUB_REPO', 'niceasvini/niceasvini.github.io')
    
    def setup(self) -> bool:
        """Configurar conexão com TikTok API"""
        try:
            logger.info("Configurando conexão com TikTok API...")
            
            # Carregar credenciais do ambiente
            self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
            self.open_id = os.getenv('TIKTOK_OPEN_ID')
            
            if not self.access_token:
                logger.error("TIKTOK_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
                return False
            
            if not self.open_id:
                logger.error("TIKTOK_OPEN_ID não encontrado nas variáveis de ambiente")
                return False
            
            # Vídeo é opcional - pode ser fornecido no run()
            # Não definir video_path padrão aqui, será definido no run() se necessário
            self.video_path = None
            
            logger.info("Configuração do TikTok concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do TikTok: {e}")
            return False
    
    def convert_image_to_short_video(self, image_path: str) -> str:
        """
        Converte uma imagem em um vídeo curto MP4 para compatibilidade com o TikTok Sandbox
        O TikTok Sandbox não suporta fotos diretamente, mas aceita vídeos curtos
        """
        try:
            logger.info("Convertendo imagem em vídeo curto MP4...")
            
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "image_video.mp4")
            
            # Encontrar FFmpeg
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                # Tentar caminhos comuns no Windows
                username = os.getenv('USERNAME', '')
                userprofile = os.getenv('USERPROFILE', '')
                common_paths = [
                    'ffmpeg',
                    'C:\\ffmpeg\\bin\\ffmpeg.exe',
                    f'{userprofile}\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.0-full_build\\bin\\ffmpeg.exe',
                ]
                
                for path in common_paths:
                    if path == 'ffmpeg':
                        try:
                            test_result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
                            if test_result.returncode == 0:
                                ffmpeg_path = 'ffmpeg'
                                break
                        except:
                            continue
                    elif os.path.exists(path):
                        try:
                            test_result = subprocess.run([path, '-version'], capture_output=True, timeout=5)
                            if test_result.returncode == 0:
                                ffmpeg_path = path
                                break
                        except:
                            continue
                
                if not ffmpeg_path:
                    raise Exception("FFmpeg não encontrado. Instale com: winget install ffmpeg")
            
            # Comando FFmpeg para converter imagem em vídeo curto
            # IMPORTANTE: Usa exatamente a imagem fornecida, sem gerar nova
            logger.info(f"Executando FFmpeg para criar vídeo curto a partir da imagem: {image_path}")
            cmd = [
                ffmpeg_path,
                "-loop", "1",
                "-i", image_path,  # Usar exatamente a imagem fornecida
                "-t", "3",  # 3 segundos de duração
                "-vf", "scale=1080:1920,format=yuv420p",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",  # 30 fps
                "-y", output_path
            ]
            
            logger.info("Executando FFmpeg para criar vídeo curto...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg erro: {result.stderr}")
                raise Exception(f"Erro ao converter imagem em vídeo: {result.stderr}")
            
            video_size = os.path.getsize(output_path)
            logger.info(f"✅ Imagem convertida em vídeo curto: {output_path} ({video_size / (1024*1024):.2f}MB)")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao converter imagem em vídeo: {e}")
            raise
    
    def get_user_info(self) -> Dict[str, Any]:
        """Obter informações do usuário"""
        try:
            url = f"{self.base_url}/v2/user/info/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            params = {
                "fields": "open_id,union_id,avatar_url,display_name,username"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter info do usuário: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do usuário: {e}")
            return {}
    
    def upload_video_via_url(self, video_url: str) -> Dict[str, Any]:
        """
        Upload de vídeo usando PULL_FROM_URL (requerido para Sandbox com GitHub Pages)
        """
        try:
            logger.info(f"Iniciando upload de vídeo via URL: {video_url}")
            
            # Passo 1: Inicializar o upload com PULL_FROM_URL
            init_url = f"{self.base_url}/v2/post/publish/video/init/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Estrutura para PULL_FROM_URL (conforme documentação do TikTok)
            init_data = {
                "post_info": {
                    "title": self.video_title,
                    "description": self.video_description,
                    "privacy_level": self.privacy_level,
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }
            
            logger.info(f"Payload: {json.dumps(init_data, indent=2)}")
            
            response = requests.post(init_url, headers=headers, json=init_data)
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_code = error_data.get("error", {}).get("code", "")
                error_message = error_data.get("error", {}).get("message", response.text)
                
                logger.error(f"Erro ao inicializar upload: {response.status_code} - {error_message}")
                
                # Mensagens de erro mais específicas para Sandbox
                if "url ownership verification" in error_message.lower():
                    logger.error("="*60)
                    logger.error("⚠️ ERRO 403: Propriedade do Domínio/URL não verificada")
                    logger.error("="*60)
                    logger.error("Para usar PULL_FROM_URL, você PRECISA verificar a propriedade do domínio no TikTok Portal!")
                    logger.error("")
                    logger.error("📋 COMO VERIFICAR O DOMÍNIO:")
                    logger.error("")
                    logger.error("1. Acesse o TikTok Developer Portal:")
                    logger.error("   https://developers.tiktok.com/")
                    logger.error("")
                    logger.error("2. Vá em 'Manage Apps' → Selecione seu app")
                    logger.error("")
                    logger.error("3. Na seção 'Products', encontre 'Content Posting API'")
                    logger.error("")
                    logger.error("4. Procure por 'Domain' ou 'URL Prefix' no widget de propriedades")
                    logger.error("")
                    logger.error("5. Adicione e verifique:")
                    logger.error(f"   - Domínio: niceasvini.github.io")
                    logger.error(f"   - OU Prefixo de URL: https://niceasvini.github.io/")
                    logger.error("")
                    logger.error("6. Para verificar, você pode:")
                    logger.error("   a) Adicionar um registro DNS (recomendado)")
                    logger.error("   b) OU adicionar um arquivo TXT na raiz do GitHub Pages")
                    logger.error("")
                    logger.error("7. Após verificar, aguarde alguns minutos e tente novamente")
                    logger.error("")
                    logger.error("📖 Documentação completa:")
                    logger.error("   https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide/#pull_from_url")
                    logger.error("="*60)
                elif "unaudited_client" in error_message.lower():
                    logger.error("="*60)
                    logger.error("⚠️ ERRO: Aplicação TikTok em modo Sandbox")
                    logger.error("="*60)
                    logger.error("Aplicações em Sandbox só podem postar em contas PRIVADAS.")
                    logger.error("O código já está configurado para SELF_ONLY (privado).")
                    logger.error("")
                    logger.error("SOLUÇÕES:")
                    logger.error("1. Certifique-se de que os tokens foram gerados com escopo correto")
                    logger.error("2. Tente regenerar os tokens: poetry run python scripts/get_tiktok_token.py")
                    logger.error("3. Para postar público, submeta o app para revisão no TikTok Portal")
                    logger.error("="*60)
                elif "integration guidelines" in error_message.lower():
                    logger.error("="*60)
                    logger.error("⚠️ ERRO: TikTok pedindo revisão das diretrizes de integração")
                    logger.error("="*60)
                    logger.error("Este erro geralmente significa:")
                    logger.error("1. Aplicação não está configurada corretamente no TikTok Portal")
                    logger.error("2. Faltam informações obrigatórias (Privacy Policy, Terms, etc)")
                    logger.error("3. Vídeo pode não atender aos requisitos de qualidade")
                    logger.error("")
                    logger.error("SOLUÇÕES:")
                    logger.error("1. Verifique se TODAS as informações estão preenchidas no TikTok Portal")
                    logger.error("2. Verifique se o vídeo atende aos requisitos (tamanho, formato, resolução)")
                    logger.error("3. Tente regenerar tokens com escopos corretos")
                    logger.error("="*60)
                
                return {
                    "status": "error", 
                    "message": f"Falha ao inicializar upload: {error_message}",
                    "error_code": error_code
                }
            
            init_result = response.json()
            publish_id = init_result["data"]["publish_id"]
            
            logger.info(f"Upload inicializado. Publish ID: {publish_id}")
            logger.info("Usando PULL_FROM_URL - TikTok vai baixar o vídeo automaticamente da URL")
            
            # Com PULL_FROM_URL, não precisamos fazer upload do arquivo
            # O TikTok processa a URL automaticamente
            
            logger.info("Aguardando TikTok processar o download do vídeo...")
            logger.info("(Isso pode levar alguns segundos/minutos dependendo do tamanho do vídeo)")
            
            # Passo 2: Confirmar o upload (com retries, pois o TikTok pode estar ainda baixando)
            confirm_url = f"{self.base_url}/v2/post/publish/status/fetch/"
            confirm_params = {"publish_id": publish_id}
            
            import time
            max_attempts = 5
            attempt = 0
            initial_wait = 5
            wait_time = 5
            
            logger.info(f"Aguardando {initial_wait} segundos antes de verificar o status...")
            time.sleep(initial_wait)
            
            while attempt < max_attempts:
                attempt += 1
                logger.info(f"Tentativa {attempt}/{max_attempts} de verificar status do upload...")
                
                confirm_response = requests.post(confirm_url, headers=headers, params=confirm_params, timeout=30)
                
                if confirm_response.status_code == 200:
                    try:
                        confirm_result = confirm_response.json()
                        data = confirm_result.get("data", {})
                        status = data.get("status", "unknown")
                        
                        video_id = data.get("video_id", "")
                        share_url = data.get("share_url", "")
                        item_id = data.get("item_id", "")
                        
                        logger.info(f"Status atual: {status}")
                        
                        is_published = (
                            status == "PUBLISHED" or
                            (video_id and video_id != "") or
                            (share_url and share_url != "") or
                            (item_id and item_id != "")
                        )
                        
                        if is_published:
                            logger.info("✅ Vídeo foi publicado com sucesso!")
                            return {
                                "status": "success",
                                "message": "✅ Vídeo publicado com sucesso no TikTok!",
                                "data": {
                                    "publish_id": publish_id,
                                    "status": status,
                                    "video_id": video_id,
                                    "item_id": item_id,
                                    "share_url": share_url,
                                    "source_url": video_url
                                }
                            }
                        elif status == "FAILED":
                            fail_reason = data.get("fail_reason", "Erro desconhecido")
                            logger.error(f"❌ Upload falhou: {fail_reason}")
                            return {
                                "status": "error",
                                "message": f"Upload falhou: {fail_reason}",
                                "data": {"publish_id": publish_id, "status": status}
                            }
                        elif status == "PROCESSING":
                            logger.info(f"⏳ Ainda processando... Status: {status}")
                            if attempt < max_attempts:
                                logger.info(f"Aguardando {wait_time} segundos antes da próxima tentativa...")
                                time.sleep(wait_time)
                                continue
                            else:
                                return {
                                    "status": "pending",
                                    "message": "Upload iniciado mas ainda processando. Verifique sua conta do TikTok.",
                                    "data": {"publish_id": publish_id, "status": status, "source_url": video_url}
                                }
                        else:
                            logger.info(f"Status: {status}. Aguardando conclusão...")
                            if attempt < max_attempts:
                                time.sleep(wait_time)
                                continue
                    except Exception as e:
                        logger.error(f"Erro ao parsear resposta: {e}")
                        logger.error(f"Resposta recebida: {confirm_response.text[:500]}")
                
                elif confirm_response.status_code == 400:
                    try:
                        error_data = confirm_response.json()
                        error_code = error_data.get("error", {}).get("code", "")
                        error_msg = error_data.get("error", {}).get("message", confirm_response.text)
                        
                        if "invalid_publish_id" in error_code.lower() or "invalid_publish_id" in error_msg.lower():
                            if attempt < max_attempts:
                                logger.info(f"Publish ID ainda não disponível para consulta (TikTok ainda está processando).")
                                logger.info(f"Aguardando {wait_time} segundos antes da próxima tentativa...")
                                time.sleep(wait_time)
                                continue
                            else:
                                return {
                                    "status": "pending",
                                    "message": "Upload iniciado mas ainda em processamento. O TikTok está baixando o vídeo da URL.",
                                    "data": {"publish_id": publish_id, "source_url": video_url}
                                }
                        else:
                            if attempt < max_attempts - 1:
                                time.sleep(wait_time)
                                continue
                            return {
                                "status": "error",
                                "message": f"Falha ao confirmar upload: {error_msg}",
                                "data": {"publish_id": publish_id}
                            }
                    except:
                        if attempt < max_attempts:
                            time.sleep(wait_time)
                            continue
                else:
                    logger.error(f"Erro ao confirmar upload: {confirm_response.status_code}")
                    if attempt < max_attempts and confirm_response.status_code in [429, 500, 502, 503, 504]:
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            "status": "error",
                            "message": f"Falha ao confirmar upload: {confirm_response.status_code}",
                            "data": {"publish_id": publish_id}
                        }
            
            # Se chegou aqui, esgotou as tentativas
            logger.warning("Esgotou as tentativas de verificar o status.")
            return {
                "status": "pending",
                "message": "✅ Upload iniciado com sucesso! O TikTok está processando o vídeo em segundo plano. Verifique sua conta do TikTok em alguns minutos.",
                "data": {
                    "publish_id": publish_id,
                    "source_url": video_url,
                    "note": "O vídeo foi enviado e será publicado automaticamente. No modo Sandbox, vídeos são publicados como PRIVADOS (SELF_ONLY)."
                }
            }
                
        except Exception as e:
            logger.error(f"Erro no upload do vídeo via URL: {e}")
            return {"status": "error", "message": str(e)}
    
    def upload_to_github_pages_via_api(self, local_file_path: str, filename: str) -> str:
        """
        Faz upload do arquivo para GitHub Pages via GitHub API
        Requer GITHUB_TOKEN configurado no .env
        """
        try:
            import base64
            
            logger.info("Fazendo upload automático para GitHub via API...")
            
            # Ler conteúdo do arquivo
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            # Codificar em base64 (GitHub API requer base64)
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # URL da API do GitHub para criar arquivo (na raiz, não em subpasta)
            api_url = f"https://api.github.com/repos/{self.github_repo}/contents/{filename}"
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Tentar descobrir a branch padrão do repositório
            branches_to_try = ["main", "master", "gh-pages"]
            
            try:
                repo_info_url = f"https://api.github.com/repos/{self.github_repo}"
                repo_response = requests.get(repo_info_url, headers={"Accept": "application/vnd.github.v3+json"}, timeout=10)
                if repo_response.status_code == 200:
                    repo_data = repo_response.json()
                    default_branch = repo_data.get("default_branch", "main")
                    if default_branch in branches_to_try:
                        branches_to_try.remove(default_branch)
                    branches_to_try.insert(0, default_branch)
                    logger.info(f"Branch padrão do repositório: {default_branch}")
            except:
                pass
            
            for branch in branches_to_try:
                try:
                    # Payload para criar arquivo
                    payload = {
                        "message": f"Adicionar vídeo para TikTok - {filename}",
                        "content": file_content_b64,
                        "branch": branch
                    }
                    
                    # Fazer upload
                    response = requests.put(api_url, headers=headers, json=payload)
                    
                    if response.status_code in [201, 200]:
                        # URL na raiz do GitHub Pages (lowercase)
                        github_pages_url = f"{self.github_pages_url.lower()}/{filename}"
                        logger.info(f"✅ Upload na branch '{branch}' concluído!")
                        return github_pages_url
                    elif response.status_code == 422:
                        # Arquivo já existe ou branch incorreta - tentar próxima branch
                        logger.debug(f"Branch '{branch}' não funcionou (422), tentando próxima...")
                        continue
                    else:
                        logger.debug(f"Branch '{branch}' retornou {response.status_code}, tentando próxima...")
                        continue
                except Exception as e:
                    logger.debug(f"Erro ao tentar branch '{branch}': {e}")
                    continue
            
            # Se nenhuma branch funcionou
            raise Exception(f"GitHub API: nenhuma branch funcionou (tentadas: {', '.join(branches_to_try)})")
                    
        except Exception as e:
            logger.error(f"Erro no upload via GitHub API: {e}")
            raise
    
    def prepare_video_for_github_pages(self, video_path: str) -> str:
        """
        Prepara o vídeo para GitHub Pages:
        1. Tenta fazer upload automático via GitHub API se tiver token
        2. Se não tiver token, mostra instruções para push manual
        3. Retorna a URL pública esperada no GitHub Pages
        """
        try:
            filename = os.path.basename(video_path)
            
            logger.info(f"Preparando vídeo '{filename}' para GitHub Pages: {self.github_pages_url}")
            logger.info(f"Repositório destino: {self.github_repo}")
            
            # Tentar fazer upload automático via GitHub API (RECOMENDADO)
            if self.github_token:
                try:
                    logger.info("Tentando fazer upload automático via GitHub API...")
                    github_pages_url = self.upload_to_github_pages_via_api(video_path, filename)
                    logger.info(f"✅ Upload automático concluído! URL: {github_pages_url}")
                    return github_pages_url
                except Exception as e:
                    logger.warning(f"⚠️ Erro no upload automático via GitHub API: {e}")
                    logger.info("Continuando com instruções para push manual...")
            
            # Se não tem token ou upload falhou, mostrar instruções (lowercase para consistência)
            github_pages_url = f"{self.github_pages_url.lower()}/{filename}"
            
            logger.info("="*60)
            logger.info("📋 COMO COLOCAR O VÍDEO NO SEU SITE (GitHub Pages):")
            logger.info("="*60)
            logger.info(f"📍 Vídeo local: {video_path}")
            logger.info(f"🌐 URL destino: {github_pages_url}")
            logger.info("")
            logger.info("OPÇÃO 1: Upload Automático (Recomendado)")
            logger.info("  1. Obtenha um GitHub Token:")
            logger.info("     https://github.com/settings/tokens")
            logger.info("     Permissão: 'repo' (controle total dos repositórios)")
            logger.info("  2. Adicione no arquivo .env:")
            logger.info(f"     GITHUB_TOKEN=seu_token_aqui")
            logger.info("  3. Execute o script novamente - o upload será automático!")
            logger.info("")
            logger.info("OPÇÃO 2: Push Manual")
            logger.info(f"  1. Clone ou vá para o repositório do seu GitHub Pages:")
            logger.info(f"     git clone https://github.com/{self.github_repo}.git")
            logger.info(f"     cd {self.github_repo.split('/')[1]}")
            logger.info(f"  2. Copie o vídeo para a raiz do repositório:")
            logger.info(f"     cp \"{video_path}\" .")
            logger.info(f"  3. Faça commit e push:")
            logger.info(f"     git add {filename}")
            logger.info(f"     git commit -m 'Adicionar vídeo para TikTok'")
            logger.info(f"     git push")
            logger.info(f"  4. Após o push, o vídeo estará disponível em:")
            logger.info(f"     {github_pages_url}")
            logger.info("="*60)
            
            return github_pages_url
            
        except Exception as e:
            logger.error(f"Erro ao preparar vídeo para GitHub Pages: {e}")
            raise
    
    def upload_video(self) -> Dict[str, Any]:
        """Fazer upload do vídeo para o TikTok"""
        try:
            logger.info(f"Iniciando upload do vídeo: {self.video_path}")
            
            # Passo 1: Inicializar o upload
            init_url = f"{self.base_url}/v2/post/publish/video/init/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            init_data = {
                "post_info": {
                    "title": self.video_title,
                    "description": self.video_description,
                    "privacy_level": self.privacy_level,
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": os.path.getsize(self.video_path),
                    "chunk_size": 10000000,  # 10MB chunks
                    "total_chunk_count": 1
                }
            }
            
            response = requests.post(init_url, headers=headers, json=init_data)
            
            if response.status_code != 200:
                logger.error(f"Erro ao inicializar upload: {response.status_code} - {response.text}")
                return {"status": "error", "message": "Falha ao inicializar upload"}
            
            init_result = response.json()
            publish_id = init_result["data"]["publish_id"]
            upload_url = init_result["data"]["upload_url"]
            
            logger.info(f"Upload inicializado. Publish ID: {publish_id}")
            
            # Passo 2: Upload do arquivo
            with open(self.video_path, 'rb') as video_file:
                files = {'video': video_file}
                upload_response = requests.put(upload_url, files=files)
                
                if upload_response.status_code != 200:
                    logger.error(f"Erro no upload do arquivo: {upload_response.status_code}")
                    return {"status": "error", "message": "Falha no upload do arquivo"}
            
            logger.info("Arquivo enviado com sucesso")
            
            # Passo 3: Confirmar o upload
            confirm_url = f"{self.base_url}/v2/post/publish/status/fetch/"
            confirm_params = {"publish_id": publish_id}
            
            confirm_response = requests.post(confirm_url, headers=headers, params=confirm_params)
            
            if confirm_response.status_code == 200:
                confirm_result = confirm_response.json()
                return {
                    "status": "success",
                    "message": "Vídeo enviado com sucesso para o TikTok",
                    "data": {
                        "publish_id": publish_id,
                        "status": confirm_result.get("data", {}).get("status", "unknown"),
                        "video_id": confirm_result.get("data", {}).get("video_id", ""),
                        "share_url": confirm_result.get("data", {}).get("share_url", "")
                    }
                }
            else:
                logger.error(f"Erro ao confirmar upload: {confirm_response.status_code}")
                return {"status": "error", "message": "Falha ao confirmar upload"}
                
        except Exception as e:
            logger.error(f"Erro no upload do vídeo: {e}")
            return {"status": "error", "message": str(e)}
    
    def run(self, video_path: str = None, video_url: str = None, image_path: str = None, image_url: str = None) -> Dict[str, Any]:
        """
        Executar upload do vídeo ou imagem no TikTok
        
        Args:
            video_path: Caminho local do vídeo (opcional)
            video_url: URL do vídeo no GitHub Pages (opcional)
            image_path: Caminho local da imagem (opcional - será convertida em vídeo curto)
            image_url: URL da imagem no GitHub Pages (opcional - será convertida em vídeo curto)
        """
        try:
            logger.info("Executando upload no TikTok...")
            
            # Obter informações do usuário
            user_info = self.get_user_info()
            if user_info and "data" in user_info:
                logger.info(f"Usuário conectado: {user_info['data'].get('display_name', 'N/A')}")
            
            # Se foi fornecida uma imagem, converter para vídeo curto primeiro
            if image_path or image_url:
                logger.info("Imagem detectada. Convertendo em vídeo curto para TikTok...")
                if image_path:
                    # Resolver caminho absoluto caso seja relativo
                    if not os.path.isabs(image_path):
                        # Tentar caminhos relativos comuns
                        base_paths = [
                            os.getcwd(),  # Diretório atual
                            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # Raiz do projeto
                        ]
                        found = False
                        for base in base_paths:
                            full_path = os.path.join(base, image_path)
                            if os.path.exists(full_path):
                                image_path = full_path
                                found = True
                                logger.info(f"Arquivo encontrado em: {full_path}")
                                break
                        if not found:
                            logger.warning(f"Arquivo não encontrado: {image_path}")
                            raise Exception(f"Arquivo de imagem não encontrado: {image_path}")
                    elif not os.path.exists(image_path):
                        logger.warning(f"Arquivo não encontrado: {image_path}")
                        raise Exception(f"Arquivo de imagem não encontrado: {image_path}")
                    
                    # Verificar se realmente é um arquivo de imagem
                    if not os.path.isfile(image_path):
                        raise Exception(f"Caminho não é um arquivo: {image_path}")
                    
                    logger.info(f"Usando imagem: {image_path} (tamanho: {os.path.getsize(image_path) / 1024:.2f} KB)")
                    # Converter imagem local em vídeo curto
                    short_video_path = self.convert_image_to_short_video(image_path)
                    video_path = short_video_path
                    logger.info(f"Imagem convertida em vídeo curto: {short_video_path}")
                elif image_url:
                    # Baixar imagem da URL, converter
                    logger.info(f"Baixando imagem de: {image_url}")
                    temp_dir = tempfile.mkdtemp()
                    temp_image_path = os.path.join(temp_dir, "downloaded_image.jpg")
                    
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        with open(temp_image_path, 'wb') as f:
                            f.write(img_response.content)
                        logger.info(f"Imagem baixada. Convertendo em vídeo curto...")
                        short_video_path = self.convert_image_to_short_video(temp_image_path)
                        video_path = short_video_path
                    else:
                        raise Exception(f"Erro ao baixar imagem: {img_response.status_code}")
                else:
                    raise Exception("Caminho ou URL da imagem inválido")
            
            # Se foi fornecida uma URL de vídeo diretamente (já está no GitHub Pages)
            if video_url:
                logger.info(f"Usando vídeo já hospedado no GitHub Pages: {video_url}")
                upload_result = self.upload_video_via_url(video_url)
                return upload_result
            
            # Se foi fornecido um caminho de vídeo local, usar ele
            if video_path:
                self.video_path = video_path
                logger.info(f"Usando vídeo fornecido: {video_path}")
            elif self.video_path and os.path.exists(self.video_path):
                logger.info(f"Usando vídeo configurado: {self.video_path}")
            else:
                raise Exception("Nenhum vídeo ou imagem fornecido. Forneça video_path, video_url, image_path ou image_url")
            
            # Verificar se o arquivo existe
            if not os.path.exists(self.video_path):
                raise Exception(f"Vídeo não encontrado: {self.video_path}")
            
            # No modo Sandbox, sempre usar PULL_FROM_URL com GitHub Pages
            if self.use_github_pages:
                logger.info(f"Modo Sandbox detectado - usando GitHub Pages ({self.github_pages_url}) para hospedar o vídeo...")
                
                # Preparar vídeo para GitHub Pages
                github_pages_url = self.prepare_video_for_github_pages(self.video_path)
                logger.info(f"URL do vídeo no GitHub Pages: {github_pages_url}")
                
                # Usar PULL_FROM_URL com GitHub Pages
                upload_result = self.upload_video_via_url(github_pages_url)
            else:
                # Upload tradicional via FILE_UPLOAD (pode não funcionar no Sandbox)
                logger.warning("⚠️ GitHub Pages não está configurado. Tentando FILE_UPLOAD (pode falhar no Sandbox)...")
                upload_result = self.upload_video()
            
            if upload_result["status"] == "success":
                logger.info("Upload concluído com sucesso!")
                return upload_result
            else:
                logger.error(f"Falha no upload: {upload_result['message']}")
                return upload_result
            
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
            logger.info("Limpando recursos do TikTok...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza do TikTok concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = TikTokUploadPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração do TikTok")
            return
        
        # Verificar se há argumentos na linha de comando
        import sys
        video_path = None
        video_url = None
        image_path = None
        image_url = None
        
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            
            # Verificar se é URL
            if arg.startswith('http://') or arg.startswith('https://'):
                # É uma URL
                # Verificar se é imagem ou vídeo pela extensão na URL
                url_lower = arg.lower()
                if url_lower.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    image_url = arg
                    logger.info(f"🌐 Usando URL de imagem: {image_url}")
                else:
                    video_url = arg
                    logger.info(f"🌐 Usando URL de vídeo: {video_url}")
            else:
                # É um caminho local
                # Verificar se é imagem ou vídeo pela extensão
                ext = os.path.splitext(arg)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                    image_path = arg
                    logger.info(f"📁 Usando imagem local: {image_path}")
                else:
                    video_path = arg
                    logger.info(f"📁 Usando vídeo local: {video_path}")
        
        result = poc.run(video_path=video_path, video_url=video_url, image_path=image_path, image_url=image_url)
        
        print(f"\nResultado da POC - TikTok Upload:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            print(f"\nDetalhes do upload:")
            print(f"  Publish ID: {result['data'].get('publish_id', 'N/A')}")
            print(f"  Status: {result['data'].get('status', 'N/A')}")
            print(f"  Video ID: {result['data'].get('video_id', 'N/A')}")
            print(f"  URL de compartilhamento: {result['data'].get('share_url', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
