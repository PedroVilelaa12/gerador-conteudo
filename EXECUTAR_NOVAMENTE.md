# 🚀 Executar Script do LinkedIn - Passo a Passo Simples

## ⚠️ **ERRO COMUM:**

Você **COLou as instruções** no terminal. Não precisa fazer isso!

**Só execute o COMANDO**, o script vai perguntar o que precisa.

---

## ✅ **O QUE FAZER:**

### **1. Digite APENAS este comando:**

```bash
poetry run python scripts/get_linkedin_token.py
```

**NÃO cole nada mais!** Só esse comando.

---

## 📋 **2. O Script Vai Perguntar:**

Quando você executar, o script vai fazer perguntas uma por uma:

**Pergunta 1:**
```
Digite seu LinkedIn Client ID:
```
**Digite:** `77f34iiy9jmxp8`
**Pressione Enter**

---

**Pergunta 2:**
```
Digite seu LinkedIn Client Secret:
```
**Digite:** `WPL_AP1.KXM3mQxUaGe89ulr.L98H/A==`
**Pressione Enter**

---

**Pergunta 3:**
```
Digite a Redirect URI configurada (ex: http://localhost:8051/callback):
```
**Digite:** `http://localhost:8501/callback`
**Pressione Enter**

---

## 🌐 **3. Navegador Vai Abrir:**

O navegador vai abrir automaticamente com a página do LinkedIn.

**Faça:**
1. Clique em **"Allow"** (Permitir)
2. **AGUARDE** o redirecionamento
3. Copie a **URL completa** da barra de endereços
4. Volte ao terminal

---

## 📋 **4. Cole a URL no Terminal:**

Quando o terminal perguntar:
```
✏️  Cole a URL de redirecionamento aqui:
```

**Cole a URL** (botão direito no terminal ou Shift+Insert)

A URL deve ser algo como:
```
http://localhost:8501/callback?code=AQTxxx...&state=...
```

---

## ✅ **5. Pronto!**

O script vai:
- Extrair o código
- Obter o token
- Salvar no `.env`

---

## 🎯 **RESUMO VISUAL:**

```
Terminal:
  poetry run python scripts/get_linkedin_token.py
  ↓
  Digite Client ID: 77f34iiy9jmxp8
  ↓
  Digite Client Secret: WPL_AP1.KXM3mQxUaGe89ulr.L98H/A==
  ↓
  Digite Redirect URI: http://localhost:8501/callback
  ↓
  Navegador abre → Clique "Allow"
  ↓
  Copie URL completa
  ↓
  Cole no terminal
  ↓
  ✅ Token salvo!
```

---

## ⚠️ **IMPORTANTE:**

- **NÃO cole instruções** no terminal
- **Só execute o comando**
- **Responda as perguntas** quando o script pedir
- **Cole apenas a URL** quando solicitado

---

## 🧪 **DEPOIS DE CONFIGURAR:**

Teste novamente:
```bash
poetry run python pocs/linkedin_poc.py
```

Agora deve funcionar! ✅

