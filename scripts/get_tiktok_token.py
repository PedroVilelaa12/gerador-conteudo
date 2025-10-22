#!/usr/bin/env python3
"""
Script para obter tokens do TikTok
Descrição: Ajuda a obter access_token e open_id do TikTok
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import webbrowser
import requests
from urllib.parse import urlencode, parse_qs, urlparse

def get_tiktok_tokens():
    """Obter tokens do TikTok via OAuth"""
    
    # Configurações (substitua pelos seus valores)
    CLIENT_KEY = input("Digite seu TikTok Client Key: ").strip()
    CLIENT_SECRET = input("Digite seu TikTok Client Secret: ").strip()
    REDIRECT_URI = "http://localhost:8000/callback"
    
    # URL de autorização
    auth_params = {
        'client_key': CLIENT_KEY,
        'scope': 'user.info.basic,video.upload',
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI
    }
    
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(auth_params)}"
    
    print("🌐 Abrindo navegador para autorização...")
    print(f"URL: {auth_url}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Autorize a aplicação no TikTok")
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
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    token_data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    print("🔄 Obtendo tokens...")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        open_id = token_data.get('open_id')
        
        print("✅ Tokens obtidos com sucesso!")
        print(f"Access Token: {access_token}")
        print(f"Open ID: {open_id}")
        
        # Salvar no .env
        save_to_env('TIKTOK_ACCESS_TOKEN', access_token)
        save_to_env('TIKTOK_OPEN_ID', open_id)
        
        return access_token, open_id
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
    print("🎵 CONFIGURAÇÃO DO TIKTOK API")
    print("=" * 40)
    
    access_token, open_id = get_tiktok_tokens()
    
    if access_token and open_id:
        print("\n🎉 Configuração do TikTok concluída!")
        print("Agora você pode usar a API do TikTok no sistema.")
    else:
        print("\n❌ Falha na configuração do TikTok")
        print("Verifique suas credenciais e tente novamente.")

if __name__ == "__main__":
    main()
