#!/usr/bin/env python3
"""
Testes para a POC do Radar de Notícias (RSS Feeds)
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar o diretório pai ao path para importar as POCs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocs.rss_feeds_poc import RSSFeedsPOC


class TestRSSFeedsPOC:
    """Testes para a POC do Radar de Notícias RSS"""
    
    def setup_method(self):
        """Configurar antes de cada teste"""
        self.poc = RSSFeedsPOC()
    
    def teardown_method(self):
        """Limpar após cada teste"""
        self.poc.cleanup()
    
    def test_init(self):
        """Testar inicialização da POC"""
        assert self.poc.name == "Radar de Notícias RSS POC"
        assert self.poc.max_noticias == 5
        assert len(self.poc.rss_feeds) == 5
        assert "G1 Economia" in self.poc.rss_feeds
        assert "UOL Economia" in self.poc.rss_feeds
    
    @patch('requests.get')
    def test_setup_success(self, mock_get):
        """Testar configuração bem-sucedida"""
        # Mock de resposta bem-sucedida
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert self.poc.setup() == True
    
    @patch('requests.get')
    def test_setup_failure(self, mock_get):
        """Testar configuração com falha"""
        # Mock de resposta com erro
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        assert self.poc.setup() == False
    
    @patch('requests.get')
    def test_buscar_noticias_rss_success(self, mock_get):
        """Testar busca de notícias RSS bem-sucedida"""
        # Mock de resposta RSS válida
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Teste Notícia 1</title>
                    <link>https://exemplo.com/noticia1</link>
                    <description>Descrição da notícia 1</description>
                    <pubDate>Mon, 31 Aug 2025 15:00:00 +0000</pubDate>
                </item>
                <item>
                    <title>Teste Notícia 2</title>
                    <link>https://exemplo.com/noticia2</link>
                    <description>Descrição da notícia 2</description>
                    <pubDate>Mon, 31 Aug 2025 16:00:00 +0000</pubDate>
                </item>
            </channel>
        </rss>'''
        mock_get.return_value = mock_response
        
        noticias = self.poc.buscar_noticias_rss("https://exemplo.com/rss", "Portal Teste")
        
        assert len(noticias) == 2
        assert noticias[0]["title"] == "Teste Notícia 1"
        assert noticias[1]["title"] == "Teste Notícia 2"
        assert noticias[0]["source"] == "Portal Teste"
    
    @patch('requests.get')
    def test_buscar_noticias_rss_no_items(self, mock_get):
        """Testar RSS sem itens"""
        # Mock de resposta RSS vazia
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
            </channel>
        </rss>'''
        mock_get.return_value = mock_response
        
        noticias = self.poc.buscar_noticias_rss("https://exemplo.com/rss", "Portal Teste")
        assert len(noticias) == 0
    
    @patch('requests.get')
    def test_buscar_noticias_rss_error(self, mock_get):
        """Testar erro na busca RSS"""
        # Mock de erro na requisição
        mock_get.side_effect = Exception("Erro de conexão")
        
        noticias = self.poc.buscar_noticias_rss("https://exemplo.com/rss", "Portal Teste")
        assert len(noticias) == 0
    
    def test_extrair_texto(self):
        """Testar extração de texto de elementos XML"""
        # Criar elemento XML mock
        from xml.etree.ElementTree import Element
        item = Element("item")
        
        title_elem = Element("title")
        title_elem.text = "Título da Notícia"
        item.append(title_elem)
        
        # Testar extração
        title = self.poc._extrair_texto(item, ['title'])
        assert title == "Título da Notícia"
        
        # Testar tag não encontrada
        subtitle = self.poc._extrair_texto(item, ['subtitle'])
        assert subtitle == ""
    
    def test_formatar_data(self):
        """Testar formatação de datas"""
        # Testar formato RSS padrão
        data_rss = "Mon, 31 Aug 2025 15:00:00 +0000"
        formatada = self.poc._formatar_data(data_rss)
        assert formatada == "31/08/2025 15:00"
        
        # Testar formato ISO
        data_iso = "2025-08-31T15:00:00Z"
        formatada = self.poc._formatar_data(data_iso)
        assert formatada == "31/08/2025 15:00"
        
        # Testar data inválida
        data_invalida = "data inválida"
        formatada = self.poc._formatar_data(data_invalida)
        assert formatada == "data inválida"
        
        # Testar data vazia
        formatada = self.poc._formatar_data("")
        assert formatada == "Data não disponível"
    
    @patch.object(RSSFeedsPOC, 'buscar_noticias_rss')
    def test_buscar_todas_noticias(self, mock_buscar):
        """Testar busca de todas as notícias"""
        # Mock de notícias de diferentes feeds
        mock_buscar.side_effect = [
            [{"title": "Notícia 1", "source": "G1"}],
            [{"title": "Notícia 2", "source": "UOL"}],
            [{"title": "Notícia 3", "source": "Estadão"}],
            Exception("Erro no feed"),  # Simular erro no 4º feed
            Exception("Erro no feed")   # Simular erro no 5º feed
        ]
        
        noticias = self.poc.buscar_todas_noticias()
        
        assert len(noticias) == 3
        assert mock_buscar.call_count == 5  # Deve tentar todos os 5 feeds
    
    def test_exibir_noticias(self, capsys):
        """Testar exibição de notícias"""
        noticias = [
            {
                "title": "Notícia Teste 1",
                "source": "Fonte 1",
                "published_at": "31/08/2025 15:00",
                "link": "https://exemplo.com/1",
                "description": "Descrição da notícia teste 1"
            },
            {
                "title": "Notícia Teste 2",
                "source": "Fonte 2",
                "published_at": "31/08/2025 16:00",
                "link": "https://exemplo.com/2",
                "description": "Descrição da notícia teste 2"
            }
        ]
        
        self.poc.exibir_noticias(noticias)
        captured = capsys.readouterr()
        
        assert "TOP 2 NOTÍCIAS DE NEGÓCIOS - BRASIL (RSS)" in captured.out
        assert "1. Notícia Teste 1" in captured.out
        assert "2. Notícia Teste 2" in captured.out
        assert "Fonte: Fonte 1" in captured.out
        assert "Fonte: Fonte 2" in captured.out
    
    def test_exibir_noticias_vazias(self, capsys):
        """Testar exibição sem notícias"""
        self.poc.exibir_noticias([])
        captured = capsys.readouterr()
        
        assert "❌ Nenhuma notícia encontrada" in captured.out
    
    @patch.object(RSSFeedsPOC, 'buscar_todas_noticias')
    def test_run_success(self, mock_buscar):
        """Testar execução bem-sucedida"""
        # Mock de notícias
        mock_noticias = [
            {"title": "Notícia 1", "source": "Fonte 1"},
            {"title": "Notícia 2", "source": "Fonte 2"}
        ]
        mock_buscar.return_value = mock_noticias
        
        # Mock do setup
        with patch.object(self.poc, 'setup', return_value=True):
            result = self.poc.run()
            
            assert result['status'] == 'success'
            assert result['data']['noticias_encontradas'] == 2
            assert result['data']['feeds_consultados'] == 5
    
    @patch.object(RSSFeedsPOC, 'buscar_todas_noticias')
    def test_run_no_noticias(self, mock_buscar):
        """Testar execução sem notícias"""
        # Mock sem notícias
        mock_buscar.return_value = []
        
        # Mock do setup
        with patch.object(self.poc, 'setup', return_value=True):
            result = self.poc.run()
            
            assert result['status'] == 'warning'
            assert result['data']['noticias_encontradas'] == 0
    
    def test_cleanup(self):
        """Testar limpeza de recursos"""
        # Não deve gerar erro
        self.poc.cleanup()


if __name__ == "__main__":
    pytest.main([__file__])
