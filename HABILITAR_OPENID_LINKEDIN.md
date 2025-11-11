# 🔧 Como Habilitar OpenID Connect no LinkedIn

## ❌ **PROBLEMA:**

Você está recebendo o erro:
```
error=unauthorized_scope_error
error_description=Scope "openid" is not authorized for your application
```

**Causa:** O produto "Sign In with LinkedIn using OpenID Connect" não está habilitado na sua aplicação.

---

## ✅ **SOLUÇÃO: Habilitar o Produto**

### **PASSO A PASSO:**

1. **Acesse:** https://www.linkedin.com/developers/apps

2. **Selecione sua aplicação:**
   - App: "Gerador de Conteúdo IA"
   - Client ID: `77f34iiy9jmxp8`

3. **Vá na aba "Products"** (Produtos)

4. **Procure por:**
   - **"Sign In with LinkedIn using OpenID Connect"**
   - Ou **"OpenID Connect"**

5. **Clique em "Get access"** ou **"Request access"**

6. **Leia e aceite os termos** (se solicitado)

7. **Aguarde alguns minutos** para o LinkedIn ativar

---

## 🎯 **O QUE ISSO HABILITA:**

Depois de habilitado, você poderá usar os escopos:
- ✅ `w_member_social` - Publicar posts
- ✅ `openid` - Autenticação OpenID Connect
- ✅ `profile` - Ler informações do perfil (para obter URN)

---

## ⚡ **DEPOIS DE HABILITAR:**

1. **Aguarde 2-5 minutos** para ativação

2. **Execute o script novamente:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

3. **Quando perguntar se quer usar openid+profile:**
   - Digite: `s` (sim)

4. **Complete a autorização**

5. **Teste:**
   ```bash
   poetry run python pocs/linkedin_poc.py
   ```

---

## 🎯 **ALTERNATIVA (Sem OpenID):**

Se você **não quiser habilitar** o OpenID Connect:

1. **Execute o script:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

2. **Quando perguntar se quer usar openid+profile:**
   - Digite: `n` (não)

3. **Configure o URN manualmente no `.env`:**
   ```env
   LINKEDIN_PERSON_URN=urn:li:person:SEU_ID
   ```

4. **Para descobrir seu ID**, você pode:
   - Usar um token de teste para consultar a API
   - Ou usar o script helper: `poetry run python scripts/get_linkedin_urn.py`

---

## 📋 **QUAL OPÇÃO ESCOLHER?**

| Opção | Vantagem | Desvantagem |
|-------|----------|-------------|
| **Habilitar OpenID** | Automático, não precisa descobrir URN | Precisa esperar ativação |
| **Não habilitar** | Funciona imediatamente | Precisa descobrir URN manualmente |

**Recomendação:** **Habilite o OpenID** - é mais fácil e automático.

---

## ✅ **DEPOIS DE HABILITAR:**

Você verá na página "Products":
```
✅ Sign In with LinkedIn using OpenID Connect (Active)
```

Então pode usar os escopos `openid profile` sem problema!

