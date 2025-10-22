#!/usr/bin/env python3
"""
Servidor Local para Imagens
Descrição: Servidor HTTP simples para servir imagens localmente
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import sys
import http.server
import socketserver
from pathlib import Path

def start_local_server(port=8000, directory="generated_images"):
    """Iniciar servidor HTTP local"""
    
    # Criar diretório se não existir
    Path(directory).mkdir(exist_ok=True)
    
    # Mudar para o diretório das imagens
    os.chdir(directory)
    
    # Configurar servidor
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 Servidor local iniciado!")
        print(f"📁 Servindo arquivos de: {os.path.abspath(directory)}")
        print(f"🔗 URL base: http://localhost:{port}")
        print(f"📸 Exemplo: http://localhost:{port}/sua_imagem.png")
        print("=" * 50)
        print("Pressione Ctrl+C para parar o servidor")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor encerrado pelo usuário")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Servidor local para imagens")
    parser.add_argument("--port", type=int, default=8000, help="Porta do servidor (padrão: 8000)")
    parser.add_argument("--directory", default="generated_images", help="Diretório das imagens (padrão: generated_images)")
    
    args = parser.parse_args()
    
    start_local_server(args.port, args.directory)

if __name__ == "__main__":
    main()
