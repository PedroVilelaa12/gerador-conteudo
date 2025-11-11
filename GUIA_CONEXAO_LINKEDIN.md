# 🔗 Guia Passo a Passo: Conectar LinkedIn

## 🚨 **PROBLEMA RESOLVIDO**

O erro que você recebeu:
```
error=unauthorized_scope_error
error_description=Scope "r_emailaddress" is not authorized for your application
```

**Causa:** Os escopos `r_emailaddress` e `r_liteprofile` foram **descontinuados** pelo LinkedIn. Agora precisamos usar apenas `w_member_social` para publicar posts.

---

## 📋 **PASSO A PASSO COMPLETO**

### **PASSO 1: Configurar Aplicação no LinkedIn Developer Portal**

1. **Acesse:** https://www.linkedin.com/developers/apps
2. **Faça login** com sua conta LinkedIn
3. **Clique em "Create app"** (ou selecione sua app existente)

4. **Preencha os dados:**
   - **App name:** Nome da sua aplicação
   - **LinkedIn Page:** Selecione uma página (ou seu perfil pessoal)
   - **Privacy Policy URL:** (pode usar https://niceasvini.github.io/privacidade.html)
   - **App Logo:** Upload de logo (opcional)

5. **Clique em "Create app"**

### **PASSO 2: Configurar Produtos e Permissões**

1. **Na página da sua app, vá para a aba "Products"**

2. **Adicione o produto:**
   - Clique em "**Get access**" no produto **"Share on LinkedIn"**
   - Isso dará acesso à API de postagem

3. **Configure as URLs de redirecionamento:**
   - Vá para a aba **"Auth"**
   - Em **"Redirect URLs"**, adicione:
     ```
     http://localhost:8051/callback
     https://localhost/
     ```
   - Clique em **"Update"**

4. **Anote suas credenciais:**
   - Na aba **"Auth"**, você verá:
     - **Client ID** (ex: `77f34iiy9jmxp8`)
     - **Client Secret** (clique em "Show" para ver)

### **PASSO 3: Configurar no Sistema**

1. **Abra o terminal na pasta do projeto**

2. **Execute o script:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

3. **Siga as instruções:**
   - Digite o **Client ID** quando solicitado
   - Digite o **Client Secret** quando solicitado
   - Digite a **Redirect URI**: `http://localhost:8051/callback`
   - O navegador abrirá automaticamente

### **PASSO 4: Autorizar no LinkedIn**

1. **No navegador que abriu:**
   - Você verá a página de autorização do LinkedIn
   - Clique em **"Allow"** para autorizar

2. **Você será redirecionado para:**
   ```
   http://localhost:8051/callback?code=AQTxxx...&state=random_state_string
   ```

3. **IMPORTANTE:** Se você ver erro 404 (página não encontrada), **NÃO TEM PROBLEMA!**
   - Copie a **URL completa** da barra de endereços
   - Cole no terminal quando solicitado

### **PASSO 5: Finalizar Configuração**

1. **Cole a URL completa no terminal**

2. **O script vai:**
   - Extrair o código de autorização
   - Trocar pelo access_token
   - Salvar automaticamente no arquivo `.env`

3. **Você verá:**
   ```
   ✅ Tokens obtidos com sucesso!
   ✅ LINKEDIN_ACCESS_TOKEN salvo no arquivo .env
   ```

### **PASSO 6: Verificar Configuração**

1. **Abra o arquivo `.env`** na raiz do projeto

2. **Verifique se contém:**
   ```env
   LINKEDIN_ACCESS_TOKEN=AQTxxx...
   LINKEDIN_CLIENT_ID=77f34iiy9jmxp8
   LINKEDIN_CLIENT_SECRET=seu_secret_aqui
   ```

3. **Teste a conexão:**
   ```bash
   poetry run python pocs/linkedin_poc.py
   ```

---

## 🔧 **SOLUÇÃO DO ERRO QUE VOCÊ TEVE**

### **Problema:**
```
error=unauthorized_scope_error
Scope "r_emailaddress" is not authorized
```

### **Solução:**
✅ **Removemos os escopos antigos** (`r_liteprofile`, `r_emailaddress`)
✅ **Usamos apenas** `w_member_social` (que é o necessário para publicar)
✅ **Atualizamos o script** para usar o escopo correto

### **URL Correta Agora:**
```
https://www.linkedin.com/oauth/v2/authorization?
  response_type=code
  &client_id=77f34iiy9jmxp8
  &redirect_uri=http://localhost:8051/callback
  &scope=w_member_social
  &state=123456
```

---

## ⚠️ **IMPORTANTE: Redirect URI**

O erro também pode ocorrer se a Redirect URI não estiver configurada corretamente:

1. **No LinkedIn Developer Portal:**
   - Vá em **"Auth"** → **"Redirect URLs"**
   - Certifique-se de que está cadastrada **exatamente** assim:
     ```
     http://localhost:8051/callback
     ```
   - Deve ser **idêntica** à URL que você usa na autorização

2. **Não funciona:**
   - ❌ `http://localhost:8051/callback/` (barra no final)
   - ❌ `http://localhost:8051/callbacks` (plural)
   - ❌ `https://localhost:8051/callback` (https ao invés de http)

3. **Funciona:**
   - ✅ `http://localhost:8051/callback`
   - ✅ `https://localhost/` (alternativa)

---

## 📝 **CHECKLIST RÁPIDO**

- [ ] App criada no LinkedIn Developer Portal
- [ ] Produto "Share on LinkedIn" adicionado
- [ ] Redirect URI configurada: `http://localhost:8051/callback`
- [ ] Client ID e Client Secret anotados
- [ ] Script executado: `poetry run python scripts/get_linkedin_token.py`
- [ ] Autorização feita no navegador
- [ ] URL de callback copiada e colada no terminal
- [ ] Token salvo no `.env`
- [ ] Teste executado com sucesso

---

## 🆘 **PROBLEMAS COMUNS**

### **1. "Redirect URI mismatch"**
**Solução:** Verifique se a Redirect URI no Developer Portal é **exatamente igual** à URL usada no código.

### **2. "Invalid client_id"**
**Solução:** Verifique se o Client ID está correto (sem espaços extras).

### **3. "Invalid scope"**
**Solução:** Certifique-se de que adicionou o produto "Share on LinkedIn" na sua app.

### **4. Página 404 ao redirecionar**
**Solução:** Normal! Apenas copie a URL completa da barra de endereços.

---

## ✅ **PRONTO!**

Depois de seguir esses passos, você terá:
- ✅ Token de acesso configurado
- ✅ Pode publicar posts no LinkedIn
- ✅ Sistema funcionando completamente

**Teste publicando um post:**
```bash
poetry run python pocs/linkedin_poc.py
```

