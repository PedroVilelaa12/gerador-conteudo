#!/usr/bin/env python3
"""
Script para executar a aplicação Streamlit
Descrição: Script para iniciar a interface web do sistema
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Função principal para executar Streamlit"""
    
    # Caminho para o arquivo Streamlit
    streamlit_file = Path(__file__).parent.parent / "web_interface" / "streamlit_app.py"
    
    if not streamlit_file.exists():
        print(f"ERRO: Arquivo Streamlit não encontrado: {streamlit_file}")
        return False
    
    print("🚀 Iniciando Sistema de Automação de Conteúdo...")
    print("=" * 60)
    print(f"📁 Arquivo: {streamlit_file}")
    print("🌐 Acesse: http://localhost:8501")
    print("=" * 60)
    
    try:
        # Executar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao executar Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
        return True
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
