# 🚀 Gerador de Conteúdo - Estrutura de POCs

Este projeto contém uma estrutura organizada para desenvolver e testar POCs (Proofs of Concept) em Python, usando **Poetry** para gerenciamento de dependências.

## 📁 Estrutura do Projeto

```
gerador-conteudo/
├── pocs/                    # Diretório das POCs
│   ├── __init__.py
│   ├── template_poc.py     # Template base para novas POCs
│   ├── exemplo_poc.py      # Exemplo de POC (validador de CPF)
│   ├── tiktok_poc.py       # POC para upload no TikTok
│   └── instagram_poc.py    # POC para upload no Instagram
├── tests/                   # Testes automatizados
│   ├── __init__.py
│   └── test_exemplo_poc.py
├── scripts/                 # Scripts utilitários
│   ├── __init__.py
│   ├── run_poc.py          # Script para executar POCs
│   ├── test_social_apis.py # Testar conexões com APIs
│   └── create_test_video.py # Criar vídeos de teste
├── pyproject.toml           # Configuração Poetry
├── poetry.lock              # Lock de dependências
├── env.example              # Exemplo de variáveis de ambiente
├── SETUP_APIS.md           # Guia para configurar APIs
└── README.md                # Este arquivo
```

## 🛠️ Configuração Inicial

### Pré-requisitos
- Python 3.8+
- Poetry instalado

### Instalar Poetry (se necessário)
```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/Mac
curl -sSL https://install.python-poetry.org | python3 -

# Ou via pip
pip install poetry
```

### 1. Configuração automática (Recomendado)
```bash
python scripts/setup_project.py
```

### 2. Configuração manual
```bash
# Instalar dependências básicas
poetry install

# Instalar grupos opcionais
poetry install --with data,api,automation

# Ativar ambiente virtual
poetry shell
```

### 3. Configurar variáveis de ambiente
```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar .env com suas configurações
```

## 🎬 POCs de Redes Sociais

Este projeto inclui POCs para upload automático de vídeos em redes sociais:

### 🎵 TikTok POC
```bash
# Executar upload no TikTok
poetry run python pocs/tiktok_poc.py
```

### 📸 Instagram POC  
```bash
# Executar upload no Instagram
poetry run python pocs/instagram_poc.py
```

### 🔧 Configuração das APIs
1. **Leia o guia completo**: `SETUP_APIS.md`
2. **Configure credenciais**: Copie `env.example` para `.env` e configure as variáveis
3. **Teste conexões**: `poetry run python scripts/test_social_apis.py`
4. **Crie vídeos de teste**: `poetry run python scripts/create_test_video.py`

### 📋 Pré-requisitos para Redes Sociais
- Conta de desenvolvedor no TikTok e Meta/Facebook
- Aplicações registradas nas respectivas plataformas
- Tokens de acesso válidos
- Vídeo de teste (criado automaticamente ou próprio)
- FFmpeg instalado (para criar vídeos de teste)

## 🚀 Como Usar

### Executar uma POC específica
```bash
# Usando o script de execução
poetry run python scripts/run_poc.py exemplo_poc

# Ou usando o comando Poetry
poetry run run-poc exemplo_poc

# Com ambiente ativado
poetry shell
python scripts/run_poc.py exemplo_poc
```

### Listar POCs disponíveis
```bash
poetry run python scripts/run_poc.py
```

### Executar testes
```bash
# Todos os testes
poetry run pytest

# Teste específico
poetry run pytest tests/test_exemplo_poc.py

# Com mais detalhes
poetry run pytest -v
```

## 📝 Criando uma Nova POC

### 1. Copiar o template
```bash
cp pocs/template_poc.py pocs/minha_nova_poc.py
```

### 2. Editar a nova POC
- Modificar a classe para herdar de `POCTemplate`
- Implementar os métodos `setup()`, `run()` e `cleanup()`
- Adicionar sua lógica específica

