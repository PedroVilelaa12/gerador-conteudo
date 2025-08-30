#!/usr/bin/env python3
"""
Script para executar POCs facilmente
Uso: python scripts/run_poc.py [nome_da_poc]
"""

import sys
import os
import importlib
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

def listar_pocs():
    """Listar todas as POCs disponíveis"""
    pocs_dir = Path(__file__).parent.parent / "pocs"
    pocs = []
    
    for arquivo in pocs_dir.glob("*.py"):
        if arquivo.name not in ["__init__.py", "template_poc.py"]:
            nome_poc = arquivo.stem
            pocs.append(nome_poc)
    
    return pocs

def executar_poc(nome_poc):
    """Executar uma POC específica"""
    try:
        # Importar a POC
        modulo = importlib.import_module(f"pocs.{nome_poc}")
        
        # Verificar se tem função main
        if hasattr(modulo, 'main'):
            print(f"🚀 Executando POC: {nome_poc}")
            print("=" * 50)
            modulo.main()
        else:
            print(f"❌ POC {nome_poc} não tem função main()")
            
    except ImportError as e:
        print(f"❌ Erro ao importar POC {nome_poc}: {e}")
    except Exception as e:
        print(f"❌ Erro ao executar POC {nome_poc}: {e}")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("📋 POCs disponíveis:")
        pocs = listar_pocs()
        
        if not pocs:
            print("   Nenhuma POC encontrada")
        else:
            for i, poc in enumerate(pocs, 1):
                print(f"   {i}. {poc}")
        
        print("\n💡 Uso: python scripts/run_poc.py [nome_da_poc]")
        print("   Exemplo: python scripts/run_poc.py exemplo_poc")
        return
    
    nome_poc = sys.argv[1]
    
    # Verificar se a POC existe
    pocs = listar_pocs()
    if nome_poc not in pocs:
        print(f"❌ POC '{nome_poc}' não encontrada")
        print(f"POCs disponíveis: {', '.join(pocs)}")
        return
    
    # Executar a POC
    executar_poc(nome_poc)

if __name__ == "__main__":
    main()
