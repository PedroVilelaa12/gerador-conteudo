# 🔧 Solução: Diferença de Portas no LinkedIn

## 🔍 **PROBLEMA IDENTIFICADO:**

No LinkedIn Developer Portal você tem:
- ✅ `http://localhost:8051/callback`
- ✅ `https://niceasvini.github.io/callback`

Mas o código está tentando usar:
- ❌ `http://localhost:8501/callback` (porta diferente!)

**A porta está diferente: 8051 vs 8501**

---

## ✅ **SOLUÇÃO: DUAS OPÇÕES**

### **OPÇÃO 1: Adicionar Porta 8501 no LinkedIn** (RECOMENDADO)

Se você quer usar a porta **8501**:

#### **Passo a Passo:**

1. **Acesse:** https://www.linkedin.com/developers/apps
2. **Selecione sua app:** "Gerador de Conteúdo IA"
3. **Vá em "Auth"**
4. **Em "Authorized redirect URLs":**
   - Clique no ícone de **editar (lápis)** ao lado do título
   - Clique em **"Add redirect URL"** ou **"+"**
   - Digite: `http://localhost:8501/callback`
   - Clique em **"Update"** ou **"Save"**

5. **Aguarde 1-2 minutos**

6. **Execute o script:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

7. **Quando solicitar Redirect URI, digite:**
   ```
   http://localhost:8501/callback
   ```

#### **Resultado:**

Você terá **3 URLs** configuradas:
- ✅ `http://localhost:8051/callback` (já existente)
- ✅ `http://localhost:8501/callback` (nova - a que você vai usar)
- ✅ `https://niceasvini.github.io/callback` (já existente)

---

### **OPÇÃO 2: Usar Porta 8051 (Já Configurada)**

Se você quer usar a porta **8051** que já está configurada:

#### **Passo a Passo:**

1. **Execute o script:**
   ```bash
   poetry run python scripts/get_linkedin_token.py
   ```

2. **Quando solicitar Redirect URI, digite:**
   ```
   http://localhost:8051/callback
   ```

3. **Pronto!** Já está configurado no LinkedIn.

---

## 🎯 **QUAL OPÇÃO ESCOLHER?**

| Opção | Quando Usar | Vantagem |
|-------|-------------|----------|
| **Opção 1** | Quer usar porta 8501 | Mais flexível, pode usar qualquer porta |
| **Opção 2** | Quer usar porta 8051 | Mais rápido, já está configurado |

**Recomendação:** Se você já estava tentando usar 8501, use a **Opção 1** para adicionar no LinkedIn.

---

## 📋 **RESUMO VISUAL:**

### **Configuração Atual:**
```
LinkedIn Developer Portal:
  ✅ http://localhost:8051/callback
  ✅ https://niceasvini.github.io/callback
```

### **Opção 1 (Adicionar 8501):**
```
LinkedIn Developer Portal:
  ✅ http://localhost:8051/callback
  ✅ http://localhost:8501/callback ← ADICIONAR ESTA
  ✅ https://niceasvini.github.io/callback

Código usa: http://localhost:8501/callback ✅
```

### **Opção 2 (Usar 8051):**
```
LinkedIn Developer Portal:
  ✅ http://localhost:8051/callback ← JÁ EXISTE
  ✅ https://niceasvini.github.io/callback

Código usa: http://localhost:8051/callback ✅
```

---

## ⚡ **AÇÃO RÁPIDA - OPÇÃO 1:**

1. **LinkedIn Developer Portal** → Sua App → **Auth**
2. **Authorized redirect URLs** → Clique no **lápis (editar)**
3. **Add redirect URL** → Digite: `http://localhost:8501/callback`
4. **Update**
5. **Aguarde 1-2 minutos**
6. **Execute:** `poetry run python scripts/get_linkedin_token.py`
7. **Digite:** `http://localhost:8501/callback`

---

## ⚡ **AÇÃO RÁPIDA - OPÇÃO 2:**

1. **Execute:** `poetry run python scripts/get_linkedin_token.py`
2. **Digite:** `http://localhost:8051/callback`
3. **Pronto!**

---

## ✅ **DEPOIS DE ESCOLHER:**

Qualquer uma das opções vai funcionar. O importante é que a porta no LinkedIn seja **igual** à porta que você digitar no script!

