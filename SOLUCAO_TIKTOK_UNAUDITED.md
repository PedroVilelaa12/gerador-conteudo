# ⚠️ Erro TikTok: "unaudited_client_can_only_post_to_private_accounts"

## 🐛 **PROBLEMA:**

Você está recebendo o erro:
```
403 - unaudited_client_can_only_post_to_private_accounts
```

## 📋 **O QUE SIGNIFICA:**

Este erro indica que sua aplicação TikTok está em **modo Sandbox** (não auditada). Aplicações em sandbox têm restrições:

- ✅ **Podem postar apenas em contas PRIVADAS** (`SELF_ONLY`)
- ❌ **NÃO podem postar em contas públicas** (`PUBLIC_TO_EVERYONE`)
- ⚠️ **Tem limitações de funcionalidades**

## ✅ **SOLUÇÃO IMEDIATA:**

O código já está configurado para usar `SELF_ONLY` (privado), mas vamos garantir que está funcionando:

### **Opção 1: Verificar Configuração Atual (Já está correto)**

O código já usa:
```python
self.privacy_level = "SELF_ONLY"  # Contas privadas
```

**✅ Seu vídeo será publicado apenas para você (privado)**

### **Opção 2: Testar com MUTUAL_FOLLOW_FRIENDS**

Você pode tentar usar `MUTUAL_FOLLOW_FRIENDS` que permite seguidores mútuos verem:

```python
self.privacy_level = "MUTUAL_FOLLOW_FRIENDS"
```

**Mas isso ainda pode dar erro em modo Sandbox.**

---

## 🚀 **SOLUÇÃO DEFINITIVA: Passar pela Auditoria do TikTok**

Para postar em **contas públicas**, você precisa:

### **1. Preencher Informações da Aplicação no TikTok Developer Portal:**

1. Acesse: https://developers.tiktok.com/
2. Vá em **"Manage Apps"** → Selecione sua app
3. Preencha TODAS as informações obrigatórias:
   - ✅ **App Information** (nome, descrição, categoria)
   - ✅ **Privacy Policy URL** (obrigatório!)
   - ✅ **Terms of Service URL** (obrigatório!)
   - ✅ **App Icon** (512x512px)
   - ✅ **App Screenshots** (mínimo 3)
   - ✅ **App Description** (mínimo 100 caracteres)

### **2. Submeter para Revisão:**

1. Depois de preencher tudo, vá em **"Submit for Review"**
2. O TikTok vai revisar sua aplicação (pode levar alguns dias)
3. Uma vez aprovada, você poderá postar em contas públicas!

---

## 🔧 **CONFIGURAÇÃO TEMPORÁRIA (Para Testar Agora):**

Você pode modificar o código para garantir que está usando privado:

**Arquivo:** `pocs/tiktok_poc.py`

```python
# Linha ~42
self.privacy_level = "SELF_ONLY"  # Garantir que está privado
```

**OU você pode forçar no `.env`:**

```env
TIKTOK_PRIVACY_LEVEL=SELF_ONLY
```

E modificar o código para ler do `.env`:

```python
self.privacy_level = os.getenv('TIKTOK_PRIVACY_LEVEL', 'SELF_ONLY')
```

---

## 📝 **VERIFICAR ONDE ESTÁ O ERRO:**

O erro está vindo do TikTok quando tenta inicializar o upload. Vamos adicionar mais informações de debug:

O código já mostra:
```
Vídeo: 0.01MB, Chunk: 0.01MB, Chunks: 1
```

Isso significa que o vídeo foi gerado corretamente. O problema é na hora de inicializar o upload no TikTok.

---

## ✅ **TESTAR COM PRIVACIDADE PRIVADA:**

Execute novamente:

```bash
poetry run python pocs/tiktok_poc.py
```

Se o erro persistir mesmo com `SELF_ONLY`, pode ser que:

1. **O app precisa ser reconfigurado** no portal
2. **Os tokens precisam ser regenerados** após configurar privacidade
3. **O TikTok mudou os requisitos** para sandbox

---

## 🎯 **PRÓXIMOS PASSOS:**

### **Se quiser postar PRIVADO (agora):**
- ✅ O código já está configurado para `SELF_ONLY`
- ⚠️ Se ainda der erro, tente regenerar os tokens:
  ```bash
  poetry run python scripts/get_tiktok_token.py
  ```

### **Se quiser postar PÚBLICO (futuro):**
1. ✅ Preencher todas as informações no TikTok Developer Portal
2. ✅ Submeter para revisão
3. ✅ Aguardar aprovação
4. ✅ Depois mudar para `PUBLIC_TO_EVERYONE`

---

## 🔍 **VERIFICAR STATUS DA APP:**

1. Acesse: https://developers.tiktok.com/app/
2. Veja o status da sua app:
   - 🔴 **Sandbox** = Modo de teste (restrições)
   - 🟡 **In Review** = Em revisão
   - 🟢 **Published** = Aprovada (pode postar público)

---

**💡 RESUMO:**
- ✅ Código já está configurado para privado (`SELF_ONLY`)
- ⚠️ Se ainda der erro, regenerar tokens pode ajudar
- 🚀 Para postar público, precisa passar pela auditoria do TikTok

