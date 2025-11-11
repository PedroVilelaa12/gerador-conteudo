#!/usr/bin/env python3
"""
POC - Geração de Imagens com OpenAI
Descrição: POC para gerar imagens usando OpenAI DALL-E API
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import base64
import requests
import logging
from typing import Any, Dict, Optional
from pocs.template_poc import POCTemplate

# Configurar logging
logger = logging.getLogger(__name__)


class OpenAIImagePOC(POCTemplate):
    """POC para geração de imagens com OpenAI DALL-E"""
    
    def __init__(self):
        """Inicializar gerador de imagens"""
        super().__init__()
        self.name = "OpenAI Image Generation POC"
        self.api_key = None
        self.base_url = "https://api.openai.com/v1/images/generations"
        
        # Configurações padrão
        self.default_size = "1024x1024"
        self.default_quality = "standard"
        self.default_style = "vivid"
    
    def setup(self) -> bool:
        """Configurar conexão com OpenAI API"""
        try:
            logger.info("Configurando conexão com OpenAI API...")
            
            # Carregar API key do ambiente
            self.api_key = os.getenv('OPENAI_API_KEY')
            
            if not self.api_key:
                logger.error("OPENAI_API_KEY não encontrado nas variáveis de ambiente")
                return False
            
            logger.info("Configuração do OpenAI concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do OpenAI: {e}")
            return False
    
    def generate_image(self, prompt: str, size: str = None, quality: str = None, style: str = None) -> Dict[str, Any]:
        """Gerar imagem usando OpenAI DALL-E"""
        try:
            logger.info(f"Gerando imagem com prompt: {prompt}")
            
            # Usar configurações padrão se não especificadas
            size = size or self.default_size
            quality = quality or self.default_quality
            style = style or self.default_style
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": quality,
                "style": style,
                "response_format": "b64_json"
            }
            
            response = requests.post(self.base_url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                image_data = result["data"][0]["b64_json"]
                
                # Decodificar base64 para bytes
                image_bytes = base64.b64decode(image_data)
                
                logger.info("Imagem gerada com sucesso")
                return {
                    "status": "success",
                    "message": "Imagem gerada com sucesso",
                    "data": {
                        "image_bytes": image_bytes,
                        "prompt": prompt,
                        "size": size,
                        "quality": quality,
                        "style": style,
                        "revised_prompt": result["data"][0].get("revised_prompt", prompt)
                    }
                }
            else:
                # Parse do erro para mensagem mais clara
                error_message = f"Erro na API OpenAI: {response.status_code}"
                try:
                    error_data = response.json()
                    error_info = error_data.get("error", {})
                    error_code = error_info.get("code", "")
                    error_msg = error_info.get("message", "")
                    
                    # Tratar diferentes tipos de erro
                    error_type = error_info.get("type", "")
                    
                    if error_code == "billing_hard_limit_reached":
                        error_message = "Limite de faturamento atingido. Adicione créditos em https://platform.openai.com/account/billing"
                    elif error_code == "insufficient_quota":
                        error_message = "Cota insuficiente. Verifique seus créditos em https://platform.openai.com/account/billing"
                    elif error_code == "invalid_api_key":
                        error_message = "Chave API inválida. Verifique se está correta no arquivo .env"
                    elif "rate_limit" in error_code.lower():
                        error_message = f"Limite de taxa excedido. Aguarde um momento antes de tentar novamente."
                    elif response.status_code == 500 or error_type == "server_error":
                        error_message = (
                            f"Erro temporário no servidor da OpenAI (500). "
                            f"Tente novamente em alguns segundos. "
                            f"Se persistir, verifique: https://status.openai.com/"
                        )
                    else:
                        error_message = f"Erro: {error_msg} (código: {error_code})"
                except:
                    error_message = f"Erro na API: {response.status_code} - {response.text[:200]}"
                
                logger.error(f"Erro na API OpenAI: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": error_message,
                    "data": {}
                }
                
        except Exception as e:
            logger.error(f"Erro na geração de imagem: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
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
            logger.info("Limpando recursos do OpenAI...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza do OpenAI concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = OpenAIImagePOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração do OpenAI")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - Geração de Imagem OpenAI:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success' and 'data' in result:
            print(f"\nDetalhes da geração:")
            print(f"  Prompt: {result['data'].get('prompt', 'N/A')}")
            print(f"  Prompt revisado: {result['data'].get('revised_prompt', 'N/A')}")
            print(f"  Tamanho: {result['data'].get('size', 'N/A')}")
            print(f"  Qualidade: {result['data'].get('quality', 'N/A')}")
            print(f"  Estilo: {result['data'].get('style', 'N/A')}")
            print(f"  Arquivo salvo: {result['data'].get('filepath', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
