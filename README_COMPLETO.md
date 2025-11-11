# 🚀 Sistema de Automação de Conteúdo com IA

Este projeto é um **sistema completo de automação de conteúdo** que gera imagens usando IA, permite aprovação humana e publica automaticamente em múltiplas redes sociais (TikTok, Instagram, LinkedIn), coletando métricas de performance.

## 🎯 **O QUE O SISTEMA FAZ**

### **Fluxo Completo:**
1. **🎨 Geração de Conteúdo**: Cria imagens usando Google Gemini (melhora prompts e gera imagens)
2. **☁️ Armazenamento**: Salva em AWS S3 com URLs públicas (opcional)
3. **✅ Aprovação Humana**: Interface Streamlit para revisar e aprovar
4. **📱 Publicação Automática**: Publica em TikTok, Instagram e LinkedIn
5. **📊 Coleta de Métricas**: Monitora likes, comentários, visualizações
6. **📈 Dashboard**: Visualiza performance e analytics

## 🏗️ **Arquitetura do Sistema**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Google Gemini │───▶│   AWS S3        │───▶│   Streamlit UI  │
│   (Geração IA)  │    │   (Storage)     │    │   (Aprovação)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SQLite DB     │◀───│   APIs Sociais  │◀───│   Publicação    │
│   (Métricas)    │    │   (TikTok/IG/LI)│    │   Automática    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 **Estrutura do Projeto**

```
gerador-conteudo/
├── 📁 pocs/                          # POCs (Proofs of Concept)
│   ├── 📁 ai_generation/             # Geração de conteúdo por IA
│   │   └── gemini_image_poc.py       # POC Google Gemini
│   ├── 📁 storage/                   # Armazenamento em nuvem
│   │   └── aws_s3_poc.py            # POC AWS S3
│   ├── 📁 metrics/                   # Coleta de métricas
│   │   └── social_metrics_poc.py     # POC métricas sociais
│   ├── template_poc.py               # Template base
│   ├── exemplo_poc.py                # Exemplo (validação CPF)
│   ├── tiktok_poc.py                 # Upload TikTok
│   └── instagram_poc.py              # Upload Instagram
├── 📁 web_interface/                 # Interface web
│   └── streamlit_app.py              # App Streamlit principal
├── 📁 database/                      # Banco de dados
│   └── models.py                     # Modelos SQLAlchemy
├── 📁 storage/                       # Armazenamento local
├── 📁 apps/                          # Aplicações principais
├── 📁 scripts/                       # Scripts utilitários
│   ├── run_poc.py                    # Executor de POCs
│   ├── run_streamlit.py              # Executor Streamlit
│   ├── setup_project.py              # Setup automático
│   ├── test_social_apis.py           # Teste APIs sociais
│   └── create_test_video.py          # Criador de vídeos teste
├── 📁 tests/                         # Testes automatizados
├── pyproject.toml                    # Configuração Poetry
├── env.example                       # Variáveis de ambiente
├── SETUP_APIS.md                     # Guia setup APIs
└── README_COMPLETO.md                # Este arquivo
```

## 🚀 **Instalação e Configuração**

### **1. Pré-requisitos**
- Python 3.8+
- Poetry
- FFmpeg (para vídeos de teste)

### **2. Instalação Automática**
```bash
# Clonar o repositório
git clone <seu-repositorio>
cd gerador-conteudo

# Configuração automática
python scripts/setup_project.py
```

### **3. Instalação Manual**
```bash
# Instalar dependências básicas
poetry install

# Instalar grupos específicos
poetry install --with ai,web,database,social

# Ativar ambiente
poetry shell
```

### **4. Configurar Variáveis de Ambiente**
```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar com suas credenciais
nano .env
```

## 🔑 **Configuração das APIs**

### **Google Gemini (Geração de Imagens)**
1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Faça login e crie uma API key
3. Configure no `.env`:
```env
GEMINI_API_KEY=sua_chave_gemini_aqui
```

**⚠️ NOTA:** Veja `CONFIGURAR_GEMINI.md` para detalhes sobre limitações e opções de produção.

