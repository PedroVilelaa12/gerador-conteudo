# 📱 Como Usar o LinkedIn no Sistema

## ✅ **ESTÁ TUDO PRONTO!**

Não precisa rodar `linkedin_poc.py` toda vez! Esse arquivo é apenas para **teste**.

---

## 🎯 **COMO FUNCIONA NA PRÁTICA:**

### **Você NÃO precisa rodar `linkedin_poc.py` manualmente!**

O sistema está **integrado no Streamlit**. Use a interface web:

---

## 🚀 **FLUXO NORMAL DE USO:**

### **1. Inicie o Streamlit:**

```bash
poetry run python scripts/run_streamlit.py
```

### **2. Acesse:** http://localhost:8501

### **3. Gere uma imagem:**
- Vá em "🎨 Gerar Conteúdo"
- Digite um prompt
- Clique em "🚀 Gerar Conteúdo"

### **4. Aprove e publique no LinkedIn:**
- Vá em "✅ Aprovar Conteúdo"
- Você verá a imagem gerada
- Marque a checkbox **"LinkedIn"**
- Clique em "✅ Aprovar e Publicar"

### **5. Pronto!** O post será publicado automaticamente no LinkedIn!

---

## 📋 **QUANDO RODAR `linkedin_poc.py`:**

O arquivo `pocs/linkedin_poc.py` é apenas para:
- ✅ **Teste rápido** - Verificar se está funcionando
- ✅ **Debug** - Quando algo não funciona
- ✅ **Desenvolvimento** - Testar mudanças no código

**Para uso normal, NÃO precisa rodar!**

---

## 🔄 **O QUE ACONTECE AUTOMATICAMENTE:**

Quando você usa a interface Streamlit:

1. **Gera imagem** → Google Gemini cria a imagem
2. **Você aprova** → Marca LinkedIn
3. **Sistema publica** → Chama automaticamente a POC do LinkedIn
4. **Post no LinkedIn** → Aparece no seu perfil!

**Tudo automático!** Você não precisa rodar nenhum script manualmente.

---

## 🎯 **DIFERENÇA:**

| Ação | Quando Fazer |
|------|--------------|
| **Rodar `linkedin_poc.py`** | Apenas para **teste/debug** |
| **Usar Streamlit** | **Uso normal** - gera e publica tudo |

---

## 📊 **RESUMO:**

```
✅ Token configurado (uma vez)
✅ URN obtido automaticamente
✅ Post publicado com sucesso

Uso Normal:
  1. Abrir Streamlit
  2. Gerar conteúdo
  3. Aprovar e marcar LinkedIn
  4. Publicar automaticamente ✅

Não precisa:
  ❌ Rodar linkedin_poc.py toda vez
  ❌ Configurar manualmente
  ❌ Rodar scripts
```

---

## 🎉 **ESTÁ PRONTO PARA USAR!**

Agora é só:
1. Abrir o Streamlit
2. Gerar conteúdo
3. Publicar no LinkedIn pela interface!

**Tudo automático!** 🚀

