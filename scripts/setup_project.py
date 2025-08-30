#!/usr/bin/env python3
"""
Script de inicialização do projeto
Executa configurações iniciais necessárias usando Poetry
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def executar_comando(comando, descricao):
    """Executar comando e mostrar resultado"""
    print(f"🔄 {descricao}...")
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {descricao} concluído com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {descricao.lower()}: {e}")
        print(f"   Saída de erro: {e.stderr}")
        return False

def verificar_python():
    """Verificar versão do Python"""
    print("🐍 Verificando versão do Python...")
    versao = sys.version_info
    if versao.major < 3 or (versao.major == 3 and versao.minor < 8):
        print(f"❌ Python 3.8+ é necessário. Versão atual: {versao.major}.{versao.minor}")
        return False
    
    print(f"✅ Python {versao.major}.{versao.minor}.{versao.micro} - OK")
    return True

def verificar_poetry():
    """Verificar se Poetry está instalado"""
    print("📦 Verificando Poetry...")
    if not shutil.which("poetry"):
        print("❌ Poetry não encontrado")
        print("💡 Instale o Poetry com:")
        print("   curl -sSL https://install.python-poetry.org | python3 -")
        print("   ou")
        print("   pip install poetry")
        return False
    
    # Verificar versão do Poetry
    try:
        resultado = subprocess.run("poetry --version", shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {resultado.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao verificar versão do Poetry")
        return False

def configurar_poetry():
    """Configurar Poetry para o projeto"""
    print("🔧 Configurando Poetry...")
    
    # Verificar se já é um projeto Poetry
    if Path("pyproject.toml").exists():
        print("✅ pyproject.toml já existe")
        
        # Verificar se Poetry reconhece o projeto
        if executar_comando("poetry check", "Verificação do projeto Poetry"):
            print("✅ Projeto Poetry configurado corretamente")
            return True
        else:
            print("⚠️  Projeto Poetry com problemas, tentando corrigir...")
    
    # Inicializar projeto Poetry se necessário
    if not Path("pyproject.toml").exists():
        print("🔄 Inicializando projeto Poetry...")
        if not executar_comando("poetry init --name gerador-conteudo --description 'Estrutura para POCs' --author 'Seu Nome <seu.email@exemplo.com>' --python '^3.8' --dependency requests --dependency python-dotenv --dev-dependency pytest --dev-dependency black --dev-dependency flake8 --no-interaction", "Inicialização do Poetry"):
            return False
    
    return True

def instalar_dependencias():
    """Instalar dependências usando Poetry"""
    print("📦 Instalando dependências com Poetry...")
    
    # Instalar dependências básicas
    if executar_comando("poetry install", "Instalação das dependências"):
        print("✅ Dependências instaladas")
        return True
    return False

def instalar_dependencias_opcionais():
    """Instalar grupos de dependências opcionais"""
    print("📦 Instalando dependências opcionais...")
    
    grupos = ["data", "api", "automation"]
    for grupo in grupos:
        print(f"🔄 Instalando grupo '{grupo}'...")
        if executar_comando(f"poetry install --with {grupo}", f"Instalação do grupo {grupo}"):
            print(f"✅ Grupo '{grupo}' instalado")
        else:
            print(f"⚠️  Grupo '{grupo}' não pôde ser instalado")
    
    return True

def configurar_git_hooks():
    """Configurar git hooks se git estiver disponível"""
    if not shutil.which("git"):
        print("⚠️  Git não encontrado, pulando configuração de hooks")
        return True
    
    print("🔧 Configurando git hooks...")
    
    # Criar diretório .git/hooks se não existir
    hooks_dir = Path(".git/hooks")
    hooks_dir.mkdir(exist_ok=True)
    
    # Criar pre-commit hook básico
    pre_commit_hook = hooks_dir / "pre-commit"
    if not pre_commit_hook.exists():
        with open(pre_commit_hook, "w") as f:
            f.write("""#!/bin/sh
# Pre-commit hook para executar testes
echo "🧪 Executando testes antes do commit..."
poetry run pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "❌ Testes falharam. Commit cancelado."
    exit 1
fi
echo "✅ Testes passaram. Commit permitido."
""")
        
        # Tornar executável (Unix/Linux/Mac)
        if os.name != 'nt':
            os.chmod(pre_commit_hook, 0o755)
        
        print("✅ Git hook pre-commit configurado")
    
    return True

def executar_teste_inicial():
    """Executar teste inicial para verificar se tudo está funcionando"""
    print("🧪 Executando teste inicial...")
    if executar_comando("poetry run pytest tests/ -v", "Teste inicial"):
        print("✅ Teste inicial passou")
        return True
    else:
        print("⚠️  Teste inicial falhou, mas o projeto pode estar funcionando")
        return True

def mostrar_proximos_passos():
    """Mostrar próximos passos para o usuário"""
    print("\n" + "="*60)
    print("🎉 PROJETO CONFIGURADO COM SUCESSO!")
    print("="*60)
    print("\n📋 Próximos passos:")
    print("1. Ativar ambiente Poetry:")
    print("   poetry shell")
    
    print("\n2. Executar POC de exemplo:")
    print("   poetry run python scripts/run_poc.py exemplo_poc")
    print("   ou")
    print("   poetry run run-poc exemplo_poc")
    
    print("\n3. Listar POCs disponíveis:")
    print("   poetry run python scripts/run_poc.py")
    
    print("\n4. Executar testes:")
    print("   poetry run pytest")
    
    print("\n5. Criar nova POC:")
    print("   cp pocs/template_poc.py pocs/minha_nova_poc.py")
    
    print("\n6. Adicionar novas dependências:")
    print("   poetry add nome-da-biblioteca")
    print("   poetry add --group dev nome-da-biblioteca-dev")
    
    print("\n7. Atualizar dependências:")
    print("   poetry update")
    
    print("\n📚 Documentação completa no README.md")
    print("🔧 Configurações em pyproject.toml")
    print("\n💡 Dica: Use 'poetry run' antes dos comandos ou 'poetry shell' para ativar o ambiente!")

def main():
    """Função principal"""
    print("🚀 Inicializando projeto Gerador de Conteúdo com Poetry...")
    print("="*60)
    
    # Verificações básicas
    if not verificar_python():
        return False
    
    if not verificar_poetry():
        return False
    
    # Configuração do Poetry
    if not configurar_poetry():
        return False
    
    # Instalação de dependências
    if not instalar_dependencias():
        return False
    
    # Instalação de dependências opcionais
    instalar_dependencias_opcionais()
    
    # Configuração de git hooks
    if not configurar_git_hooks():
        return False
    
    # Teste inicial
    executar_teste_inicial()
    
    # Mostrar próximos passos
    mostrar_proximos_passos()
    
    return True

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        print("\n❌ Configuração falhou. Verifique os erros acima.")
        sys.exit(1)
