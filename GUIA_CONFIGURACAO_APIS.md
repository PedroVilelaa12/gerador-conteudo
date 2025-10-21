# 🔑 Guia de Configuração das APIs Sociais

## 🚀 **CONFIGURAÇÃO AUTOMÁTICA (RECOMENDADO)**

```bash
# Execute o script principal que te guia por tudo:
poetry run python scripts/setup_social_apis.py
```

## 📋 **CONFIGURAÇÃO MANUAL**

### **1. 🤖 OpenAI (Para Geração de Imagens)**

**Mais Fácil - Só precisa da chave API:**

1. Acesse: https://platform.openai.com/
2. Crie conta ou faça login
3. Vá em "API Keys" → "Create new secret key"
4. Copie a chave (começa com `sk-`)
5. Cole no seu `.env`:
```env
OPENAI_API_KEY=sk-sua_chave_aqui
```

### **2. 🎵 TikTok (Para Publicação)**

**Configuração Completa:**

1. **Criar App no TikTok:**
   - Acesse: https://developers.tiktok.com/
   - "Manage Apps" → "Create an app"
   - Preencha: Nome, descrição, categoria
   - Platform: Web

2. **Configurar Permissões:**
   - "Add products" → Adicione:
     - Login Kit
     - Content Posting API
   - Configure permissões:
     - `user.info.basic`
     - `video.upload`
     - `video.publish`

3. **Obter Tokens:**
```bash
poetry run python scripts/get_tiktok_token.py
```

### **3. 📸 Instagram (Para Publicação)**

**Configuração Completa:**

1. **Criar App no Facebook:**
   - Acesse: https://developers.facebook.com/
   - "Meus Apps" → "Criar App"
   - Tipo: Consumidor

2. **Configurar Instagram:**
   - Adicione produto: "Instagram Basic Display"
   - Configure URLs:
     - Valid OAuth Redirect URIs: `https://localhost/`
     - Deauthorize Callback URL: `https://localhost/`

3. **Obter Tokens:**
```bash
poetry run python scripts/get_instagram_token.py
```

### **4. 💼 LinkedIn (Para Publicação)**

**Configuração Completa:**

1. **Criar App no LinkedIn:**
   - Acesse: https://developer.linkedin.com/
   - "My Apps" → "Create App"
   - Conecte com uma página LinkedIn

2. **Configurar Produtos:**
   - Adicione:
     - Share on LinkedIn
     - Sign In with LinkedIn using OpenID Connect

3. **Obter Tokens:**
```bash
poetry run python scripts/get_linkedin_token.py
```

## 🎯 **CONFIGURAÇÃO MÍNIMA PARA TESTAR**

**Se você quer testar rapidamente, configure apenas:**

1. **OpenAI** (para gerar imagens)
2. **Uma rede social** (TikTok, Instagram ou LinkedIn)

**Exemplo mínimo:**
```env
# Só OpenAI
OPENAI_API_KEY=sk-sua_chave_aqui

# Só TikTok
TIKTOK_ACCESS_TOKEN=seu_token_aqui
TIKTOK_OPEN_ID=seu_open_id_aqui
```

## 🚀 **APÓS CONFIGURAR**

### **1. Testar o Sistema:**
```bash
# Iniciar interface web
poetry run python scripts/run_streamlit.py

# Acessar: http://localhost:8501
```

### **2. Para Instagram (se configurado):**
```bash
# Iniciar servidor local para URLs públicas
poetry run python scripts/start_local_server.py
```

### **3. Fluxo de Uso:**
1. **Gerar Conteúdo**: Crie imagens com IA
2. **Aprovar**: Revise e edite descrições
3. **Publicar**: Escolha plataformas e publique
4. **Monitorar**: Acompanhe métricas

## ❓ **DÚVIDAS FREQUENTES**

### **P: Preciso configurar todas as APIs?**
**R:** Não! Configure apenas as que quiser usar. O sistema funciona com qualquer combinação.

### **P: Posso configurar depois?**
**R:** Sim! Você pode configurar as APIs quando quiser. O sistema detecta automaticamente o que está configurado.

### **P: Instagram precisa de URL pública?**
**R:** Sim, mas você pode usar o servidor local que criei ou ngrok.

### **P: Quanto custa?**
**R:** 
- **OpenAI**: ~$0.02-0.08 por imagem
- **APIs Sociais**: Gratuitas (com limites)
- **AWS S3**: Não necessário (sistema funciona sem)

## 🆘 **PROBLEMAS COMUNS**

### **Erro de Token Inválido:**
- Verifique se copiou o token completo
- Tokens podem expirar, gere um novo

### **Erro de Permissões:**
- Verifique se configurou as permissões corretas na plataforma
- Para TikTok: precisa de Content Posting API
- Para Instagram: precisa de Instagram Basic Display

### **Erro de Redirect URI:**
- Use exatamente: `https://localhost/` para Instagram/LinkedIn
- Use exatamente: `http://localhost:8000/callback` para TikTok

## 🎉 **PRONTO!**

Depois de configurar, você terá um sistema completo de:
- ✅ **Geração de imagens** com IA
- ✅ **Aprovação humana** via interface web
- ✅ **Publicação automática** nas redes sociais
- ✅ **Coleta de métricas** e analytics

**Happy Content Automation! 🚀**
