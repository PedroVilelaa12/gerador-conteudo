#!/usr/bin/env python3
"""
Script para testar as conexões com as APIs de redes sociais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocs.tiktok_poc import TikTokUploadPOC
from pocs.instagram_poc import InstagramUploadPOC
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tiktok_connection():
    """Testar conexão com TikTok API"""
    print("\n" + "="*50)
    print("TESTANDO CONEXÃO COM TIKTOK")
    print("="*50)
    
    try:
        poc = TikTokUploadPOC()
        
        # Testar apenas a configuração
        if poc.setup():
            print("OK: Configuração do TikTok")
            
            # Testar obtenção de informações do usuário
            user_info = poc.get_user_info()
            if user_info and "data" in user_info:
                print(f"OK: Usuário conectado: {user_info['data'].get('display_name', 'N/A')}")
                print(f"   Username: @{user_info['data'].get('username', 'N/A')}")
                return True
            else:
                print("ERRO: Falha ao obter informações do usuário")
                return False
        else:
            print("ERRO: Falha na configuração do TikTok")
            return False
            
    except Exception as e:
        print(f"ERRO no teste do TikTok: {e}")
        return False
    finally:
        if 'poc' in locals():
            poc.cleanup()


def test_instagram_connection():
    """Testar conexão com Instagram API"""
    print("\n" + "="*50)
    print("TESTANDO CONEXÃO COM INSTAGRAM")
    print("="*50)
    
    try:
        poc = InstagramUploadPOC()
        
        # Testar apenas a configuração
        if poc.setup():
            print("OK: Configuração do Instagram")
            
            # Testar obtenção de informações da conta
            account_info = poc.get_account_info()
            if account_info and "username" in account_info:
                print(f"OK: Conta conectada: @{account_info.get('username', 'N/A')}")
                print(f"   Nome: {account_info.get('name', 'N/A')}")
                print(f"   Tipo: {account_info.get('account_type', 'N/A')}")
                return True
            else:
                print("ERRO: Falha ao obter informações da conta")
                return False
        else:
            print("ERRO: Falha na configuração do Instagram")
            return False
            
    except Exception as e:
        print(f"ERRO no teste do Instagram: {e}")
        return False
    finally:
        if 'poc' in locals():
            poc.cleanup()


def main():
    """Função principal para testar todas as conexões"""
    print("TESTE DE CONEXÕES COM APIS DE REDES SOCIAIS")
    print("=" * 60)
    
    # Verificar se o arquivo .env existe
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        print("ATENÇÃO: Arquivo .env não encontrado!")
        print("   Copie o arquivo env.example para .env e configure suas credenciais")
        print(f"   Caminho esperado: {env_path}")
        return
    
    results = {
        "tiktok": False,
        "instagram": False
    }
    
    # Testar TikTok
    results["tiktok"] = test_tiktok_connection()
    
    # Testar Instagram
    results["instagram"] = test_instagram_connection()
    
    # Resumo final
    print("\n" + "="*50)
    print("RESUMO DOS TESTES")
    print("="*50)
    
    print(f"TikTok API: {'CONECTADO' if results['tiktok'] else 'FALHOU'}")
    print(f"Instagram API: {'CONECTADO' if results['instagram'] else 'FALHOU'}")
    
    if all(results.values()):
        print("\nTodas as APIs estão funcionando!")
        print("   Você pode executar os scripts de upload:")
        print("   - python pocs/tiktok_poc.py")
        print("   - python pocs/instagram_poc.py")
    else:
        print("\nAlgumas APIs falharam.")
        print("   Verifique as credenciais no arquivo .env")
        print("   Consulte SETUP_APIS.md para mais informações")


if __name__ == "__main__":
    main()
