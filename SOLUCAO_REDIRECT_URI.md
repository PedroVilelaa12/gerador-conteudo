# 🔧 Solução: Redirect URI não corresponde

## ❌ **O ERRO:**

```
The redirect_uri does not match the registered value
```

## 🔍 **CAUSA DO PROBLEMA:**

Você configurou no LinkedIn Developer Portal:
```
http://localhost:8501
```

Mas o código está usando:
```
http://localhost:8501/callback
```

**Elas devem ser EXATAMENTE iguais!**

---

## ✅ **SOLUÇÃO:**

### **Opção 1: Adicionar `/callback` no LinkedIn (RECOMENDADO)**

1. **Acesse:** https://www.linkedin.com/developers/apps
2. **Selecione sua aplicação** (com Client ID: `77f34iiy9jmxp8`)
3. **Vá na aba "Auth"**
4. **Em "Redirect URLs":**
   - **Remova:** `http://localhost:8501`
   - **Adicione:** `http://localhost:8501/callback`
   - **Clique em "Update"**

5. **Execute o script novamente:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

### **Opção 2: Remover `/callback` do código (ALTERNATIVA)**

Se você preferir manter `http://localhost:8501` no LinkedIn, preciso atualizar o script para não usar `/callback`.

---

## 📝 **CHECKLIST:**

Quando configurar a Redirect URI no LinkedIn, certifique-se:

- ✅ **Usar HTTP** (não HTTPS): `http://localhost:8501/callback`
- ✅ **Porta correta:** `8501` (ou a que você escolher)
- ✅ **Com `/callback`:** `http://localhost:8501/callback`
- ✅ **Sem espaços** antes ou depois
- ✅ **Exatamente igual** à URL usada no código

**NÃO funciona:**
- ❌ `http://localhost:8501/` (barra no final)
- ❌ `https://localhost:8501/callback` (https ao invés de http)
- ❌ `http://localhost:8501` (sem /callback)
- ❌ `http://localhost:8502/callback` (porta diferente)

**FUNCIONA:**
- ✅ `http://localhost:8501/callback`

---

## 🔄 **DEPOIS DE CORRIGIR:**

1. **Atualize no LinkedIn Developer Portal**
2. **Aguarde 1-2 minutos** (as mudanças podem levar um pouco para aplicar)
3. **Execute o script novamente:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```
4. **Quando solicitar a Redirect URI, digite:**
   ```
   http://localhost:8501/callback
   ```

---

## ⚠️ **SOBRE O ERRO NO TERMINAL:**

No terminal você viu:
```
Cole a URL de redirecionamento aqui: ^V
❌ Código de autorização não encontrado na URL
```

Isso aconteceu porque você colou `^V` (atalho do Windows) ao invés da URL completa.

**Quando o navegador redirecionar:**
1. A URL será algo como: `http://localhost:8501/callback?code=AQTxxx...`
2. **Copie a URL COMPLETA** da barra de endereços
3. **Cole no terminal**

Se der erro 404 (página não encontrada), **NÃO TEM PROBLEMA!** A URL ainda está válida e você só precisa copiar ela.

---

## ✅ **RESUMO RÁPIDO:**

1. **LinkedIn Developer Portal** → Adicione: `http://localhost:8501/callback`
2. **Execute o script** novamente
3. **Use a mesma URI:** `http://localhost:8501/callback`
4. **Copie a URL completa** quando redirecionar (mesmo se der 404)

