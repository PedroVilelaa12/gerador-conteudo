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
        self.privacy_level = "SELF_ONLY"  # SELF_ONLY, MUTUAL_FOLLOW_FRIENDS, PUBLIC_TO_EVERYONE
    
    def setup(self) -> bool:
        """Configurar conexão com TikTok API"""
        try:
            logger.info("Configurando conexão com TikTok API...")
            
            # Carregar credenciais do ambiente
            self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
            self.open_id = os.getenv('TIKTOK_OPEN_ID')
            self.video_path = os.getenv('TEST_VIDEO_PATH', 'test_video.mp4')
            
            if not self.access_token:
                logger.error("TIKTOK_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
                return False
            
            if not self.open_id:
                logger.error("TIKTOK_OPEN_ID não encontrado nas variáveis de ambiente")
                return False
            
            # Verificar se o arquivo de vídeo existe
            if not os.path.exists(self.video_path):
                logger.error(f"Arquivo de vídeo não encontrado: {self.video_path}")
                return False
            
            logger.info("Configuração do TikTok concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do TikTok: {e}")
            return False
    
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
    
    def run(self) -> Dict[str, Any]:
        """Executar upload do vídeo no TikTok"""
        try:
            logger.info("Executando upload no TikTok...")
            
            # Obter informações do usuário
            user_info = self.get_user_info()
            if user_info and "data" in user_info:
                logger.info(f"Usuário conectado: {user_info['data'].get('display_name', 'N/A')}")
            
            # Fazer upload do vídeo
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
        
        result = poc.run()
        
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
