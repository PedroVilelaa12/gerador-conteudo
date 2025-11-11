# 🎵 Guia Completo: Configurar TikTok

## 📋 **PASSO A PASSO COMPLETO**

### **PASSO 1: Criar Aplicação no TikTok Developer Portal**

1. **Acesse:** https://developers.tiktok.com/
2. **Faça login** com sua conta TikTok
3. **Vá em "Manage Apps"** (Gerenciar Apps)
4. **Clique em "Create an app"** (Criar app)

5. **Preencha as informações:**
   - **App name:** Nome da sua aplicação (ex: "Gerador de Conteúdo IA")
   - **App description:** Descrição do propósito
   - **Category:** Escolha a categoria apropriada
   - **Platform:** Selecione **Web**

6. **Clique em "Submit"** ou "Create"

---

### **PASSO 2: Adicionar Produtos e Configurar Permissões**

1. **Na página da sua app, vá em "Add products"** (Adicionar produtos)

2. **Adicione o produto "Login Kit":**
   - Clique em "Get started" ou "Add"
   - Configure as permissões necessárias

3. **Adicione o produto "Content Posting API":**
   - Clique em "Get started" ou "Add"
   - Este é essencial para publicar vídeos!

4. **Configure as permissões (scopes):**
   - ✅ `user.info.basic` - Informações básicas do usuário
   - ✅ `video.upload` - Upload de vídeos
   - ✅ `video.publish` - Publicar vídeos

---

### **PASSO 3: Configurar Redirect URI**

1. **Vá em "Settings"** ou "Basic Information"

2. **Na seção "Platform settings":**
   - Encontre **"Redirect URI"** ou **"OAuth redirect URL"**
   - Adicione: `http://localhost:8000/callback`
   - Clique em "Save" ou "Update"

⚠️ **IMPORTANTE:** Deve ser **exatamente** `http://localhost:8000/callback`

---

### **PASSO 4: Anotar Credenciais**

1. **Vá em "Basic Information"** ou "Keys"

2. **Anote:**
   - **Client Key** (chave pública)
   - **Client Secret** (chave secreta - clique em "Show" para ver)

3. **Você vai precisar desses valores!**

---

### **PASSO 5: Obter Tokens via Script**

1. **Execute o script:**
   ```bash
   poetry run python scripts/get_tiktok_token.py
   ```

2. **Quando solicitar, informe:**
   - **Client Key:** (o que você anotou)
   - **Client Secret:** (o que você anotou)
   - **Redirect URI:** `http://localhost:8000/callback`

3. **O navegador abrirá automaticamente**

4. **Autorize no TikTok:**
   - Clique em **"Allow"** ou **"Permitir"**
   - Aguarde o redirecionamento

5. **Copie a URL completa** da barra de endereços
   - Deve ser: `http://localhost:8000/callback?code=xxx...`
   - Mesmo se der erro 404, copie a URL!

6. **Cole no terminal** (botão direito ou Shift+Insert)

7. **Pronto!** O token será salvo automaticamente no `.env`

---

## 📋 **CHECKLIST:**

- [ ] App criada no TikTok Developer Portal
- [ ] Produto "Login Kit" adicionado
- [ ] Produto "Content Posting API" adicionado
- [ ] Permissões configuradas (`user.info.basic`, `video.upload`, `video.publish`)
- [ ] Redirect URI configurada: `http://localhost:8000/callback`
- [ ] Client Key e Client Secret anotados
- [ ] Script executado: `poetry run python scripts/get_tiktok_token.py`
- [ ] Autorização feita no navegador
- [ ] URL de callback copiada e colada no terminal
- [ ] Tokens salvos no `.env`
- [ ] Teste executado com sucesso

---

## ⚠️ **IMPORTANTE: TikTok Precisa de VÍDEO**

**O TikTok só aceita vídeos, não imagens!**

### **Opções:**

1. **Criar vídeo de teste:**
   - Use: `poetry run python scripts/create_test_video.py`
   - Ou forneça um vídeo próprio

2. **Converter imagem para vídeo:**
   - Você precisaria adicionar essa funcionalidade
   - Pode usar bibliotecas como `moviepy` ou `opencv`

3. **Configurar vídeo no `.env`:**
   ```env
   TEST_VIDEO_PATH=caminho/para/seu/video.mp4
   ```

---

## 🧪 **TESTAR:**

Depois de configurar:

```bash
poetry run python pocs/tiktok_poc.py
```

**Resultado esperado:**
```
✅ Configuração do TikTok concluída com sucesso
✅ Vídeo enviado com sucesso para o TikTok
```

---

## 🎯 **USAR NO STREAMLIT:**

O TikTok está integrado na interface! Mas lembre-se:

- ✅ O TikTok precisa de **vídeo** (não imagem)
- ✅ Configure `TEST_VIDEO_PATH` no `.env`
- ✅ Ou converta imagem para vídeo antes de publicar

---

## ❓ **DÚVIDAS FREQUENTES:**

### **P: Preciso de vídeo mesmo para testar?**
**R:** Sim, o TikTok só aceita vídeos. Use o script `create_test_video.py` para criar um.

### **P: Posso publicar imagens no TikTok?**
**R:** Não diretamente. Você precisaria converter a imagem para vídeo primeiro.

### **P: A Redirect URI deve ser exatamente igual?**
**R:** Sim! `http://localhost:8000/callback` deve ser idêntica no TikTok e no código.

---

## ✅ **PRONTO!**

Depois de seguir esses passos, você terá:
- ✅ Tokens configurados
- ✅ Pode fazer upload de vídeos
- ✅ Sistema funcionando completamente

**Happy TikTok Uploading! 🎵**

