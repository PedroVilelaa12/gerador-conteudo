# 🎵 Como Obter ACCESS_TOKEN e OPEN_ID do TikTok

## 📋 **PASSO A PASSO COMPLETO:**

### **PASSO 1: Verificar Redirect URI no TikTok Portal**

**ANTES de executar o script**, verifique a Redirect URI configurada:

1. Acesse: https://developers.tiktok.com/
2. Vá em **"Manage Apps"** → Selecione sua app
3. Vá em **"Products"** → **"Login Kit"**
4. Na aba **"Web"**, veja qual Redirect URI está configurada

**ANOTE ESSA URL!** Você vai precisar usar EXATAMENTE a mesma no script.

---

### **PASSO 2: Executar o Script**

```bash
poetry run python scripts/get_tiktok_token.py
```

---

### **PASSO 3: Informar os Dados**

O script vai perguntar 3 coisas:

#### **1. Client Key:**
```
Digite seu TikTok Client Key: 
```
Cole o seu Client Key (ex: `aweteckbvo88g1r9` ou `sbawdf7o9c1ykst5uf`)

#### **2. Client Secret:**
```
Digite seu TikTok Client Secret: 
```
Cole o seu Client Secret

#### **3. Redirect URI:**
```
Digite a Redirect URI configurada (ex: https://niceasvini.github.io/callback.html): 
```

⚠️ **IMPORTANTE:** Use EXATAMENTE a mesma URL que está no TikTok Portal!

**Se estiver no Portal:**
- `https://niceasvini.github.io/callback.html` → Use essa no script
- `http://localhost:8000/callback` → Use essa no script (se usar localhost)

**Ou simplesmente pressione Enter** para usar o padrão (`https://niceasvini.github.io/callback.html`)

---

### **PASSO 4: Autorizar no Navegador**

1. O navegador abrirá automaticamente com a página de autorização do TikTok
2. **Clique em "Allow"** ou **"Permitir"**
3. Você será redirecionado para a URL do callback (ex: `https://niceasvini.github.io/callback.html?code=xxx...`)
4. **A página mostrará a URL completa** com um botão para copiar

---

### **PASSO 5: Copiar URL de Callback**

1. Na página `callback.html`, clique no botão **"📋 Copiar URL Completa"**
2. Volte ao terminal
3. **Cole a URL** (botão direito → Paste ou Shift+Insert)
4. Pressione Enter

---

### **PASSO 6: Verificar Sucesso**

Se tudo funcionar, você verá:

```
✅ Código obtido: xxx...
🔄 Obtendo tokens...
✅ Tokens obtidos com sucesso!
Access Token: act_xxxxxxxxxxxx...
Open ID: 7123456789abcdefg
Refresh Token: rft_xxxxxxxxxxxx...
✅ TIKTOK_ACCESS_TOKEN salvo no arquivo .env
✅ TIKTOK_OPEN_ID salvo no arquivo .env
✅ TIKTOK_REFRESH_TOKEN salvo no arquivo .env

🎉 Configuração do TikTok concluída!
```

---

## ❌ **SE DER ERRO "redirect_uri":**

### **Causa:**
A Redirect URI no script não corresponde à do TikTok Portal.

### **Solução:**

1. **Verifique no TikTok Portal:**
   - Products → Login Kit → Web → Redirect URI
   - Anote EXATAMENTE qual URL está lá

2. **Use a MESMA URL no script:**
   - Quando o script perguntar a Redirect URI
   - Digite EXATAMENTE a mesma que está no Portal
   - Caractere por caractere, incluindo `https://` ou `http://`

3. **Exemplo:**
   - **Portal:** `https://niceasvini.github.io/callback.html`
   - **Script:** `https://niceasvini.github.io/callback.html` ✅
   - **NÃO:** `https://niceasvini.github.io/callback` ❌
   - **NÃO:** `http://niceasvini.github.io/callback.html` ❌

---

## ✅ **RESULTADO FINAL NO `.env`:**

Após executar com sucesso, seu `.env` terá:

```env
# TikTok
TIKTOK_CLIENT_KEY=aweteckbvo88g1r9
TIKTOK_CLIENT_SECRET=sua_client_secret
TIKTOK_REDIRECT_URI=https://niceasvini.github.io/callback.html
TIKTOK_ACCESS_TOKEN=act_xxxxxxxxxxxx...  ← Gerado automaticamente!
TIKTOK_OPEN_ID=7123456789abcdefg  ← Gerado automaticamente!
TIKTOK_REFRESH_TOKEN=rft_xxxxxxxxxxxx...  ← Gerado automaticamente!
```

---

## 🔄 **RENOVAR TOKENS (Refresh Token):**

O `access_token` expira em 24 horas. Para renovar sem autorizar novamente:

Você pode usar o `refresh_token` para obter um novo `access_token`. Um script será criado para isso no futuro.

Por enquanto, quando o token expirar, basta executar o script novamente.

---

## ✅ **CHECKLIST:**

- [ ] Redirect URI verificada no TikTok Portal
- [ ] Script executado: `poetry run python scripts/get_tiktok_token.py`
- [ ] Client Key informado
- [ ] Client Secret informado
- [ ] Redirect URI informada (igual à do Portal)
- [ ] Autorização feita no navegador
- [ ] URL de callback copiada e colada
- [ ] Tokens obtidos com sucesso
- [ ] Tokens salvos no `.env`

---

## 🎯 **RESUMO:**

1. ✅ Verifique Redirect URI no TikTok Portal
2. ✅ Execute o script
3. ✅ Use EXATAMENTE a mesma Redirect URI nos dois lugares
4. ✅ Autorize no navegador
5. ✅ Copie e cole a URL de callback
6. ✅ Pronto! Tokens salvos automaticamente

**A chave é usar a MESMA Redirect URI em TODOS os lugares!** 🚀

