#!/usr/bin/env python3
"""
POC: Radar de Notícias (RSS Feeds)
Descrição: Buscar as 5 principais notícias de negócios do Brasil usando RSS feeds
Autor: [Seu nome]
Data: 2024
"""

import logging
import requests
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
import os
from datetime import datetime
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()


class RSSFeedsPOC:
    """POC para Radar de Notícias usando RSS Feeds brasileiros"""
    
    def __init__(self):
        """Inicializar a POC"""
        self.name = "Radar de Notícias RSS POC"
        self.max_noticias = 5
        
        # RSS Feeds de portais brasileiros
        self.rss_feeds = {
            "G1 Economia": "https://g1.globo.com/rss/g1/economia/",
            # "UOL Economia": "https://rss.uol.com.br/feed/economia.xml",
            # "Estadão Economia": "https://www.estadao.com.br/rss/economia.xml",
            # "Valor Econômico": "https://valor.globo.com/rss/",
            # "Agência Brasil": "https://agenciabrasil.ebc.com.br/rss/feed/economia"
        }
        
        logger.info(f"Iniciando {self.name}")
    
    def setup(self) -> bool:
        """Configurar ambiente e dependências"""
        try:
            logger.info("Configurando RSS Feeds...")
            
            # Testar se consegue acessar pelo menos um feed
            test_feed = list(self.rss_feeds.values())[0]
            response = requests.get(test_feed, timeout=10)
            
            if response.status_code == 200:
                logger.info("RSS Feeds configurados com sucesso")
                return True
            else:
                logger.error(f"Erro ao acessar RSS feed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na configuração: {e}")
            return False
    
    def buscar_noticias_rss(self, feed_url: str, portal_name: str) -> List[Dict[str, Any]]:
        """Buscar notícias de um RSS feed específico"""
        try:
            logger.info(f"Buscando notícias de {portal_name}...")
            
            # Fazer requisição para o RSS feed
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()
            
            # Parsear XML do RSS
            root = ET.fromstring(response.content)
            
            noticias = []
            
            # Procurar por diferentes formatos de RSS
            items = root.findall('.//item') or root.findall('.//entry')
            
            for item in items:
                try:
                    # Extrair informações da notícia
                    title = self._extrair_texto(item, ['title', 'name'])
                    link = self._extrair_texto(item, ['link', 'url'])
                    description = self._extrair_texto(item, ['description', 'summary', 'content'])
                    pub_date = self._extrair_texto(item, ['pubDate', 'published', 'updated'])
                    
                    # Formatar data se disponível
                    formatted_date = self._formatar_data(pub_date)
                    
                    if title:  # Só adicionar se tiver título
                        noticia = {
                            "title": title,
                            "link": link,
                            "description": description,
                            "published_at": formatted_date,
                            "source": portal_name,
                            "feed_url": feed_url
                        }
                        noticias.append(noticia)
                        
                except Exception as e:
                    logger.warning(f"Erro ao processar item do {portal_name}: {e}")
                    continue
            
            logger.info(f"Encontradas {len(noticias)} notícias em {portal_name}")
            return noticias
            
        except Exception as e:
            logger.error(f"Erro ao buscar RSS de {portal_name}: {e}")
            return []
    
    def _extrair_texto(self, element, tags: List[str]) -> str:
        """Extrair texto de diferentes tags possíveis"""
        for tag in tags:
            found = element.find(tag)
            if found is not None:
                text = found.text
                if text:
                    return text.strip()
        return ""
    
    def _formatar_data(self, date_str: str) -> str:
        """Formatar data do RSS para formato legível"""
        if not date_str:
            return "Data não disponível"
        
        try:
            # Tentar diferentes formatos de data
            date_formats = [
                "%a, %d %b %Y %H:%M:%S %z",  # RSS padrão
                "%Y-%m-%dT%H:%M:%SZ",        # ISO
                "%Y-%m-%dT%H:%M:%S%z",       # ISO com timezone
                "%d/%m/%Y %H:%M"             # Formato brasileiro
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    continue
            
            # Se nenhum formato funcionar, retornar original
            return date_str
            
        except Exception:
            return date_str
    
    def buscar_todas_noticias(self) -> List[Dict[str, Any]]:
        """Buscar notícias de todos os RSS feeds"""
        todas_noticias = []
        
        for portal_name, feed_url in self.rss_feeds.items():
            try:
                logger.info(f"🔍 Consultando {portal_name}...")
                noticias = self.buscar_noticias_rss(feed_url, portal_name)
                
                if noticias:
                    logger.info(f"✅ {len(noticias)} notícias encontradas em {portal_name}")
                    todas_noticias.extend(noticias)
                else:
                    logger.warning(f"⚠️  Nenhuma notícia encontrada em {portal_name}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao buscar {portal_name}: {e}")
                continue
        
        logger.info(f"📊 Total de notícias coletadas: {len(todas_noticias)}")
        
        # Ordenar por data (mais recentes primeiro) - SEM LIMITE
        if todas_noticias:
            todas_noticias.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            logger.info(f"🎯 Retornando TODAS as {len(todas_noticias)} notícias encontradas")
            return todas_noticias  # Retorna todas, sem limite
        else:
            logger.warning("⚠️  Nenhuma notícia encontrada em nenhum feed")
            return []
    
    def exibir_noticias(self, noticias: List[Dict[str, Any]]) -> None:
        """Exibir notícias no terminal"""
        if not noticias:
            print("❌ Nenhuma notícia encontrada")
            return
        
        print(f"\n📰 TOP {len(noticias)} NOTÍCIAS DE NEGÓCIOS - BRASIL (RSS)")
        print("=" * 70)
        
        for i, noticia in enumerate(noticias, 1):
            title = noticia.get("title", "Título não disponível")
            source = noticia.get("source", "Fonte não disponível")
            published_at = noticia.get("published_at", "Data não disponível")
            link = noticia.get("link", "")
            description = noticia.get("description", "")
            
            print(f"\n{i}. {title}")
            print(f"   📍 Fonte: {source}")
            print(f"   📅 Publicado: {published_at}")
            
            if link:
                print(f"   🔗 Link: {link}")
            
            if description:
                # Limitar descrição para não ficar muito longa
                desc_limpa = description.replace('\n', ' ').strip()
                if len(desc_limpa) > 150:
                    desc_limpa = desc_limpa[:150] + "..."
                print(f"   📝 {desc_limpa}")
    
    def run(self) -> Dict[str, Any]:
        """Executar a POC principal"""
        try:
            logger.info("Executando Radar de Notícias RSS...")
            
            # Buscar notícias de todos os feeds
            noticias = self.buscar_todas_noticias()
            
            if noticias:
                # Exibir notícias
                self.exibir_noticias(noticias)
                
                result = {
                    "status": "success",
                    "message": f"Radar de Notícias RSS executado com sucesso - {len(noticias)} notícias encontradas",
                    "data": {
                        "noticias_encontradas": len(noticias),
                        "feeds_consultados": len(self.rss_feeds),
                        "limite": self.max_noticias
                    }
                }
                
                logger.info("Radar de Notícias RSS concluído com sucesso")
                return result
            else:
                result = {
                    "status": "warning",
                    "message": "Nenhuma notícia encontrada nos RSS feeds",
                    "data": {
                        "noticias_encontradas": 0,
                        "feeds_consultados": len(self.rss_feeds),
                        "limite": self.max_noticias
                    }
                }
                
                logger.warning("Nenhuma notícia encontrada")
                return result
                
        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def cleanup(self):
        """Limpar recursos utilizados"""
        try:
            logger.info("Limpando recursos...")
            # Não há recursos específicos para limpar nesta POC
            logger.info("Limpeza concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal para executar a POC"""
    poc = RSSFeedsPOC()
    
    try:
        # Configurar
        if not poc.setup():
            logger.error("Falha na configuração")
            return
        
        # Executar
        result = poc.run()
        
        # Exibir resultado resumido
        print(f"\n" + "=" * 70)
        print(f"📊 RESULTADO DA POC - RADAR DE NOTÍCIAS RSS")
        print("=" * 70)
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success':
            print(f"✅ POC executada com sucesso!")
            print(f"📰 Notícias encontradas: {result['data']['noticias_encontradas']}")
            print(f"📡 Feeds consultados: {result['data']['feeds_consultados']}")
        elif result['status'] == 'warning':
            print(f"⚠️  POC executada, mas sem resultados")
        else:
            print(f"❌ POC falhou")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        print(f"❌ Erro inesperado: {e}")
    
    finally:
        # Limpar
        poc.cleanup()


if __name__ == "__main__":
    main()
