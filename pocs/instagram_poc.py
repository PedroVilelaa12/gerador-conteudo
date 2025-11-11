#!/usr/bin/env python3
"""
Instagram POC - Upload de Vídeo
Descrição: POC para fazer upload automático de vídeos no Instagram
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import requests
import json
import time
import logging
from typing import Any, Dict
from pocs.template_poc import POCTemplate

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InstagramUploadPOC(POCTemplate):
    """POC para upload de vídeos no Instagram"""
    
    def __init__(self):
        """Inicializar uploader do Instagram"""
        super().__init__()
        self.name = "Instagram Upload POC"
        self.access_token = None
        self.instagram_account_id = None
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Configurações padrão
        self.media_caption = os.getenv("INSTAGRAM_MEDIA_CAPTION", "Teste de upload automático via API do Instagram 🚀 #teste #api")
        self.default_media_type = os.getenv("INSTAGRAM_MEDIA_TYPE", "VIDEO").upper()
        self.default_video_url = os.getenv('INSTAGRAM_VIDEO_URL')
        self.default_image_url = os.getenv('INSTAGRAM_IMAGE_URL')
    
    def setup(self) -> bool:
        """Configurar conexão com Instagram API"""
        try:
            logger.info("Configurando conexão com Instagram API...")
            
            # Carregar credenciais do ambiente
            self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
            self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
            
            if not self.access_token:
                logger.error("INSTAGRAM_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
                return False
            
            if not self.instagram_account_id:
                logger.error("INSTAGRAM_ACCOUNT_ID não encontrado nas variáveis de ambiente")
                return False
            
            logger.info("Configuração do Instagram concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do Instagram: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Obter informações da conta do Instagram"""
        try:
            url = f"{self.base_url}/{self.instagram_account_id}"
            params = {
                "fields": "username,name,profile_picture_url,followers_count",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter info da conta: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao obter informações da conta: {e}")
            return {}
    
    def create_media_container(self, media_url: str, media_type: str, caption: str) -> str:
        """Criar container de mídia para o Instagram"""
        try:
            logger.info("Criando container de mídia...")
            
            url = f"{self.base_url}/{self.instagram_account_id}/media"
            
            data = {
                "access_token": self.access_token,
                "caption": caption or self.media_caption
            }

            if media_type == "VIDEO":
                data.update({
                    "media_type": "REELS",
                    "video_url": media_url,
                })
            else:
                data.update({
                    "image_url": media_url,
                })
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                container_id = result.get("id")
                logger.info(f"Container criado com sucesso: {container_id}")
                return container_id
            else:
                logger.error(f"Erro ao criar container: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar container de mídia: {e}")
            return None
    
    def check_container_status(self, container_id: str) -> Dict[str, Any]:
        """Verificar status do container de mídia"""
        try:
            url = f"{self.base_url}/{container_id}"
            params = {
                "fields": "status_code,status",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao verificar status: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao verificar status do container: {e}")
            return {}
    
    def publish_media(self, container_id: str) -> Dict[str, Any]:
        """Publicar o vídeo no Instagram"""
        try:
            logger.info("Publicando mídia...")
            
            url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
            
            data = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                media_id = result.get("id")
                logger.info(f"Mídia publicada com sucesso: {media_id}")
                return {"status": "success", "media_id": media_id}
            else:
                logger.error(f"Erro ao publicar: {response.status_code} - {response.text}")
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            logger.error(f"Erro ao publicar media: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_media_info(self, media_id: str) -> Dict[str, Any]:
        """Obter informações do vídeo publicado"""
        try:
            url = f"{self.base_url}/{media_id}"
            params = {
                "fields": "id,media_type,media_url,permalink,caption,timestamp",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao obter info do vídeo: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do vídeo: {e}")
            return {}
    
    def upload_media(self, media_url: str, media_type: str, caption: str) -> Dict[str, Any]:
        """Processo completo de upload da mídia"""
        try:
            # Passo 1: Criar container de mídia
            container_id = self.create_media_container(media_url, media_type, caption)
            if not container_id:
                return {"status": "error", "message": "Falha ao criar container de mídia"}
            
            # Passo 2: Aguardar processamento da mídia
            logger.info("Aguardando processamento da mídia...")
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                status_info = self.check_container_status(container_id)
                status_code = status_info.get("status_code")
                status = status_info.get("status")

                if status_code == "FINISHED":
                    logger.info("Processamento concluído com sucesso")
                    break
                elif status_code == "ERROR":
                    error_message = status_info.get("status", "Erro no processamento da mídia")
                    logger.error(f"Erro no processamento da mídia: {error_message}")
                    return {"status": "error", "message": error_message}
                elif status_code == "IN_PROGRESS":
                    logger.info(f"Processamento em andamento ({status})... (tentativa {attempt + 1}/{max_attempts})")
                    time.sleep(10)  # Aguardar 10 segundos
                    attempt += 1
                else:
                    logger.info(f"Status: {status_code or status}, aguardando...")
                    time.sleep(5)
                    attempt += 1
            
            if attempt >= max_attempts:
                return {"status": "error", "message": "Timeout no processamento da mídia"}
            
            # Passo 3: Publicar a mídia
            publish_result = self.publish_media(container_id)
            
            if publish_result["status"] == "success":
                media_id = publish_result["media_id"]
                
                # Obter informações da mídia publicada
                media_info = self.get_media_info(media_id)
                
                return {
                    "status": "success",
                    "message": "Mídia enviada com sucesso para o Instagram",
                    "data": {
                        "container_id": container_id,
                        "media_id": media_id,
                        "permalink": media_info.get("permalink", ""),
                        "media_url": media_info.get("media_url", ""),
                        "timestamp": media_info.get("timestamp", "")
                    }
                }
            else:
                return publish_result
                
        except Exception as e:
            logger.error(f"Erro no upload do vídeo: {e}")
            return {"status": "error", "message": str(e)}
    
    def run(self, media_url: str = None, media_type: str = None, caption: str = None) -> Dict[str, Any]:
        """Executar upload no Instagram"""
        try:
            logger.info("Executando upload no Instagram...")
            
            # Obter informações da conta
            account_info = self.get_account_info()
            if account_info:
                logger.info(f"Conta conectada: @{account_info.get('username', 'N/A')}")
            
            resolved_media_type = (media_type or self.default_media_type or "VIDEO").upper()
            if resolved_media_type not in {"VIDEO", "IMAGE"}:
                resolved_media_type = "VIDEO"
            
            resolved_media_url = media_url
            if not resolved_media_url:
                if resolved_media_type == "VIDEO":
                    resolved_media_url = self.default_video_url
                else:
                    resolved_media_url = self.default_image_url
            
            if not resolved_media_url:
                return {"status": "error", "message": "URL pública da mídia não informada e não configurada no .env"}
            
            resolved_caption = caption or self.media_caption
            
            upload_result = self.upload_media(resolved_media_url, resolved_media_type, resolved_caption)
            
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
            logger.info("Limpando recursos do Instagram...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza do Instagram concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = InstagramUploadPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração do Instagram")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - Instagram Upload:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            print(f"\nDetalhes do upload:")
            print(f"  Container ID: {result['data'].get('container_id', 'N/A')}")
            print(f"  Media ID: {result['data'].get('media_id', 'N/A')}")
            print(f"  Permalink: {result['data'].get('permalink', 'N/A')}")
            print(f"  Timestamp: {result['data'].get('timestamp', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
