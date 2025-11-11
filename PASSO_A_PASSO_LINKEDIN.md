# 🎯 Passo a Passo Completo - LinkedIn Connection

## ✅ **CHECKLIST ANTES DE COMEÇAR:**

- [ ] Client ID: `77f34iiy9jmxp8` ✅
- [ ] Client Secret: `WPL_AP1.KXM3mQxUaGe89ulr.L98H/A==` ✅
- [ ] Redirect URI configurada no LinkedIn: `http://localhost:8501/callback` ⚠️ **PRECISA CORRIGIR**

---

## 🔧 **PASSO 1: CORRIGIR REDIRECT URI NO LINKEDIN**

1. **Acesse:** https://www.linkedin.com/developers/apps

2. **Faça login** e selecione sua aplicação

3. **Vá na aba "Auth"** (Autenticação)

4. **Na seção "Redirect URLs":**
   
   **ANTES (ERRADO):**
   ```
   http://localhost:8501
   ```
   
   **DEPOIS (CORRETO):**
   ```
   http://localhost:8501/callback
   ```
   
5. **Clique em "Update"**

6. **Aguarde 1-2 minutos** para as mudanças serem aplicadas

---

## 🚀 **PASSO 2: EXECUTAR O SCRIPT**

No terminal, execute:

```bash
poetry run python scripts/get_linkedin_token.py
```

---

## 📝 **PASSO 3: INFORMAR OS DADOS**

Quando o script perguntar, digite:

**1. Client ID:**
```
77f34iiy9jmxp8
```

**2. Client Secret:**
```
WPL_AP1.KXM3mQxUaGe89ulr.L98H/A==
```

**3. Redirect URI:**
```
http://localhost:8501/callback
```

⚠️ **IMPORTANTE:** Deve ser **EXATAMENTE** `http://localhost:8501/callback` (com `/callback` no final)

---

## 🌐 **PASSO 4: AUTORIZAR NO NAVEGADOR**

1. **O navegador abrirá automaticamente**

2. **Você verá a página do LinkedIn pedindo autorização**

3. **Clique em "Allow" (Permitir)**

4. **Você será redirecionado para:**
   ```
   http://localhost:8501/callback?code=AQTxxx...&state=random_state_string
   ```

5. **Mesmo que apareça "404 Not Found" ou erro, NÃO TEM PROBLEMA!**

6. **Copie a URL COMPLETA da barra de endereços:**
   - Selecione tudo na barra de endereços
   - Copie (Ctrl+C)
   - **Deve começar com:** `http://localhost:8501/callback?code=...`

---

## 📋 **PASSO 5: COLAR NO TERMINAL**

1. **Volte para o terminal**

2. **Quando aparecer:**
   ```
   Cole a URL de redirecionamento aqui:
   ```

3. **Cole a URL completa:**
   - Cole (Ctrl+V) a URL que você copiou
   - Deve ser algo como: `http://localhost:8501/callback?code=AQTxxx...`

4. **Pressione Enter**

---

## ✅ **PASSO 6: VERIFICAR SUCESSO**

Se tudo deu certo, você verá:

```
✅ Código obtido: AQTxxx...
🔄 Obtendo tokens...
✅ Tokens obtidos com sucesso!
✅ LINKEDIN_ACCESS_TOKEN salvo no arquivo .env
✅ LINKEDIN_CLIENT_ID salvo no arquivo .env
✅ LINKEDIN_CLIENT_SECRET salvo no arquivo .env

🎉 Configuração do LinkedIn concluída!
```

---

## 🧪 **PASSO 7: TESTAR**

Teste se está funcionando:

```bash
poetry run python pocs/linkedin_poc.py
```

Se funcionar, você verá:
```
✅ Configuração do LinkedIn concluída com sucesso
✅ Post publicado com sucesso no LinkedIn
```

---

## ❌ **ERROS COMUNS E SOLUÇÕES**

### **Erro: "redirect_uri does not match"**

**Causa:** Redirect URI no LinkedIn diferente da usada no código

**Solução:**
1. Verifique no LinkedIn Developer Portal que está: `http://localhost:8501/callback`
2. Verifique no script que está usando: `http://localhost:8501/callback`
3. Devem ser **IDÊNTICAS** (mesma porta, mesmo caminho)

---

### **Erro: "Código de autorização não encontrado"**

**Causa:** Você colou algo que não é uma URL válida

**Solução:**
1. Copie a URL **COMPLETA** da barra de endereços do navegador
2. Deve começar com: `http://localhost:8501/callback?code=...`
3. Não cole apenas `^V` ou parte da URL

---

### **Erro: "404 Not Found" no navegador**

**Isso NÃO é um erro!**

- O LinkedIn redireciona para `localhost:8501/callback`
- Não há servidor rodando nessa porta
- Mas a URL ainda contém o `code` necessário
- **Copie a URL mesmo assim** e cole no terminal

---

## 📞 **RESUMO RÁPIDO**

1. ✅ LinkedIn: Adicione `http://localhost:8501/callback` nas Redirect URLs
2. ✅ Execute: `poetry run python scripts/get_linkedin_token.py`
3. ✅ Digite: Client ID, Secret, e Redirect URI (`http://localhost:8501/callback`)
4. ✅ Autorize no navegador
5. ✅ Copie a URL completa (mesmo com erro 404)
6. ✅ Cole no terminal
7. ✅ Pronto! Token salvo no `.env`

---

## 🎉 **PRONTO!**

Depois desses passos, você terá o token configurado e poderá publicar posts no LinkedIn pela interface Streamlit!

