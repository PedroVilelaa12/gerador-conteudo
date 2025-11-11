#!/usr/bin/env python3
"""
LinkedIn POC - Publicação de Posts
Descrição: POC para fazer publicação automática de posts no LinkedIn
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import requests
import json
import logging
from typing import Any, Dict, Optional
from pocs.template_poc import POCTemplate

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInUploadPOC(POCTemplate):
    """POC para publicação de posts no LinkedIn"""
    
    def __init__(self):
        """Inicializar publisher do LinkedIn"""
        super().__init__()
        self.name = "LinkedIn Upload POC"
        self.access_token = None
        self.person_urn = None  # URN do perfil ou página
        self.base_url = "https://api.linkedin.com/v2"
        
        # Configurações do post
        self.post_text = "Teste de publicação automática via API do LinkedIn 🚀"
        self.image_url = None
        self.visibility = "PUBLIC"  # PUBLIC, CONNECTIONS, PRIVATE
    
    def setup(self) -> bool:
        """Configurar conexão com LinkedIn API"""
        try:
            logger.info("Configurando conexão com LinkedIn API...")
            
            # Carregar credenciais do ambiente
            self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
            
            if not self.access_token:
                logger.error("LINKEDIN_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
                return False
            
            # Obter URN do perfil/usuário
            self.person_urn = self.get_person_urn()
            
            if not self.person_urn:
                logger.warning("Não foi possível obter URN do perfil. Algumas funcionalidades podem não funcionar.")
                # Ainda pode tentar publicar com URN manual
                self.person_urn = os.getenv('LINKEDIN_PERSON_URN')
            
            logger.info("Configuração do LinkedIn concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do LinkedIn: {e}")
            return False
    
    def get_person_urn(self) -> Optional[str]:
        """Obter URN do perfil do usuário"""
        try:
            # Método 1: Tentar via OpenID Connect /userinfo
            url_userinfo = f"{self.base_url}/userinfo"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url_userinfo, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # LinkedIn OpenID Connect retorna 'sub' com formato diferente
                sub = data.get("sub", "")
                if sub:
                    # O 'sub' pode já vir como URN ou como ID
                    if sub.startswith("urn:li:person:"):
                        logger.info(f"URN obtido via /userinfo: {sub}")
                        return sub
                    else:
                        # Se for só o ID, formar o URN
                        urn = f"urn:li:person:{sub}"
                        logger.info(f"URN formado via /userinfo: {urn}")
                        return urn
                
                # Fallback: tentar obter de outras formas
                person_id = data.get("id", "")
                if person_id:
                    urn = f"urn:li:person:{person_id}"
                    logger.info(f"URN formado via ID: {urn}")
                    return urn
            
            # Método 2: Tentar via endpoint /me (LinkedIn v2)
            logger.info("Tentando obter URN via endpoint /me...")
            url_me = f"{self.base_url}/me"
            params = {
                "projection": "(id)"
            }
            
            response_me = requests.get(url_me, headers=headers, params=params)
            
            if response_me.status_code == 200:
                data_me = response_me.json()
                person_id = data_me.get("id", "")
                if person_id:
                    urn = f"urn:li:person:{person_id}"
                    logger.info(f"URN obtido via /me: {urn}")
                    return urn
            
            # Método 3: Verificar se está configurado manualmente no .env
            manual_urn = os.getenv('LINKEDIN_PERSON_URN')
            if manual_urn:
                logger.info(f"URN obtido do .env: {manual_urn}")
                return manual_urn
            
            # Se nenhum método funcionou
            logger.warning(f"Não foi possível obter URN do perfil.")
            logger.warning(f"Tentativa /userinfo: {response.status_code}")
            if 'response_me' in locals():
                logger.warning(f"Tentativa /me: {response_me.status_code}")
            return None
                
        except Exception as e:
            logger.error(f"Erro ao obter URN do perfil: {e}")
            # Tentar usar URN manual do .env como último recurso
            manual_urn = os.getenv('LINKEDIN_PERSON_URN')
            if manual_urn:
                logger.info(f"Usando URN do .env como fallback: {manual_urn}")
                return manual_urn
            return None
    
    def create_text_post(self, text: str, visibility: str = None) -> Dict[str, Any]:
        """Criar post de texto simples"""
        try:
            logger.info("Criando post de texto no LinkedIn...")
            
            visibility = visibility or self.visibility
            
            url = f"{self.base_url}/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Verificar se temos URN válido
            author_urn = self.person_urn
            if not author_urn:
                # Tentar obter novamente
                author_urn = self.get_person_urn()
            
            if not author_urn:
                # Última tentativa: usar do .env ou erro
                author_urn = os.getenv('LINKEDIN_PERSON_URN') or os.getenv('LINKEDIN_PERSON_ID')
                if author_urn and not author_urn.startswith("urn:li:person:"):
                    author_urn = f"urn:li:person:{author_urn}"
            
            if not author_urn:
                error_msg = (
                    "Não foi possível obter o URN do perfil. "
                    "Configure LINKEDIN_PERSON_URN no arquivo .env com o formato: urn:li:person:SEU_ID"
                )
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "data": {}
                }
            
            # Construir o payload para post de texto
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            response = requests.post(url, headers=headers, json=post_data)
            
            if response.status_code == 201:
                result = response.json()
                post_id = result.get("id", "")
                logger.info(f"Post criado com sucesso: {post_id}")
                return {
                    "status": "success",
                    "message": "Post publicado com sucesso no LinkedIn",
                    "data": {
                        "post_id": post_id,
                        "post_urn": post_id,
                        "text": text,
                        "visibility": visibility
                    }
                }
            else:
                error_response = response.text
                logger.error(f"Erro ao criar post: {response.status_code} - {error_response}")
                
                # Parse do erro para mensagem mais clara
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message", "") or error_json.get("serviceErrorCode", "")
                    if "author" in error_response.lower():
                        error_msg = (
                            f"Erro na API LinkedIn: URN do autor inválido. "
                            f"Status: {response.status_code}. "
                            f"Configure LINKEDIN_PERSON_URN no .env ou adicione escopos 'openid profile' ao token."
                        )
                    else:
                        error_msg = f"Erro na API LinkedIn: {response.status_code} - {error_detail}"
                except:
                    error_msg = f"Erro na API LinkedIn: {response.status_code} - {error_response[:200]}"
                
                return {
                    "status": "error",
                    "message": error_msg,
                    "data": {}
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar post de texto: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def create_image_post(self, text: str, image_url: str, visibility: str = None) -> Dict[str, Any]:
        """Criar post com imagem"""
        try:
            logger.info("Criando post com imagem no LinkedIn...")
            
            visibility = visibility or self.visibility
            
            # Passo 1: Registrar upload da imagem
            register_upload_url = f"{self.base_url}/assets?action=registerUpload"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Obter URN válido (mesma lógica do create_text_post)
            author_urn = self.person_urn or self.get_person_urn()
            if not author_urn:
                author_urn = os.getenv('LINKEDIN_PERSON_URN') or os.getenv('LINKEDIN_PERSON_ID')
                if author_urn and not author_urn.startswith("urn:li:person:"):
                    author_urn = f"urn:li:person:{author_urn}"
            
            if not author_urn:
                logger.error("URN do autor não encontrado para upload de imagem")
                return self.create_text_post(text, visibility)
            
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": author_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            register_response = requests.post(register_upload_url, headers=headers, json=register_data)
            
            if register_response.status_code != 200:
                logger.error(f"Erro ao registrar upload: {register_response.status_code}")
                # Fallback para post de texto apenas
                return self.create_text_post(text, visibility)
            
            upload_data = register_response.json()
            upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_urn = upload_data["value"]["asset"]
            
            # Passo 2: Fazer upload real da imagem
            image_data = None
            
            # Se image_url for um caminho de arquivo local
            if image_url and (os.path.exists(image_url) or image_url.startswith('file://')):
                try:
                    file_path = image_url.replace('file://', '') if image_url.startswith('file://') else image_url
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            image_data = f.read()
                        logger.info(f"Imagem carregada do arquivo local: {file_path}")
                    else:
                        logger.warning(f"Arquivo não encontrado: {file_path}")
                except Exception as e:
                    logger.error(f"Erro ao ler arquivo local: {e}")
            
            # Se image_url for uma URL HTTP/HTTPS
            elif image_url and (image_url.startswith('http://') or image_url.startswith('https://')):
                try:
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        image_data = img_response.content
                        logger.info(f"Imagem baixada da URL: {image_url}")
                    else:
                        logger.warning(f"Erro ao baixar imagem: {img_response.status_code}")
                except Exception as e:
                    logger.error(f"Erro ao baixar imagem da URL: {e}")
            
            # Se não conseguiu obter a imagem, criar post de texto
            if not image_data:
                logger.warning("Não foi possível obter a imagem. Criando post de texto com referência à imagem.")
                return self.create_text_post(f"{text}\n\nImagem: {image_url}", visibility)
            
            # Fazer upload da imagem para o LinkedIn
            try:
                upload_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                
                upload_response = requests.put(upload_url, headers=upload_headers, data=image_data, timeout=60)
                
                if upload_response.status_code not in [200, 201, 204]:
                    logger.error(f"Erro no upload da imagem: {upload_response.status_code} - {upload_response.text}")
                    logger.warning("Tentando criar post de texto como fallback...")
                    return self.create_text_post(text, visibility)
                
                logger.info("Upload da imagem concluído com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fazer upload da imagem: {e}")
                logger.warning("Tentando criar post de texto como fallback...")
                return self.create_text_post(text, visibility)
            
            # Passo 3: Criar post com referência à imagem
            url = f"{self.base_url}/ugcPosts"
            headers_post = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Garantir que temos URN válido
            if not author_urn:
                author_urn = self.person_urn or self.get_person_urn()
                if not author_urn:
                    author_urn = os.getenv('LINKEDIN_PERSON_URN') or os.getenv('LINKEDIN_PERSON_ID')
                    if author_urn and not author_urn.startswith("urn:li:person:"):
                        author_urn = f"urn:li:person:{author_urn}"
            
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "media": asset_urn
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            response = requests.post(url, headers=headers_post, json=post_data)
            
            if response.status_code == 201:
                result = response.json()
                post_id = result.get("id", "")
                logger.info(f"Post com imagem criado com sucesso: {post_id}")
                return {
                    "status": "success",
                    "message": "Post com imagem publicado no LinkedIn",
                    "data": {
                        "post_id": post_id,
                        "post_urn": post_id,
                        "text": text,
                        "image_url": image_url,
                        "visibility": visibility
                    }
                }
            else:
                # Fallback para post de texto
                logger.warning(f"Erro ao criar post com imagem: {response.status_code}. Tentando post de texto...")
                return self.create_text_post(text, visibility)
                
        except Exception as e:
            logger.error(f"Erro ao criar post com imagem: {e}")
            # Fallback para post de texto
            return self.create_text_post(text, visibility)
    
    def publish_post(self, text: str, image_url: str = None, visibility: str = None) -> Dict[str, Any]:
        """Publicar post (texto ou com imagem)"""
        try:
            if image_url:
                return self.create_image_post(text, image_url, visibility)
            else:
                return self.create_text_post(text, visibility)
                
        except Exception as e:
            logger.error(f"Erro ao publicar post: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def run(self, text: str = None, image_url: str = None) -> Dict[str, Any]:
        """Executar publicação no LinkedIn"""
        try:
            logger.info("Executando publicação no LinkedIn...")
            
            # Usar texto fornecido ou padrão
            post_text = text or self.post_text
            post_image = image_url or self.image_url
            
            # Publicar post
            result = self.publish_post(post_text, post_image)
            
            if result["status"] == "success":
                logger.info("Publicação concluída com sucesso!")
                return result
            else:
                logger.error(f"Falha na publicação: {result['message']}")
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
            logger.info("Limpando recursos do LinkedIn...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza do LinkedIn concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = LinkedInUploadPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração do LinkedIn")
            return
        
        # Exemplo de uso
        result = poc.run()
        
        print(f"\nResultado da POC - LinkedIn Upload:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            print(f"\nDetalhes da publicação:")
            print(f"  Post ID: {result['data'].get('post_id', 'N/A')}")
            print(f"  Texto: {result['data'].get('text', 'N/A')}")
            print(f"  Visibilidade: {result['data'].get('visibility', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()


