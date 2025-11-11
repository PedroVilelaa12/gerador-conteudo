# 🔧 Corrigir Redirect URI no LinkedIn Developer Portal

## ❌ **O ERRO QUE VOCÊ ESTÁ VENDO:**

```
The redirect_uri does not match the registered value
```

Isso significa que a Redirect URI no LinkedIn não está igual à do código.

---

## ✅ **SOLUÇÃO PASSO A PASSO:**

### **PASSO 1: Acessar LinkedIn Developer Portal**

1. **Abra o navegador**
2. **Acesse:** https://www.linkedin.com/developers/apps
3. **Faça login** com sua conta LinkedIn

### **PASSO 2: Selecionar Sua Aplicação**

1. **Encontre sua aplicação** com Client ID: `77f34iiy9jmxp8`
2. **Clique nela** para abrir

### **PASSO 3: Ir para Configurações de Autenticação**

1. **No menu lateral esquerdo**, procure por **"Auth"** ou **"Autenticação"**
2. **Clique em "Auth"**

### **PASSO 4: Verificar/Corrigir Redirect URLs**

Na seção **"Redirect URLs"**, você verá uma lista de URLs.

**O QUE DEVE ESTAR LÁ:**

```
http://localhost:8501/callback
```

**SE NÃO ESTIVER:**

1. **Clique em "Add redirect URL"** ou o botão de adicionar (+)
2. **Digite EXATAMENTE:**
   ```
   http://localhost:8501/callback
   ```
3. **IMPORTANTE:**
   - ✅ Começa com `http://` (não `https://`)
   - ✅ Porta `8501`
   - ✅ Tem `/callback` no final
   - ✅ Sem espaços antes ou depois

4. **Clique em "Update"** ou "Save"

### **PASSO 5: Remover URLs Incorretas (Se Houver)**

Se houver outras URLs como:
- ❌ `http://localhost:8501` (sem `/callback`)
- ❌ `https://localhost:8501/callback` (com `https`)
- ❌ `http://localhost:8051/callback` (porta diferente)

**Remova-as** clicando no ícone de lixeira (🗑️) ao lado de cada uma.

### **PASSO 6: Aguardar Atualização**

1. **Clique em "Update"** ou "Save"
2. **Aguarde 1-2 minutos** para o LinkedIn processar a mudança

---

## 📋 **CHECKLIST DO QUE DEVE ESTAR CONFIGURADO:**

```
✅ Redirect URL: http://localhost:8501/callback
✅ Exatamente igual à URL usada no código
✅ Sem espaços
✅ Porta correta (8501)
✅ Com /callback no final
✅ http:// (não https://)
```

---

## 🔍 **COMO VERIFICAR SE ESTÁ CORRETO:**

1. **No LinkedIn Developer Portal:**
   - Vá em **"Auth"** → **"Redirect URLs"**
   - Deve ter: `http://localhost:8501/callback`

2. **No código:**
   - Quando o script perguntar a Redirect URI
   - Digite: `http://localhost:8501/callback`

3. **Devem ser IDÊNTICAS!**

---

## 🎯 **VISUAL DA CONFIGURAÇÃO CORRETA:**

```
┌─────────────────────────────────────────────┐
│  LinkedIn Developer Portal                   │
│  Auth → Redirect URLs                        │
├─────────────────────────────────────────────┤
│  ✓ http://localhost:8501/callback           │
│                                             │
│  [Add redirect URL]                         │
└─────────────────────────────────────────────┘
```

---

## ⚠️ **PROBLEMAS COMUNS:**

### **Problema 1: URL sem /callback**
```
❌ Configurado: http://localhost:8501
✅ Deve ser: http://localhost:8501/callback
```

### **Problema 2: URL com https**
```
❌ Configurado: https://localhost:8501/callback
✅ Deve ser: http://localhost:8501/callback
```

### **Problema 3: Porta diferente**
```
❌ Configurado: http://localhost:8051/callback
✅ Deve ser: http://localhost:8501/callback
```

### **Problema 4: Espaços extras**
```
❌ Configurado: http://localhost:8501/callback 
                              (espaço no final)
✅ Deve ser: http://localhost:8501/callback
```

---

## 🔄 **DEPOIS DE CORRIGIR:**

1. **Aguarde 1-2 minutos**
2. **Execute o script novamente:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```
3. **Quando solicitar a Redirect URI, digite:**
   ```
   http://localhost:8501/callback
   ```
4. **Agora deve funcionar!** ✅

---

## 📸 **PASSO A PASSO VISUAL:**

1. **Acesse:** https://www.linkedin.com/developers/apps

2. **Selecione sua app**

3. **Clique em "Auth" no menu**

4. **Em "Redirect URLs":**
   - Se já existe, edite para: `http://localhost:8501/callback`
   - Se não existe, adicione: `http://localhost:8501/callback`

5. **Clique em "Update"**

6. **Aguarde 1-2 minutos**

7. **Teste novamente!**

---

## ✅ **TESTE RÁPIDO:**

Depois de corrigir, ao executar o script:
- ✅ Não deve aparecer erro "redirect_uri does not match"
- ✅ Deve abrir a página de autorização do LinkedIn
- ✅ Você deve conseguir clicar em "Allow"
- ✅ Deve redirecionar para `http://localhost:8501/callback?code=...`

