#!/usr/bin/env python3
"""
Script para obter tokens do LinkedIn
Descrição: Ajuda a obter access_token do LinkedIn
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import webbrowser
import requests
from urllib.parse import urlencode, parse_qs, urlparse

def get_linkedin_tokens():
    """Obter tokens do LinkedIn via OAuth"""
    
    # Configurações (substitua pelos seus valores)
    CLIENT_ID = input("Digite seu LinkedIn Client ID: ").strip()
    CLIENT_SECRET = input("Digite seu LinkedIn Client Secret: ").strip()
    REDIRECT_URI = "https://localhost/"
    
    # URL de autorização
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'random_state_string',
        'scope': 'r_liteprofile,r_emailaddress,w_member_social'
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
    
    print("🌐 Abrindo navegador para autorização...")
    print(f"URL: {auth_url}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Autorize a aplicação no LinkedIn")
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
        return None
    
    auth_code = query_params['code'][0]
    print(f"✅ Código obtido: {auth_code}")
    
    # Trocar código por token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    print("🔄 Obtendo tokens...")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        print("✅ Tokens obtidos com sucesso!")
        print(f"Access Token: {access_token}")
        
        # Salvar no .env
        save_to_env('LINKEDIN_ACCESS_TOKEN', access_token)
        save_to_env('LINKEDIN_CLIENT_ID', CLIENT_ID)
        save_to_env('LINKEDIN_CLIENT_SECRET', CLIENT_SECRET)
        
        return access_token
    else:
        print(f"❌ Erro ao obter tokens: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

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
    print("💼 CONFIGURAÇÃO DO LINKEDIN API")
    print("=" * 40)
    
    access_token = get_linkedin_tokens()
    
    if access_token:
        print("\n🎉 Configuração do LinkedIn concluída!")
        print("Agora você pode usar a API do LinkedIn no sistema.")
    else:
        print("\n❌ Falha na configuração do LinkedIn")
        print("Verifique suas credenciais e tente novamente.")

if __name__ == "__main__":
    main()
