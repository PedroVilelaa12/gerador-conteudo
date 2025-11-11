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
    REDIRECT_URI = input("Digite a Redirect URI configurada (ex: http://localhost:8051/callback): ").strip() or "http://localhost:8051/callback"
    
    # URL de autorização
    print("\n📋 Escopos disponíveis:")
    print("   1. w_member_social (para publicar posts) - OBRIGATÓRIO")
    print("   2. w_member_social + openid + profile (obter URN automaticamente) - RECOMENDADO")
    print("\n⚠️  Para usar openid+profile, você precisa habilitar 'Sign In with LinkedIn using OpenID Connect'")
    print("    no LinkedIn Developer Portal → Products")
    
    use_openid = input("\nDeseja tentar usar openid+profile? (s/n) [n]: ").strip().lower()
    
    if use_openid == 's':
        scope = 'w_member_social openid profile'
        print("✅ Tentando com escopos: w_member_social openid profile")
    else:
        scope = 'w_member_social'
        print("✅ Usando apenas: w_member_social")
        print("⚠️  Você precisará configurar LINKEDIN_PERSON_URN manualmente no .env")
    
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'random_state_string',
        'scope': scope
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
    
    print("🌐 Abrindo navegador para autorização...")
    print(f"URL: {auth_url}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Autorize a aplicação no LinkedIn")
    print("2. Você será redirecionado para uma URL com 'code='")
    print("3. Copie a URL completa (mesmo se der erro 404)")
    print("\n💡 DICAS PARA COLAR:")
    print("   - PowerShell: Clique com botão direito no terminal → Paste")
    print("   - Ou pressione: Ctrl+Shift+V")
    print("   - Ou apenas digite a URL manualmente")
    print("\n📌 EXEMPLO do que colar:")
    print(f"   {REDIRECT_URI}?code=AQTxxx...&state=...")
    
    webbrowser.open(auth_url)
    
    # Obter código de autorização
    print("\n" + "="*60)
    print("⚠️  IMPORTANTE: Copie a URL COMPLETA da barra de endereços")
    print("   Depois clique com botão direito no terminal e selecione 'Paste'")
    print("   Ou pressione Ctrl+Shift+V")
    print("="*60)
    redirect_url = input("\n✏️  Cole a URL de redirecionamento aqui: ").strip()
    
    # Se estiver vazia ou parecer inválida, tentar novamente
    if not redirect_url or len(redirect_url) < 20:
        print("\n⚠️  URL parece estar vazia ou incompleta.")
        print("💡 Tente novamente:")
        print("   1. Vá ao navegador")
        print("   2. Copie TUDO da barra de endereços (Ctrl+L para selecionar)")
        print("   3. Clique com botão direito no terminal → Paste")
        redirect_url = input("\n✏️  Cole a URL novamente: ").strip()
    
    # Verificar se a URL é a correta
    if 'linkedin.com/oauth/v2/authorization' in redirect_url:
        print("\n" + "="*60)
        print("❌ ERRO: Você colou a URL ERRADA!")
        print("="*60)
        print("Você colou a URL INICIAL (que o script abre)")
        print("Você precisa colar a URL de REDIRECIONAMENTO!")
        print("\n📋 O QUE FAZER:")
        print("1. No navegador, clique em 'Allow' (Permitir)")
        print("2. AGUARDE o LinkedIn redirecionar")
        print("3. Copie a URL da BARRA DE ENDEREÇOS")
        print("   (Deve começar com: http://localhost:8501/callback?code=...)")
        print("4. Cole novamente no terminal")
        print("="*60)
        
        # Tentar novamente
        redirect_url = input("\n✏️  Cole a URL CORRETA de redirecionamento: ").strip()
    
    # Extrair código da URL
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print("\n" + "="*60)
        print("❌ Código de autorização não encontrado na URL")
        print("="*60)
        print("A URL deve conter '?code=' seguido de uma string longa")
        print("\n✅ URL CORRETA deve ser assim:")
        print("   http://localhost:8501/callback?code=AQT123abc456...&state=...")
        print("\n❌ URL ERRADA seria assim:")
        print("   https://www.linkedin.com/oauth/v2/authorization?...")
        print("\n💡 Tente novamente:")
        print("   1. Vá ao navegador")
        print("   2. Clique em 'Allow' se ainda não clicou")
        print("   3. Copie a URL da barra de endereços DEPOIS do redirecionamento")
        print("="*60)
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
