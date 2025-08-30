#!/usr/bin/env python3
"""
POC - Busca e Download de Clipes (Pexels API)
Descrição: POC para buscar vídeos na API do Pexels e baixar o primeiro resultado
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import requests
import json
from typing import Any, Dict
from .template_poc import POCTemplate, logger


class PexelsAPIPOC(POCTemplate):
    """POC para busca e download de vídeos do Pexels"""
    
    def __init__(self):
        """Inicializar busca de vídeos do Pexels"""
        super().__init__()
        self.name = "Busca e Download de Clipes Pexels POC"
        self.api_key = None
        self.palavra_chave = "financial market"
        self.base_url = "https://api.pexels.com/videos/search"
        self.headers = {}
        self.video_info = None
        self.historico_file = "pexels_historico.json"
    
    def setup(self) -> bool:
        """Configurar API do Pexels"""
        try:
            logger.info("Configurando API do Pexels...")
            
            # Tentar obter API key das variáveis de ambiente
            self.api_key = os.getenv('PEXELS_API_KEY')
            
            if not self.api_key:
                logger.warning("PEXELS_API_KEY não encontrada no .env")
                logger.info("Você pode obter uma API key gratuita em: https://www.pexels.com/api/")
                # Para teste, vamos usar uma chave de exemplo (não funcionará)
                self.api_key = "YOUR_PEXELS_API_KEY_HERE"
                logger.warning("Usando chave de exemplo - substitua pela sua chave real no .env")
            
            # Configurar headers para requisições
            self.headers = {
                'Authorization': self.api_key,
                'User-Agent': 'Pexels API POC'
            }
            
            logger.info("Configuração do Pexels concluída")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração: {e}")
            return False
    
    def carregar_historico(self) -> Dict[str, list]:
        """Carregar histórico de vídeos já baixados"""
        try:
            if os.path.exists(self.historico_file):
                with open(self.historico_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Erro ao carregar histórico: {e}")
            return {}
    
    def salvar_historico(self, historico: Dict[str, list]):
        """Salvar histórico de vídeos baixados"""
        try:
            with open(self.historico_file, 'w', encoding='utf-8') as f:
                json.dump(historico, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erro ao salvar histórico: {e}")
    
    def adicionar_ao_historico(self, palavra_chave: str, video_id: int):
        """Adicionar vídeo ao histórico"""
        historico = self.carregar_historico()
        if palavra_chave not in historico:
            historico[palavra_chave] = []
        
        if video_id not in historico[palavra_chave]:
            historico[palavra_chave].append(video_id)
            # Manter apenas os últimos 50 vídeos por palavra-chave
            if len(historico[palavra_chave]) > 50:
                historico[palavra_chave] = historico[palavra_chave][-50:]
            
            self.salvar_historico(historico)
    
    def selecionar_proximo_video(self, videos: list, palavra_chave: str) -> Dict[str, Any]:
        """Selecionar o próximo vídeo por ordem de relevância que não foi baixado"""
        historico = self.carregar_historico()
        videos_baixados = historico.get(palavra_chave, [])
        
        # Procurar o primeiro vídeo que não foi baixado (em ordem de relevância)
        for i, video in enumerate(videos):
            if video.get('id') not in videos_baixados:
                logger.info(f"Selecionado vídeo por relevância: posição {i+1} de {len(videos)}")
                logger.info(f"ID do vídeo: {video.get('id')}")
                logger.info(f"Vídeos já baixados para '{palavra_chave}': {len(videos_baixados)}")
                return video
        
        # Se todos os vídeos já foram baixados, resetar e pegar o primeiro
        logger.info("Todos os vídeos disponíveis já foram baixados, reiniciando do primeiro...")
        logger.info(f"Resetando histórico para '{palavra_chave}'")
        
        # Limpar histórico desta palavra-chave
        historico[palavra_chave] = []
        self.salvar_historico(historico)
        
        return videos[0]
    
    def buscar_videos(self, query: str, per_page: int = 15) -> Dict[str, Any]:
        """Buscar vídeos na API do Pexels"""
        try:
            logger.info(f"Buscando vídeos com a palavra-chave: '{query}'")
            
            params = {
                'query': query,
                'per_page': per_page,
                'orientation': 'landscape'  # Preferir vídeos em landscape
            }
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            if response.status_code == 401:
                logger.error("Erro de autenticação - verifique sua API key do Pexels")
                return {"videos": [], "error": "API key inválida"}
            
            if response.status_code != 200:
                logger.error(f"Erro na busca: {response.status_code} - {response.text}")
                return {"videos": [], "error": f"Erro HTTP {response.status_code}"}
            
            data = response.json()
            logger.info(f"Encontrados {data.get('total_results', 0)} vídeos")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return {"videos": [], "error": str(e)}
        except Exception as e:
            logger.error(f"Erro inesperado na busca: {e}")
            return {"videos": [], "error": str(e)}
    
    def baixar_video(self, video_info: Dict[str, Any]) -> str:
        """Baixar vídeo do Pexels"""
        try:
            # Pegar a URL do vídeo em qualidade HD
            video_files = video_info.get('video_files', [])
            if not video_files:
                raise ValueError("Nenhum arquivo de vídeo encontrado")
            
            # Procurar por qualidade HD primeiro, senão pegar o primeiro disponível
            video_url = None
            for video_file in video_files:
                if video_file.get('quality') == 'hd':
                    video_url = video_file.get('link')
                    break
            
            if not video_url:
                video_url = video_files[0].get('link')
            
            if not video_url:
                raise ValueError("URL de vídeo não encontrada")
            
            # Gerar nome do arquivo
            video_id = video_info.get('id', 'unknown')
            filename = f"pexels_video_{video_id}_{self.palavra_chave}.mp4"
            filepath = os.path.join(os.getcwd(), filename)
            
            logger.info(f"Baixando vídeo: {video_url}")
            logger.info(f"Salvando como: {filename}")
            
            # Baixar o vídeo
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"Vídeo baixado com sucesso! Tamanho: {file_size / (1024*1024):.2f} MB")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao baixar vídeo: {e}")
            raise
    
    def run(self) -> Dict[str, Any]:
        """Executar busca e download de vídeo"""
        try:
            logger.info("Executando busca e download de vídeo do Pexels...")
            
            # Buscar vídeos
            resultado_busca = self.buscar_videos(self.palavra_chave)
            
            if "error" in resultado_busca:
                return {
                    "status": "error",
                    "message": f"Erro na busca: {resultado_busca['error']}",
                    "data": {}
                }
            
            videos = resultado_busca.get('videos', [])
            if not videos:
                return {
                    "status": "error",
                    "message": f"Nenhum vídeo encontrado para '{self.palavra_chave}'",
                    "data": {}
                }
            
            # Selecionar próximo vídeo por relevância (evitando repetições)
            video_selecionado = self.selecionar_proximo_video(videos, self.palavra_chave)
            self.video_info = video_selecionado
            
            logger.info(f"Vídeo selecionado: {video_selecionado.get('user', {}).get('name', 'Autor desconhecido')}")
            logger.info(f"Duração: {video_selecionado.get('duration', 'N/A')} segundos")
            
            # Baixar o vídeo
            arquivo_baixado = self.baixar_video(video_selecionado)
            
            # Adicionar ao histórico para evitar repetição
            self.adicionar_ao_historico(self.palavra_chave, video_selecionado.get('id'))
            
            result = {
                "status": "success",
                "message": f"Vídeo baixado com sucesso para '{self.palavra_chave}'",
                "data": {
                    "palavra_chave": self.palavra_chave,
                    "arquivo_baixado": arquivo_baixado,
                    "video_id": video_selecionado.get('id'),
                    "autor": video_selecionado.get('user', {}).get('name'),
                    "duracao": video_selecionado.get('duration'),
                    "total_resultados": resultado_busca.get('total_results', 0)
                }
            }
            
            logger.info("Busca e download concluídos com sucesso")
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
            logger.info("Limpando recursos do Pexels...")
            # Aqui você poderia limpar arquivos temporários se necessário
            logger.info("Limpeza concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = PexelsAPIPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - Busca e Download Pexels:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success':
            data = result['data']
            print(f"\n📹 Vídeo baixado com sucesso!")
            print(f"🔍 Palavra-chave: {data['palavra_chave']}")
            print(f"📁 Arquivo: {data['arquivo_baixado']}")
            print(f"🆔 ID do vídeo: {data['video_id']}")
            print(f"👤 Autor: {data['autor']}")
            print(f"⏱️ Duração: {data['duracao']} segundos")
            print(f"📊 Total de resultados encontrados: {data['total_resultados']}")
        else:
            print(f"\n❌ Erro: {result['message']}")
            if "API key" in result['message']:
                print("\n💡 Dica: Para usar esta POC:")
                print("1. Obtenha uma API key gratuita em: https://www.pexels.com/api/")
                print("2. Adicione PEXELS_API_KEY=sua_chave_aqui no arquivo .env")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
