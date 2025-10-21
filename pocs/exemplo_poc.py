#!/usr/bin/env python3
"""
Exemplo de POC - Validador de CPF
Descrição: POC para validar números de CPF brasileiros
Autor: Exemplo
Data: 2024
"""

import re
import logging
from typing import Any, Dict
from pocs.template_poc import POCTemplate

# Configurar logging
logger = logging.getLogger(__name__)


class CPFValidatorPOC(POCTemplate):
    """POC para validação de CPF"""
    
    def __init__(self):
        """Inicializar validador de CPF"""
        super().__init__()
        self.name = "Validador de CPF POC"
        self.cpfs_teste = [
            "123.456.789-09",
            "111.444.777-35",
            "000.000.000-00",
            "123.456.789-10"
        ]
    
    def setup(self) -> bool:
        """Configurar validador"""
        try:
            logger.info("Configurando validador de CPF...")
            # Aqui você poderia carregar regras de validação, etc.
            return True
        except Exception as e:
            logger.error(f"Erro na configuração: {e}")
            return False
    
    def validar_cpf(self, cpf: str) -> bool:
        """Validar um CPF específico"""
        # Remover caracteres especiais
        cpf_limpo = re.sub(r'[^\d]', '', cpf)
        
        # Verificar se tem 11 dígitos
        if len(cpf_limpo) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            return False
        
        # Calcular primeiro dígito verificador
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcular segundo dígito verificador
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verificar se os dígitos calculados coincidem
        return cpf_limpo[-2:] == f"{digito1}{digito2}"
    
    def run(self) -> Dict[str, Any]:
        """Executar validação de CPFs"""
        try:
            logger.info("Executando validação de CPFs...")
            
            resultados = {}
            for cpf in self.cpfs_teste:
                valido = self.validar_cpf(cpf)
                resultados[cpf] = valido
                logger.info(f"CPF {cpf}: {'VÁLIDO' if valido else 'INVÁLIDO'}")
            
            result = {
                "status": "success",
                "message": "Validação de CPFs concluída",
                "data": {
                    "cpfs_validados": len(self.cpfs_teste),
                    "resultados": resultados
                }
            }
            
            logger.info("Validação concluída com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": {}
            }
    
    def cleanup(self):
        """Limpar recursos"""
        try:
            logger.info("Limpando validador...")
            # Aqui você poderia limpar arquivos temporários, etc.
            logger.info("Limpeza concluída")
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")


def main():
    """Função principal"""
    poc = CPFValidatorPOC()
    
    try:
        if not poc.setup():
            logger.error("Falha na configuração")
            return
        
        result = poc.run()
        
        print(f"\nResultado da POC - Validador de CPF:")
        print(f"Status: {result['status']}")
        print(f"Mensagem: {result['message']}")
        
        if result['status'] == 'success':
            print(f"\nCPFs validados: {result['data']['cpfs_validados']}")
            print("Resultados:")
            for cpf, valido in result['data']['resultados'].items():
                status = "VÁLIDO" if valido else "INVÁLIDO"
                print(f"  {cpf}: {status}")
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    
    finally:
        poc.cleanup()


if __name__ == "__main__":
    main()
