#!/usr/bin/env python3
"""
POC - Coleta de Métricas de Redes Sociais
Descrição: POC para coletar métricas de posts publicados
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import requests
import logging
from typing import Any, Dict, List
from datetime import datetime
from pocs.template_poc import POCTemplate

# Configurar logging
logger = logging.getLogger(__name__)


class SocialMetricsPOC(POCTemplate):
    """POC para coleta de métricas de redes sociais"""
    
    def __init__(self):
        """Inicializar coletor de métricas"""
        super().__init__()
        self.name = "Social Metrics Collection POC"
        
        # Tokens de acesso
        self.tiktok_token = None
        self.instagram_token = None
        self.linkedin_token = None
        
        # URLs base das APIs
        self.tiktok_base = "https://open.tiktokapis.com"
        self.instagram_base = "https://graph.facebook.com/v18.0"
        self.linkedin_base = "https://api.linkedin.com/v2"
    
    def setup(self) -> bool:
        """Configurar tokens de acesso"""
        try:
            logger.info("Configurando coletor de métricas...")
            
            # Carregar tokens do ambiente
            self.tiktok_token = os.getenv('TIKTOK_ACCESS_TOKEN')
            self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
            self.linkedin_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
            
            if not any([self.tiktok_token, self.instagram_token, self.linkedin_token]):
                logger.warning("Nenhum token de rede social encontrado")
                return False
            
            logger.info("Configuração de métricas concluída")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração: {e}")
            return False
    
    def get_tiktok_metrics(self, video_id: str) -> Dict[str, Any]:
        """Obter métricas de vídeo do TikTok"""
        try:
            if not self.tiktok_token:
                return {"status": "error", "message": "Token TikTok não configurado"}
            
            logger.info(f"Coletando métricas do TikTok para vídeo: {video_id}")
            
            url = f"{self.tiktok_base}/v2/video/info/"
            headers = {
                "Authorization": f"Bearer {self.tiktok_token}",
                "Content-Type": "application/json"
            }
            params = {
                "fields": "id,title,cover_image_url,embed_url,like_count,comment_count,share_count,view_count,create_time"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "platform": "tiktok",
                    "data": {
                        "video_id": video_id,
                        "likes": data.get("data", {}).get("like_count", 0),
                        "comments": data.get("data", {}).get("comment_count", 0),
                        "shares": data.get("data", {}).get("share_count", 0),
                        "views": data.get("data", {}).get("view_count", 0),
                        "created_time": data.get("data", {}).get("create_time", ""),
                        "title": data.get("data", {}).get("title", ""),
                        "embed_url": data.get("data", {}).get("embed_url", "")
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro na API TikTok: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do TikTok: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_instagram_metrics(self, media_id: str) -> Dict[str, Any]:
        """Obter métricas de post do Instagram"""
        try:
            if not self.instagram_token:
                return {"status": "error", "message": "Token Instagram não configurado"}
            
            logger.info(f"Coletando métricas do Instagram para post: {media_id}")
            
            url = f"{self.instagram_base}/{media_id}"
            params = {
                "fields": "id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count",
                "access_token": self.instagram_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "platform": "instagram",
                    "data": {
                        "media_id": media_id,
                        "likes": data.get("like_count", 0),
                        "comments": data.get("comments_count", 0),
                        "shares": 0,  # Instagram não expõe shares via API
                        "views": 0,   # Instagram não expõe views via API
                        "created_time": data.get("timestamp", ""),
                        "caption": data.get("caption", ""),
                        "media_url": data.get("media_url", ""),
                        "permalink": data.get("permalink", "")
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro na API Instagram: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do Instagram: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_linkedin_metrics(self, post_id: str) -> Dict[str, Any]:
        """Obter métricas de post do LinkedIn"""
        try:
            if not self.linkedin_token:
                return {"status": "error", "message": "Token LinkedIn não configurado"}
            
            logger.info(f"Coletando métricas do LinkedIn para post: {post_id}")
            
            # LinkedIn usa URN format
            url = f"{self.linkedin_base}/socialActions/{post_id}"
            headers = {
                "Authorization": f"Bearer {self.linkedin_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "platform": "linkedin",
                    "data": {
                        "post_id": post_id,
                        "likes": data.get("numLikes", 0),
                        "comments": data.get("numComments", 0),
                        "shares": data.get("numShares", 0),
                        "views": 0,  # LinkedIn não expõe views via API
                        "created_time": data.get("created", {}).get("time", ""),
                        "text": data.get("text", {}).get("text", ""),
                        "permalink": data.get("permalink", "")
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro na API LinkedIn: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do LinkedIn: {e}")
            return {"status": "error", "message": str(e)}
    
    def collect_all_metrics(self, posts: List[Dict[str, str]]) -> Dict[str, Any]:
        """Coletar métricas de múltiplos posts"""
        try:
            logger.info(f"Coletando métricas de {len(posts)} posts...")
            
            results = []
            total_metrics = {
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_views": 0,
                "platforms": {}
            }
            
            for post in posts:
                platform = post.get("platform", "").lower()
                post_id = post.get("post_id", "")
                
                if platform == "tiktok":
                    metrics = self.get_tiktok_metrics(post_id)
                elif platform == "instagram":
                    metrics = self.get_instagram_metrics(post_id)
                elif platform == "linkedin":
                    metrics = self.get_linkedin_metrics(post_id)
                else:
                    metrics = {"status": "error", "message": f"Plataforma não suportada: {platform}"}
                
                if metrics["status"] == "success":
                    data = metrics["data"]
                    results.append(metrics)
                    
                    # Somar métricas totais
                    total_metrics["total_likes"] += data.get("likes", 0)
                    total_metrics["total_comments"] += data.get("comments", 0)
                    total_metrics["total_shares"] += data.get("shares", 0)
                    total_metrics["total_views"] += data.get("views", 0)
                    
                    # Métricas por plataforma
                    if platform not in total_metrics["platforms"]:
                        total_metrics["platforms"][platform] = {
                            "likes": 0, "comments": 0, "shares": 0, "views": 0, "posts": 0
                        }
                    
                    total_metrics["platforms"][platform]["likes"] += data.get("likes", 0)
                    total_metrics["platforms"][platform]["comments"] += data.get("comments", 0)
                    total_metrics["platforms"][platform]["shares"] += data.get("shares", 0)
                    total_metrics["platforms"][platform]["views"] += data.get("views", 0)
                    total_metrics["platforms"][platform]["posts"] += 1
                else:
                    results.append(metrics)
            
            return {
                "status": "success",
                "message": f"Métricas coletadas de {len(results)} posts",
                "data": {
                    "individual_metrics": results,
                    "total_metrics": total_metrics,
                    "collection_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na coleta de métricas: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def run(self) -> Dict[str, Any]:
        """Executar coleta de métricas de exemplo"""
        try:
            logger.info("Executando coleta de métricas de exemplo...")
            
            # Posts de exemplo (você substituiria pelos IDs reais)
            example_posts = [
                {"platform": "tiktok", "post_id": "example_tiktok_id"},
                {"platform": "instagram", "post_id": "example_instagram_id"},
                {"platform": "linkedin", "post_id": "example_linkedin_id"}
            ]
            
            # Coletar métricas
            result = self.collect_all_metrics(example_posts)
            
            logger.info("Coleta de métricas concluída")
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
            logger.info("Limpando recursos de métricas...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza de métricas concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = SocialMetricsPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração de métricas")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - Coleta de Métricas:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            total = result['data'].get('total_metrics', {})
            print(f"\nMétricas Totais:")
            print(f"  Total de Likes: {total.get('total_likes', 0)}")
            print(f"  Total de Comentários: {total.get('total_comments', 0)}")
            print(f"  Total de Compartilhamentos: {total.get('total_shares', 0)}")
            print(f"  Total de Visualizações: {total.get('total_views', 0)}")
            
            print(f"\nPor Plataforma:")
            for platform, metrics in total.get('platforms', {}).items():
                print(f"  {platform.upper()}:")
                print(f"    Posts: {metrics.get('posts', 0)}")
                print(f"    Likes: {metrics.get('likes', 0)}")
                print(f"    Comentários: {metrics.get('comments', 0)}")
                print(f"    Compartilhamentos: {metrics.get('shares', 0)}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
