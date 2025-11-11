# 🤖 Configurar Google Gemini

## 📋 **PASSO A PASSO COMPLETO**

### **PASSO 1: Obter Chave de API do Gemini**

1. **Acesse:** https://aistudio.google.com/app/apikey
2. **Faça login** com sua conta Google
3. **No menu lateral**, clique em **"Get API Keys"** ou **"Chaves de API"**
4. **Clique em "Create API Key"** ou **"Criar chave de API"**
5. **Copie a chave gerada**

---

### **PASSO 2: Adicionar no Arquivo `.env`**

No arquivo `.env` na raiz do projeto, adicione:

```env
GEMINI_API_KEY=sua_chave_gemini_aqui
```

**Substitua `sua_chave_gemini_aqui` pela chave que você copiou.**

---

### **PASSO 3: Instalar Dependências**

Execute:

```bash
poetry install --with ai
```

Ou se já tiver o Poetry configurado:

```bash
poetry add google-generativeai
```

---

## ⚠️ **IMPORTANTE SOBRE GERAÇÃO DE IMAGENS**

### **Limitação Atual:**

O Google Gemini **não possui uma API pública de geração de imagens** como o DALL-E da OpenAI.

**O que este sistema faz:**
1. ✅ Usa Gemini para **melhorar e enriquecer** o prompt de texto
2. ✅ Gera uma **imagem placeholder** para desenvolvimento/teste

**Para produção, você tem 3 opções:**

### **Opção 1: Usar Vertex AI Imagen** (Recomendado para produção)

1. Criar conta no Google Cloud Platform
2. Ativar Vertex AI Imagen API
3. Integrar com a API do Imagen

### **Opção 2: Usar Outro Serviço de Geração de Imagens**

- Stability AI
- Midjourney API (quando disponível)
- Outros serviços

### **Opção 3: Usar Gemini Apenas para Melhorar Prompts**

- Gemini melhora o prompt
- Você envia o prompt melhorado para outro serviço
- Ou usa manualmente em ferramentas como DALL-E, Midjourney, etc.

---

## 🧪 **TESTAR:**

Depois de configurar:

```bash
poetry run python pocs/ai_generation/gemini_image_poc.py
```

**Resultado esperado:**
```
✅ Configuração do Gemini concluída com sucesso
✅ Prompt melhorado pelo Gemini: [prompt detalhado]
✅ Imagem placeholder criada
```

---

## 📝 **EXEMPLO DE ARQUIVO `.env`:**

```env
# Google Gemini API
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Outras configurações...
TIKTOK_ACCESS_TOKEN=seu_token
LINKEDIN_ACCESS_TOKEN=seu_token
# etc...
```

---

## 🔗 **LINKS ÚTEIS:**

- **Google AI Studio:** https://aistudio.google.com/
- **Documentação Gemini:** https://ai.google.dev/
- **Vertex AI Imagen:** https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview

---

## 🆘 **RESOLVER PROBLEMAS:**

### **Erro: "GEMINI_API_KEY não encontrado"**

✅ **Solução:** Verifique se o arquivo `.env` existe e contém `GEMINI_API_KEY=...`

### **Erro: "Biblioteca google-generativeai não instalada"**

✅ **Solução:** Execute `poetry add google-generativeai` ou `poetry install --with ai`

### **Erro: "Invalid API key"**

✅ **Solução:** 
1. Verifique se a chave está correta no `.env`
2. Verifique se não há espaços antes ou depois da chave
3. Obtenha uma nova chave em https://aistudio.google.com/app/apikey

---

## ✅ **CHECKLIST:**

- [ ] Chave de API obtida em https://aistudio.google.com/app/apikey
- [ ] `GEMINI_API_KEY` adicionada no arquivo `.env`
- [ ] Dependências instaladas (`poetry install --with ai`)
- [ ] Teste executado com sucesso
- [ ] Entendeu as limitações sobre geração de imagens

---

## 💡 **NOTA FINAL:**

Esta migração de OpenAI para Gemini mantém a mesma interface do código, mas:

- **Gemini é excelente** para melhorar prompts e processar texto
- **Para geração de imagens**, considere integrar Vertex AI Imagen ou outro serviço
- **O código atual** funciona como placeholder para desenvolvimento

Para produção real de geração de imagens, você precisará integrar com Vertex AI Imagen ou manter outro serviço de geração de imagens.

