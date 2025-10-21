#!/usr/bin/env python3
"""
Script para obter tokens do Instagram
Descrição: Ajuda a obter access_token e account_id do Instagram
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import webbrowser
import requests
from urllib.parse import urlencode, parse_qs, urlparse

def get_instagram_tokens():
    """Obter tokens do Instagram via OAuth"""
    
    # Configurações (substitua pelos seus valores)
    APP_ID = input("Digite seu Facebook App ID: ").strip()
    APP_SECRET = input("Digite seu Facebook App Secret: ").strip()
    REDIRECT_URI = "https://localhost/"
    
    # URL de autorização
    auth_params = {
        'client_id': APP_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'user_profile,user_media',
        'response_type': 'code'
    }
    
    auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(auth_params)}"
    
    print("🌐 Abrindo navegador para autorização...")
    print(f"URL: {auth_url}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Autorize a aplicação no Instagram")
    print("2. Você será redirecionado para uma URL com 'code='")
    print("3. Copie a URL completa e cole aqui")
    
    webbrowser.open(auth_url)
    
    # Obter código de autorização
    redirect_url = input("\nCole a URL de redirecionamento aqui: ").strip()
    
    # Extrair código da URL
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print("❌ Código de autorização não encontrado na URL")
        return None, None
    
    auth_code = query_params['code'][0]
    print(f"✅ Código obtido: {auth_code}")
    
    # Trocar código por token
    token_url = "https://api.instagram.com/oauth/access_token"
    
    token_data = {
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }
    
    print("🔄 Obtendo tokens...")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        user_id = token_data.get('user_id')
        
        print("✅ Tokens obtidos com sucesso!")
        print(f"Access Token: {access_token}")
        print(f"User ID: {user_id}")
        
        # Salvar no .env
        save_to_env('INSTAGRAM_ACCESS_TOKEN', access_token)
        save_to_env('INSTAGRAM_ACCOUNT_ID', user_id)
        
        return access_token, user_id
    else:
        print(f"❌ Erro ao obter tokens: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None, None

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
    
    print(f"✅ {key} salvo no arquivo .env")

def main():
    """Função principal"""
    print("📸 CONFIGURAÇÃO DO INSTAGRAM API")
    print("=" * 40)
    
    access_token, account_id = get_instagram_tokens()
    
    if access_token and account_id:
        print("\n🎉 Configuração do Instagram concluída!")
        print("Agora você pode usar a API do Instagram no sistema.")
    else:
        print("\n❌ Falha na configuração do Instagram")
        print("Verifique suas credenciais e tente novamente.")

if __name__ == "__main__":
    main()
