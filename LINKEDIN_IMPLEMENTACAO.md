# 💼 Implementação do LinkedIn no Sistema

## 📍 Onde Está Cada Parte

### ✅ **1. POC de Postagem (Criado Agora)**
**Arquivo:** `pocs/linkedin_poc.py`

**O que faz:**
- Conecta com a API do LinkedIn usando OAuth
- Publica posts de texto simples
- Publica posts com imagens (quando disponível)
- Gerencia autenticação e tokens

**Principais métodos:**
- `setup()` - Configura conexão e obtém tokens
- `create_text_post()` - Cria post apenas com texto
- `create_image_post()` - Cria post com imagem
- `publish_post()` - Método principal de publicação
- `run()` - Executa a publicação

### ✅ **2. Script de Obtenção de Token**
**Arquivo:** `scripts/get_linkedin_token.py`

**O que faz:**
- Ajuda a obter o `access_token` do LinkedIn via OAuth
- Abre navegador para autorização
- Salva tokens no arquivo `.env`

**Como usar:**
```bash
poetry run python scripts/get_linkedin_token.py
```

### ✅ **3. Coleta de Métricas**
**Arquivo:** `pocs/metrics/social_metrics_poc.py`

**Método:** `get_linkedin_metrics(post_id)`

**O que faz:**
- Coleta likes, comentários e shares de posts publicados
- Retorna métricas agregadas

### ✅ **4. Interface Streamlit (Integrado Agora)**
**Arquivo:** `web_interface/streamlit_app.py`

**Onde está integrado:**
- Linha 41: Import da POC do LinkedIn
- Linha 119: Inicialização da POC
- Linha 210-242: Função `publish_to_social_media()` - agora suporta LinkedIn
- Linha 470: Checkbox para selecionar LinkedIn
- Linha 520-523: Lógica de publicação no LinkedIn

**Como usar:**
1. Gere conteúdo na página "🎨 Gerar Conteúdo"
2. Vá para "✅ Aprovar Conteúdo"
3. Marque a checkbox "LinkedIn"
4. Clique em "✅ Aprovar e Publicar"

### ✅ **5. Configuração de Variáveis de Ambiente**
**Arquivo:** `.env`

**Variáveis necessárias:**
```env
LINKEDIN_ACCESS_TOKEN=seu_token_aqui
LINKEDIN_CLIENT_ID=seu_client_id_aqui
LINKEDIN_CLIENT_SECRET=seu_client_secret_aqui
```

## 🔧 Como Funciona

### Fluxo de Publicação:

1. **Usuário aprova conteúdo** → Interface Streamlit
2. **Seleciona LinkedIn** → Checkbox marcado
3. **Sistema chama `publish_to_social_media("linkedin", ...)`**
4. **Função prepara dados:**
   - Extrai texto (descrição + hashtags)
   - Obtém URL da imagem (se houver)
5. **Chama `linkedin_poc.run(text=..., image_url=...)`**
6. **POC publica no LinkedIn:**
   - Autentica com token
   - Cria post de texto ou com imagem
   - Retorna resultado

### Estrutura da POC:

```python
class LinkedInUploadPOC(POCTemplate):
    def setup()           # Configura autenticação
    def get_person_urn()  # Obtém URN do perfil
    def create_text_post()  # Post apenas texto
    def create_image_post() # Post com imagem
    def publish_post()      # Método unificado
    def run()              # Execução principal
```

## 📋 Pré-requisitos

1. **Aplicação LinkedIn criada:**
   - Acesse: https://developer.linkedin.com/
   - Crie uma aplicação
   - Configure produtos: "Share on LinkedIn"

2. **Tokens configurados:**
   - Execute: `poetry run python scripts/get_linkedin_token.py`
   - Ou configure manualmente no `.env`

3. **Permissões necessárias:**
   - `w_member_social` - Para publicar posts
   - `r_liteprofile` - Para obter informações do perfil

## 🚀 Como Testar

### Teste 1: Publicação via Script
```bash
poetry run python pocs/linkedin_poc.py
```

### Teste 2: Publicação via Interface
1. Inicie o Streamlit: `poetry run python scripts/run_streamlit.py`
2. Gere uma imagem
3. Aprove e selecione LinkedIn
4. Publique

## 📝 Notas Importantes

⚠️ **Limitações conhecidas:**
- Upload de imagens requer download e re-upload (implementação básica)
- LinkedIn tem rate limits
- Tokens podem expirar (precisa renovar)

✅ **O que funciona:**
- Posts de texto simples
- Posts com imagens (via URL pública)
- Configuração automática
- Integração completa com interface

## 🔗 Arquivos Relacionados

- `pocs/linkedin_poc.py` - POC principal
- `scripts/get_linkedin_token.py` - Obter tokens
- `web_interface/streamlit_app.py` - Interface (linhas 210-242, 520-523)
- `pocs/metrics/social_metrics_poc.py` - Métricas (linhas 147-188)
- `env.example` - Template de configuração