### **AWS S3 (Armazenamento)**
1. Crie conta AWS
2. Configure bucket S3
3. Configure no `.env`:
```env
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
S3_BUCKET_NAME=seu-bucket
AWS_REGION=us-east-1
```

### **TikTok API**
1. Acesse [TikTok for Developers](https://developers.tiktok.com/)
2. Crie aplicação
3. Configure no `.env`:
```env
TIKTOK_ACCESS_TOKEN=seu_token
TIKTOK_OPEN_ID=seu_open_id
```

### **Instagram API**
1. Acesse [Meta for Developers](https://developers.facebook.com/)
2. Configure Instagram Basic Display
3. Configure no `.env`:
```env
INSTAGRAM_ACCESS_TOKEN=seu_token
INSTAGRAM_ACCOUNT_ID=seu_account_id
```

### **LinkedIn API**
1. Acesse [LinkedIn Developers](https://developer.linkedin.com/)
2. Crie aplicação
3. Configure no `.env`:
```env
LINKEDIN_ACCESS_TOKEN=seu_token
LINKEDIN_CLIENT_ID=seu_client_id
LINKEDIN_CLIENT_SECRET=seu_client_secret
```

## 🎮 **Como Usar**

### **1. Executar Interface Web**
```bash
# Método 1: Script dedicado
poetry run python scripts/run_streamlit.py

# Método 2: Direto
poetry run streamlit run web_interface/streamlit_app.py
```

### **2. Acessar Interface**
- Abra: http://localhost:8501
- Navegue pelas páginas:
  - **🏠 Dashboard**: Visão geral do sistema
  - **🎨 Gerar Conteúdo**: Criar imagens com IA
  - **✅ Aprovar Conteúdo**: Revisar e publicar
  - **📊 Métricas**: Analytics e performance
  - **⚙️ Configurações**: Gerenciar APIs

### **3. Fluxo de Trabalho**

#### **Passo 1: Gerar Conteúdo**
1. Vá para "🎨 Gerar Conteúdo"
2. Digite um prompt descritivo
3. Configure tamanho, qualidade e estilo
4. Clique em "🚀 Gerar Conteúdo"
5. Aguarde a IA criar a imagem

#### **Passo 2: Aprovar e Publicar**
1. Vá para "✅ Aprovar Conteúdo"
2. Revise a imagem gerada
3. Edite descrição e hashtags
4. Selecione plataformas (TikTok/Instagram/LinkedIn)
5. Clique em "✅ Aprovar e Publicar"

#### **Passo 3: Monitorar Métricas**
1. Vá para "📊 Métricas"
2. Clique em "🔄 Atualizar Métricas"
3. Visualize performance por plataforma
4. Analise gráficos de engajamento

### **4. Executar POCs Individuais**
```bash
# Listar POCs disponíveis
poetry run python scripts/run_poc.py

# Executar POC específica
poetry run python scripts/run_poc.py gemini_image_poc
poetry run python scripts/run_poc.py aws_s3_poc
poetry run python scripts/run_poc.py social_metrics_poc
```

## 📊 **Funcionalidades Principais**

### **🎨 Geração de Conteúdo**
- ✅ Integração com Google Gemini (melhoria de prompts e geração de imagens)
- ✅ Configuração de tamanho (1024x1024, 1024x1792, 1792x1024)
- ✅ Qualidade (standard, hd)
- ✅ Estilo (vivid, natural)
- ✅ Prompts revisados automaticamente

### **☁️ Armazenamento**
- ✅ Upload automático para AWS S3
- ✅ URLs públicas para APIs sociais
- ✅ Gerenciamento de arquivos
- ✅ Backup e versionamento

### **📱 Publicação Social**
- ✅ TikTok (Content Posting API)
- ✅ Instagram (Graph API)
- ✅ LinkedIn (UGC Posts API)
- ✅ Publicação simultânea
- ✅ Configuração por plataforma

### **📈 Analytics**
- ✅ Coleta automática de métricas
- ✅ Likes, comentários, compartilhamentos
- ✅ Visualizações (quando disponível)
- ✅ Dashboard interativo
- ✅ Gráficos de performance

### **🗄️ Banco de Dados**
- ✅ SQLite (padrão) ou PostgreSQL
- ✅ Modelos SQLAlchemy
- ✅ Histórico completo
- ✅ Relacionamentos entre entidades

## 🛠️ **Tecnologias Utilizadas**

### **Backend**
- **Python 3.8+**: Linguagem principal
- **Poetry**: Gerenciamento de dependências
- **SQLAlchemy**: ORM para banco de dados
- **Requests**: Cliente HTTP para APIs

### **Frontend**
- **Streamlit**: Interface web interativa
- **Plotly**: Gráficos e visualizações
- **CSS**: Estilização personalizada

### **APIs Externas**
- **Google Gemini**: Melhoria de prompts e geração de imagens
- **AWS S3**: Armazenamento em nuvem
- **TikTok API**: Publicação no TikTok
- **Instagram Graph API**: Publicação no Instagram
- **LinkedIn API**: Publicação no LinkedIn

### **Ferramentas**
- **FFmpeg**: Processamento de vídeo
- **Pillow**: Manipulação de imagens
- **OpenCV**: Processamento de imagem
- **MoviePy**: Edição de vídeo

## 💰 **Custos Estimados**

### **Gratuito (MVP)**
- ✅ APIs das redes sociais (limites básicos)
- ✅ SQLite (banco local)
- ✅ Streamlit (execução local)

### **Pago (Produção)**
- 💰 **Google Gemini**: Gratuito (com limites de uso)
- 💰 **AWS S3**: ~$0.023 por GB/mês
- 💰 **Hospedagem**: $5-20/mês (Railway, Render)

### **Escalabilidade**
- 📈 Custos crescem com volume de conteúdo
- 📈 APIs sociais têm limites de taxa
- 📈 Considerar cache e otimizações

## 🔧 **Desenvolvimento**

### **Estrutura de POCs**
Cada POC segue o padrão:
```python
class MinhaPOC(POCTemplate):
    def setup(self) -> bool:
        # Configuração inicial
        return True
    
    def run(self) -> Dict[str, Any]:
        # Lógica principal
        return {"status": "success", "data": {}}
    
    def cleanup(self):
        # Limpeza de recursos
        pass
```

### **Adicionar Nova POC**
1. Copie `pocs/template_poc.py`
2. Implemente sua lógica
3. Adicione testes
4. Documente no README

### **Adicionar Nova Plataforma Social**
1. Crie POC em `pocs/`
2. Implemente métodos de upload
3. Adicione à interface Streamlit
4. Configure métricas

## 🧪 **Testes**

```bash
# Executar todos os testes
poetry run pytest

# Teste específico
poetry run pytest tests/test_exemplo_poc.py

# Com cobertura
poetry run pytest --cov=pocs
```

## 📚 **Documentação Adicional**

- **SETUP_APIS.md**: Guia detalhado para configurar APIs
- **pocs/template_poc.py**: Template para novas POCs
- **database/models.py**: Modelos de banco de dados
- **web_interface/streamlit_app.py**: Interface principal

## 🚨 **Limitações e Considerações**

### **APIs Sociais**
- ⚠️ Rate limits por plataforma
- ⚠️ Políticas de conteúdo
- ⚠️ Aprovação de aplicações
- ⚠️ Tokens de acesso expiram

### **IA e Conteúdo**
- ⚠️ Direitos autorais
- ⚠️ Políticas de deepfake
- ⚠️ Marca d'água obrigatória
- ⚠️ Moderação de conteúdo

### **Escalabilidade**
- ⚠️ Limites de API
- ⚠️ Custos crescentes
- ⚠️ Armazenamento de dados
- ⚠️ Processamento de mídia

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 **Suporte**

- 📧 Email: seu.email@exemplo.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/gerador-conteudo/issues)
- 📖 Wiki: [Documentação](https://github.com/seu-usuario/gerador-conteudo/wiki)

---

**🎉 Happy Content Automation! 🚀**
