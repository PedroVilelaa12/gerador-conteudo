# 🔧 Como Obter o URN do LinkedIn

## ❌ **PROBLEMA:**

O código precisa do **URN** (Uniform Resource Name) do seu perfil para publicar posts, mas não consegue obter automaticamente.

## ✅ **SOLUÇÃO 1: Regerar Token com Escopos Corretos (RECOMENDADO)**

O token atual tem apenas `w_member_social`. Precisamos adicionar `openid profile` para ler o perfil.

### **Passo a Passo:**

1. **Execute o script novamente:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

2. **Quando solicitar, informe:**
   - Client ID: `77f34iiy9jmxp8`
   - Client Secret: (seu secret)
   - Redirect URI: `http://localhost:8501/callback`

3. **Autorize novamente** (vai pedir permissões adicionais)

4. **O novo token terá os escopos:** `w_member_social openid profile`

5. **Teste novamente:**
   ```bash
   poetry run python pocs/linkedin_poc.py
   ```

---

## ✅ **SOLUÇÃO 2: Configurar URN Manualmente**

Se não quiser regenerar o token, você pode obter o URN manualmente e configurar.

### **Como Obter o URN Manualmente:**

1. **Acesse:** https://www.linkedin.com/in/SEU-PERFIL/

2. **Na URL, você verá seu ID ou pode usar:**

3. **Método via API (se tiver outro token de teste):**
   - Use o endpoint: `https://api.linkedin.com/v2/me?projection=(id)`
   - O ID retornado precisa ser formatado como: `urn:li:person:ID`

4. **Configure no `.env`:**
   ```env
   LINKEDIN_PERSON_URN=urn:li:person:SEU_ID_AQUI
   ```

### **Exemplo:**

Se você descobrir que seu ID é `123456789`, adicione no `.env`:
```env
LINKEDIN_PERSON_URN=urn:li:person:123456789
```

---

## ✅ **SOLUÇÃO 3: Usar Script Helper**

Criei um método no código que tenta obter automaticamente, mas se não conseguir, você pode:

1. **Verificar o erro** no terminal (ele mostra qual endpoint falhou)

2. **Usar a Solução 1** (regerar token com escopos corretos)

---

## 📋 **QUAL SOLUÇÃO USAR?**

| Situação | Solução Recomendada |
|----------|-------------------|
| Pode regenerar token | ✅ **Solução 1** (mais simples) |
| Não quer regenerar | ✅ **Solução 2** (configurar manual) |
| Quer automatizar tudo | ✅ **Solução 1** (melhor) |

---

## 🎯 **RECOMENDAÇÃO:**

**Use a Solução 1** - Regerar o token com escopos `w_member_social openid profile`:

1. É mais automático
2. Não precisa descobrir o URN manualmente
3. O código consegue obter automaticamente

---

## 📝 **O QUE MUDA:**

### **Antes:**
- Escopo: `w_member_social` apenas
- Não consegue ler perfil
- Precisa URN manual

### **Depois:**
- Escopos: `w_member_social openid profile`
- Consegue ler perfil automaticamente
- Obtém URN automaticamente

---

## ⚡ **AÇÃO RÁPIDA:**

```bash
# 1. Regerar token com novos escopos
poetry run python scripts/get_linkedin_token.py

# 2. Testar novamente
poetry run python pocs/linkedin_poc.py
```

---

## ✅ **RESULTADO ESPERADO:**

Depois de regenerar com escopos corretos:
```
✅ Configuração do LinkedIn concluída com sucesso
✅ URN obtido via /userinfo: urn:li:person:123456
✅ Post criado com sucesso: urn:li:ugcPost:...
```

