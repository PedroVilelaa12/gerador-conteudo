#!/usr/bin/env python3
"""
Testes para a POC de validação de CPF
"""

import pytest
import sys
import os

# Adicionar o diretório pai ao path para importar as POCs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocs.exemplo_poc import CPFValidatorPOC


class TestCPFValidatorPOC:
    """Testes para a POC de validação de CPF"""
    
    def setup_method(self):
        """Configurar antes de cada teste"""
        self.poc = CPFValidatorPOC()
    
    def teardown_method(self):
        """Limpar após cada teste"""
        self.poc.cleanup()
    
    def test_setup(self):
        """Testar configuração da POC"""
        assert self.poc.setup() == True
    
    def test_validar_cpf_valido(self):
        """Testar validação de CPF válido"""
        cpf_valido = "123.456.789-09"
        assert self.poc.validar_cpf(cpf_valido) == True
    
    def test_validar_cpf_invalido(self):
        """Testar validação de CPF inválido"""
        cpf_invalido = "123.456.789-10"
        assert self.poc.validar_cpf(cpf_invalido) == False
    
    def test_validar_cpf_todos_iguais(self):
        """Testar CPF com todos os dígitos iguais"""
        cpf_todos_iguais = "000.000.000-00"
        assert self.poc.validar_cpf(cpf_todos_iguais) == False
    
    def test_validar_cpf_formato_invalido(self):
        """Testar CPF com formato inválido"""
        cpf_formato_invalido = "123.456.789"
        assert self.poc.validar_cpf(cpf_formato_invalido) == False
    
    def test_run_poc(self):
        """Testar execução completa da POC"""
        self.poc.setup()
        result = self.poc.run()
        
        assert result['status'] == 'success'
        assert 'cpfs_validados' in result['data']
        assert 'resultados' in result['data']
        assert len(result['data']['resultados']) == 4  # 4 CPFs de teste


if __name__ == "__main__":
    pytest.main([__file__])
