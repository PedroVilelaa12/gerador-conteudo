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
    REDIRECT_URI = input("Digite a Redirect URI configurada (ex: https://niceasvini.github.io/callback.html): ").strip() or "https://niceasvini.github.io/callback.html"
    
    # URL de autorização
    auth_params = {
        'client_key': CLIENT_KEY,
        'scope': 'user.info.basic,video.upload,video.publish',
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI
    }
    
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(auth_params)}"
    
    print("🌐 Abrindo navegador para autorização...")
    print(f"URL: {auth_url}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Autorize a aplicação no TikTok")
    print("2. Você será redirecionado para uma URL com 'code='")
    print("3. Copie a URL completa (mesmo se der erro 404)")
    print("\n💡 DICAS PARA COLAR:")
    print("   - PowerShell: Clique com botão direito no terminal → Paste")
    print("   - Ou pressione: Shift+Insert")
    print("\n📌 EXEMPLO do que colar:")
    print(f"   {REDIRECT_URI}?code=xxx...&state=...")
    
    webbrowser.open(auth_url)
    
    # Obter código de autorização
    print("\n" + "="*60)
    print("⚠️  IMPORTANTE: Copie a URL COMPLETA da barra de endereços")
    print("   Depois clique com botão direito no terminal e selecione 'Paste'")
    print("   Ou pressione Shift+Insert")
    print("="*60)
    redirect_url = input("\n✏️  Cole a URL de redirecionamento aqui: ").strip()
    
    # Verificar se a URL é a correta
    if 'tiktok.com/v2/auth/authorize' in redirect_url:
        print("\n" + "="*60)
        print("❌ ERRO: Você colou a URL ERRADA!")
        print("="*60)
        print("Você colou a URL INICIAL (que o script abre)")
        print("Você precisa colar a URL de REDIRECIONAMENTO!")
        print("\n📋 O QUE FAZER:")
        print("1. No navegador, clique em 'Allow' (Permitir)")
        print("2. AGUARDE o TikTok redirecionar")
        print("3. Copie a URL da BARRA DE ENDEREÇOS")
        print(f"   (Deve começar com: {REDIRECT_URI}?code=...)")
        print("4. Cole novamente no terminal")
        print("="*60)
        
        # Tentar novamente
        redirect_url = input("\n✏️  Cole a URL CORRETA de redirecionamento: ").strip()
    
    # Verificar se está vazia ou parece inválida
    if not redirect_url or len(redirect_url) < 20:
        print("\n⚠️  URL parece estar vazia ou incompleta.")
        print("💡 Tente novamente:")
        print("   1. Vá ao navegador")
        print("   2. Copie TUDO da barra de endereços (Ctrl+L para selecionar)")
        print("   3. Clique com botão direito no terminal → Paste")
        redirect_url = input("\n✏️  Cole a URL novamente: ").strip()
    
    # Extrair código da URL
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print("\n" + "="*60)
        print("❌ Código de autorização não encontrado na URL")
        print("="*60)
        print("A URL deve conter '?code=' seguido de uma string longa")
        print("\n✅ URL CORRETA deve ser assim:")
        print(f"   {REDIRECT_URI}?code=xxx123abc456...&state=...")
        print("\n❌ URL ERRADA seria assim:")
        print("   https://www.tiktok.com/v2/auth/authorize?...")
        print("\n💡 Tente novamente:")
        print("   1. Vá ao navegador")
        print("   2. Clique em 'Allow' se ainda não clicou")
        print("   3. Copie a URL da barra de endereços DEPOIS do redirecionamento")
        print("="*60)
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
    print(f"📝 Usando Redirect URI: {REDIRECT_URI}")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        open_id = token_data.get('open_id')
        refresh_token = token_data.get('refresh_token')
        
        print("✅ Tokens obtidos com sucesso!")
        print(f"Access Token: {access_token}")
        print(f"Open ID: {open_id}")
        if refresh_token:
            print(f"Refresh Token: {refresh_token}")
        
        # Salvar no .env
        save_to_env('TIKTOK_CLIENT_KEY', CLIENT_KEY)
        save_to_env('TIKTOK_CLIENT_SECRET', CLIENT_SECRET)
        save_to_env('TIKTOK_REDIRECT_URI', REDIRECT_URI)
        save_to_env('TIKTOK_ACCESS_TOKEN', access_token)
        save_to_env('TIKTOK_OPEN_ID', open_id)
        if refresh_token:
            save_to_env('TIKTOK_REFRESH_TOKEN', refresh_token)
        
        return access_token, open_id
    else:
        print(f"❌ Erro ao obter tokens: {response.status_code}")
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('error_description', response.text)
        
        print(f"Detalhes: {error_msg}")
        
        # Tratamento específico para erro de redirect_uri
        if 'redirect_uri' in error_msg.lower() or 'redirect_uri is not matched' in error_msg.lower():
            print("\n" + "="*60)
            print("❌ ERRO: Redirect URI não corresponde!")
            print("="*60)
            print("A Redirect URI usada deve ser EXATAMENTE igual à configurada no TikTok Portal.")
            print(f"\nRedirect URI usada no script: {REDIRECT_URI}")
            print("\n📋 O QUE FAZER:")
            print("1. Acesse: https://developers.tiktok.com/")
            print("2. Vá em 'Manage Apps' → Selecione sua app")
            print("3. Vá em 'Products' → 'Login Kit' → Aba 'Web'")
            print("4. Verifique qual Redirect URI está configurada")
            print("5. Certifique-se de que seja EXATAMENTE:")
            print(f"   {REDIRECT_URI}")
            print("6. Se estiver diferente, corrija no Portal e execute o script novamente")
            print("="*60)
        
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
