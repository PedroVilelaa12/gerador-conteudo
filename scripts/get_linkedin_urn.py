#!/usr/bin/env python3
"""
Script Helper para Obter URN do LinkedIn
Descrição: Ajuda a obter o URN do perfil quando não consegue automaticamente
Autor: Gerador de Conteúdo
Data: 2024
"""

import os
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

def get_urn_via_userinfo(access_token):
    """Tentar obter URN via OpenID Connect /userinfo"""
    try:
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            sub = data.get("sub", "")
            if sub:
                if sub.startswith("urn:li:person:"):
                    return sub
                else:
                    return f"urn:li:person:{sub}"
        
        return None
    except Exception as e:
        print(f"Erro em /userinfo: {e}")
        return None

def get_urn_via_me(access_token):
    """Tentar obter URN via endpoint /me"""
    try:
        url = "https://api.linkedin.com/v2/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "projection": "(id)"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            person_id = data.get("id", "")
            if person_id:
                return f"urn:li:person:{person_id}"
        
        return None
    except Exception as e:
        print(f"Erro em /me: {e}")
        return None

def save_to_env(key, value):
    """Salvar variável no arquivo .env"""
    env_file = Path(__file__).parent.parent / '.env'
    
    # Ler arquivo atual
    lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        # Criar arquivo se não existir
        env_file.touch()
    
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
    print("🔍 OBTENDO URN DO LINKEDIN")
    print("=" * 50)
    
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ LINKEDIN_ACCESS_TOKEN não encontrado no .env")
        print("Execute primeiro: poetry run python scripts/get_linkedin_token.py")
        return
    
    print("🔍 Tentando obter URN do perfil...")
    print()
    
    # Tentar método 1: /userinfo
    print("1️⃣ Tentando via /userinfo (OpenID Connect)...")
    urn = get_urn_via_userinfo(access_token)
    
    if urn:
        print(f"✅ URN obtido: {urn}")
        save_to_env('LINKEDIN_PERSON_URN', urn)
        print("\n🎉 URN configurado com sucesso!")
        return
    
    print("❌ Não funcionou via /userinfo")
    print()
    
    # Tentar método 2: /me
    print("2️⃣ Tentando via /me...")
    urn = get_urn_via_me(access_token)
    
    if urn:
        print(f"✅ URN obtido: {urn}")
        save_to_env('LINKEDIN_PERSON_URN', urn)
        print("\n🎉 URN configurado com sucesso!")
        return
    
    print("❌ Não funcionou via /me")
    print()
    
    # Se não funcionou
    print("=" * 50)
    print("❌ Não foi possível obter URN automaticamente")
    print()
    print("💡 SOLUÇÕES:")
    print()
    print("Opção 1: Regerar token com escopos corretos")
    print("  poetry run python scripts/get_linkedin_token.py")
    print("  (O novo token terá escopos: w_member_social openid profile)")
    print()
    print("Opção 2: Configurar manualmente no .env")
    print("  LINKEDIN_PERSON_URN=urn:li:person:SEU_ID")
    print()
    print("Para descobrir seu ID, você pode:")
    print("  - Verificar sua URL do LinkedIn: linkedin.com/in/SEU_PERFIL")
    print("  - Ou usar a API com um token de teste")
    print("=" * 50)

if __name__ == "__main__":
    main()

