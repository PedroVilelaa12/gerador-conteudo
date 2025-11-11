#!/usr/bin/env python3
"""
Script Principal - Configuração das APIs Sociais
Descrição: Guia completo para configurar TikTok, Instagram e LinkedIn
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import sys
from pathlib import Path

def print_header(title):
    """Imprimir cabeçalho"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step, title):
    """Imprimir passo"""
    print(f"\n📋 PASSO {step}: {title}")
    print("-" * 40)

def check_env_file():
    """Verificar se arquivo .env existe"""
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("💡 Copie o arquivo env.example para .env primeiro:")
        print("   cp env.example .env")
        return False
    return True

def setup_tiktok():
    """Configurar TikTok"""
    print_step(1, "CONFIGURAÇÃO DO TIKTOK")
    
    print("🎵 Para configurar o TikTok:")
    print("1. Acesse: https://developers.tiktok.com/")
    print("2. Crie uma aplicação")
    print("3. Adicione os produtos: Login Kit e Content Posting API")
    print("4. Configure as permissões necessárias")
    print("5. Anote o Client Key e Client Secret")
    
    choice = input("\nDeseja configurar o TikTok agora? (s/n): ").lower()
    if choice == 's':
        try:
            from scripts.get_tiktok_token import main as tiktok_main
            tiktok_main()
        except Exception as e:
            print(f"❌ Erro na configuração do TikTok: {e}")
    else:
        print("⏭️  Pulando configuração do TikTok")

def setup_instagram():
    """Configurar Instagram"""
    print_step(2, "CONFIGURAÇÃO DO INSTAGRAM")
    
    print("📸 Para configurar o Instagram:")
    print("1. Acesse: https://developers.facebook.com/")
    print("2. Crie uma aplicação")
    print("3. Adicione o produto: Instagram Basic Display")
    print("4. Configure as URLs de redirecionamento")
    print("5. Anote o App ID e App Secret")
    
    choice = input("\nDeseja configurar o Instagram agora? (s/n): ").lower()
    if choice == 's':
        try:
            from scripts.get_instagram_token import main as instagram_main
            instagram_main()
        except Exception as e:
            print(f"❌ Erro na configuração do Instagram: {e}")
    else:
        print("⏭️  Pulando configuração do Instagram")

def setup_linkedin():
    """Configurar LinkedIn"""
    print_step(3, "CONFIGURAÇÃO DO LINKEDIN")
    
    print("💼 Para configurar o LinkedIn:")
    print("1. Acesse: https://developer.linkedin.com/")
    print("2. Crie uma aplicação")
    print("3. Adicione os produtos: Share on LinkedIn e Sign In")
    print("4. Configure as URLs de redirecionamento")
    print("5. Anote o Client ID e Client Secret")
    
    choice = input("\nDeseja configurar o LinkedIn agora? (s/n): ").lower()
    if choice == 's':
        try:
            from scripts.get_linkedin_token import main as linkedin_main
            linkedin_main()
        except Exception as e:
            print(f"❌ Erro na configuração do LinkedIn: {e}")
    else:
        print("⏭️  Pulando configuração do LinkedIn")

def setup_gemini():
    """Configurar Google Gemini"""
    print_step(4, "CONFIGURAÇÃO DO GOOGLE GEMINI")
    
    print("🤖 Para configurar o Google Gemini:")
    print("1. Acesse: https://aistudio.google.com/app/apikey")
    print("2. Faça login com sua conta Google")
    print("3. Clique em 'Get API Key' ou 'Create API Key'")
    print("4. Copie a chave gerada")
    print("5. Cole aqui")
    
    api_key = input("\nDigite sua chave da API Gemini (ou pressione Enter para pular): ").strip()
    
    if api_key:
        # Salvar no .env
        save_to_env('GEMINI_API_KEY', api_key)
        print("✅ Chave do Gemini salva com sucesso!")
    else:
        print("⏭️  Pulando configuração do Gemini")

def save_to_env(key, value):
    """Salvar variável no arquivo .env"""
    env_file = '.env'
    
    # Ler arquivo atual
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Atualizar ou adicionar variável
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'{key}={value}\n')
    
    # Salvar arquivo
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def show_next_steps():
    """Mostrar próximos passos"""
    print_header("PRÓXIMOS PASSOS")
    
    print("🎉 Configuração concluída!")
    print("\n📋 Para testar o sistema:")
    print("1. Execute: poetry run python scripts/run_streamlit.py")
    print("2. Acesse: http://localhost:8501")
    print("3. Vá em 'Gerar Conteúdo' para criar imagens com IA")
    print("4. Vá em 'Aprovar Conteúdo' para publicar nas redes sociais")
    
    print("\n🔧 Para Instagram (se configurado):")
    print("1. Execute: poetry run python scripts/start_local_server.py")
    print("2. Isso criará URLs públicas para suas imagens")
    
    print("\n📊 Para monitorar métricas:")
    print("1. Vá em 'Métricas' na interface")
    print("2. Clique em 'Atualizar Métricas'")

def main():
    """Função principal"""
    print_header("CONFIGURAÇÃO DAS APIS SOCIAIS")
    
    print("🎯 Este script vai te ajudar a configurar:")
    print("   • TikTok API (para publicação)")
    print("   • Instagram API (para publicação)")
    print("   • LinkedIn API (para publicação)")
    print("   • Google Gemini API (para geração de imagens)")
    
    # Verificar arquivo .env
    if not check_env_file():
        return
    
    print("\n💡 DICA: Você pode configurar todas as APIs ou apenas as que quiser usar.")
    print("   O sistema funciona mesmo se você configurar apenas uma API.")
    
    # Configurar cada API
    setup_gemini()
    setup_tiktok()
    setup_instagram()
    setup_linkedin()
    
    # Mostrar próximos passos
    show_next_steps()

if __name__ == "__main__":
    main()
