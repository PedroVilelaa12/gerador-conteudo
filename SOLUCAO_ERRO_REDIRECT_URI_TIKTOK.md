# 🔧 Solução: Erro redirect_uri no TikTok

## ❌ **O ERRO QUE VOCÊ ESTÁ VENDO:**

```
Ocorreu um erro
Não foi possível entrar com o TikTok.
...
• redirect_uri
```

**Causa:** A Redirect URI usada pelo script não corresponde exatamente à URL configurada no TikTok Developer Portal.

---

## ✅ **SOLUÇÃO PASSO A PASSO:**

### **PASSO 1: Verificar Redirect URI no TikTok Developer Portal**

1. Acesse: https://developers.tiktok.com/
2. Faça login e vá em "Manage Apps"
3. Selecione sua aplicação "Gerador de Conteúdo"
4. Vá em **"Products"** → **"Login Kit"**
5. Na aba **"Web"**, veja qual Redirect URI está configurada

**DEVE SER EXATAMENTE:**
```
https://niceasvini.github.io/callback.html
```

⚠️ **IMPORTANTE:**
- ✅ Deve começar com `https://` (não `http://`)
- ✅ Deve ser `niceasvini.github.io` (seu domínio GitHub Pages)
- ✅ Deve ter `/callback.html` no final
- ✅ Sem barra final (`/`)
- ✅ Sem espaços

---

### **PASSO 2: Corrigir se Estiver Diferente**

Se a URL no TikTok Portal estiver diferente:

1. **Remova** a URI antiga (se houver)
2. **Adicione** a URI correta:
   ```
   https://niceasvini.github.io/callback.html
   ```
3. **Salve** as alterações
4. **Aguarde** 1-2 minutos

---

### **PASSO 3: Executar o Script com a URL Correta**

Quando executar:

```bash
poetry run python scripts/get_tiktok_token.py
```

E o script perguntar pela Redirect URI, digite:

```
https://niceasvini.github.io/callback.html
```

⚠️ **EXATAMENTE IGUAL** à que está no TikTok Portal!

---

### **PASSO 4: Verificar se Funcionou**

Após colar a URL correta no script:

1. O navegador abrirá
2. Você clicará em "Allow"
3. Você será redirecionado para `https://niceasvini.github.io/callback.html?code=xxx...`
4. A página mostrará a URL completa
5. Copie e cole no terminal
6. Os tokens serão gerados automaticamente

---

## 🔍 **VERIFICAÇÃO RÁPIDA:**

| Local | URL Esperada |
|-------|--------------|
| **TikTok Portal → Login Kit → Web** | `https://niceasvini.github.io/callback.html` |
| **Script get_tiktok_token.py** | `https://niceasvini.github.io/callback.html` |
| **Arquivo .env** | `TIKTOK_REDIRECT_URI=https://niceasvini.github.io/callback.html` |

**TODOS DEVEM SER EXATAMENTE IGUAIS!**

---

## ⚠️ **PROBLEMAS COMUNS:**

### **Erro: "redirect_uri não corresponde"**

**Causa:** URL diferente entre Portal e Script

**Solução:**
1. Verifique qual URL está no TikTok Portal
2. Use EXATAMENTE a mesma URL no script
3. Certifique-se de que não há espaços extras

### **Erro: "URL não é HTTPS"**

**Causa:** TikTok exige HTTPS para GitHub Pages

**Solução:**
- Use `https://` (não `http://`)
- Não use `localhost` (não funciona com GitHub Pages)

---

## ✅ **CHECKLIST:**

- [ ] Redirect URI no TikTok Portal: `https://niceasvini.github.io/callback.html`
- [ ] Redirect URI no script: `https://niceasvini.github.io/callback.html`
- [ ] URLs são exatamente iguais (caractere por caractere)
- [ ] Salvou as alterações no TikTok Portal
- [ ] Aguardou 1-2 minutos após salvar
- [ ] Tentou executar o script novamente

---

## 🎯 **RESUMO:**

1. ✅ Verifique a Redirect URI no TikTok Portal
2. ✅ Use EXATAMENTE a mesma URL no script
3. ✅ Certifique-se de que ambas usam `https://niceasvini.github.io/callback.html`
4. ✅ Execute o script novamente

**A URL deve ser IDÊNTICA em ambos os lugares!**