### 3. Exemplo de estrutura
```python
class MinhaNovaPOC(POCTemplate):
    def __init__(self):
        super().__init__()
        self.name = "Minha Nova POC"
    
    def setup(self) -> bool:
        # Sua configuração aqui
        return True
    
    def run(self) -> Dict[str, Any]:
        # Sua lógica principal aqui
        return {"status": "success", "data": {}}
    
    def cleanup(self):
        # Sua limpeza aqui
        pass
```

## 🧪 Testando POCs

### Estrutura de testes
- Cada POC deve ter testes correspondentes em `tests/`
- Usar pytest para execução
- Testar setup, execução e cleanup

### Exemplo de teste
```python
def test_minha_poc():
    poc = MinhaNovaPOC()
    assert poc.setup() == True
    
    result = poc.run()
    assert result['status'] == 'success'
    
    poc.cleanup()
```

## 📚 Gerenciamento de Dependências

### Adicionar novas dependências
```bash
# Dependência básica
poetry add nome-da-biblioteca

# Dependência de desenvolvimento
poetry add --group dev nome-da-biblioteca

# Dependência de dados
poetry add --group data pandas

# Dependência de API
poetry add --group api fastapi

# Dependência de automação
poetry add --group automation selenium
```

### Grupos de dependências disponíveis
- **dev**: pytest, black, flake8, mypy
- **data**: pandas, numpy
- **api**: fastapi, uvicorn
- **automation**: selenium, beautifulsoup4
- **social**: requests, python-dotenv, pillow (para APIs de redes sociais)

### Atualizar dependências
```bash
# Atualizar todas
poetry update

# Atualizar específica
poetry update nome-da-biblioteca
```

### Ver dependências
```bash
# Listar todas
poetry show

# Listar por grupo
poetry show --tree --only dev
```

## 🔧 Comandos Úteis

### Formatação de código
```bash
poetry run black pocs/ tests/ scripts/
```

### Verificação de qualidade
```bash
poetry run flake8 pocs/ tests/ scripts/
```

### Executar POC com logging detalhado
```bash
poetry run python -u pocs/exemplo_poc.py
```

### Gerenciar ambiente virtual
```bash
# Ativar
poetry shell

# Desativar
exit

# Ver informações
poetry env info
```

## 📋 Checklist para Nova POC

- [ ] Copiar `template_poc.py`
- [ ] Implementar lógica específica
- [ ] Adicionar docstrings e comentários
- [ ] Criar testes correspondentes
- [ ] Testar execução
- [ ] Documentar no README (se necessário)

## 🆘 Solução de Problemas

### Erro de importação
- Verificar se o arquivo `__init__.py` existe
- Verificar se o path está correto
- Usar `poetry run` antes dos comandos Python

### Dependências faltando
```bash
poetry install
poetry install --with dev,data,api,automation
```

### Problemas com Poetry
```bash
# Verificar configuração
poetry check

# Limpar cache
poetry cache clear --all pypi

# Reinstalar dependências
poetry install --sync
```

### Problemas de permissão (Windows)
- Executar PowerShell como administrador
- Verificar políticas de execução de scripts

## 🤝 Contribuindo

1. Criar nova POC seguindo o template
2. Adicionar testes correspondentes
3. Executar testes antes de commitar: `poetry run pytest`
4. Manter documentação atualizada

## 🎯 Vantagens do Poetry

✅ **Gerenciamento inteligente** - Resolve dependências automaticamente  
✅ **Ambientes isolados** - Cada projeto tem seu ambiente virtual  
✅ **Grupos de dependências** - Organiza dependências por propósito  
✅ **Lock file** - Garante reprodutibilidade entre ambientes  
✅ **Integração moderna** - Usa pyproject.toml como padrão  
✅ **Comandos simples** - Interface intuitiva para gerenciar projetos  

---

**Happy coding! 🎉**