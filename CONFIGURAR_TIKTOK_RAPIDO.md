# 🎵 Configurar TikTok - Resumo Rápido

## 🚀 **AÇÃO RÁPIDA:**

### **1. Criar App no TikTok Developer Portal**

1. Acesse: https://developers.tiktok.com/
2. Login → "Manage Apps" → "Create an app"
3. Preencha e crie a app
4. Anote: **Client Key** e **Client Secret**

### **2. Adicionar Produtos**

Na sua app:
- "Add products" → **Login Kit** (Get started)
- "Add products" → **Content Posting API** (Get started) ⭐ **ESSENCIAL**

### **3. Configurar Redirect URI**

- Settings → **Redirect URI**: `http://localhost:8000/callback`
- Salve

### **4. Executar Script**

```bash
poetry run python scripts/get_tiktok_token.py
```

**Quando perguntar:**
- Client Key: (o que você anotou)
- Client Secret: (o que você anotou)
- Redirect URI: `http://localhost:8000/callback`

### **5. Autorizar e Colar URL**

1. Navegador abre → Clique "Allow"
2. Copie URL completa da barra de endereços
3. Cole no terminal (botão direito)

### **6. Pronto!** ✅

---

## 📋 **CHECKLIST RÁPIDO:**

- [ ] App criada
- [ ] Login Kit adicionado
- [ ] Content Posting API adicionado ⭐
- [ ] Redirect URI: `http://localhost:8000/callback`
- [ ] Script executado
- [ ] Token obtido

---

## ⚠️ **IMPORTANTE:**

O TikTok precisa de **VÍDEO**, não imagem!

**Criar vídeo de teste:**
```bash
poetry run python scripts/create_test_video.py
```

Isso cria: `test_media/tiktok_test.mp4`

**Configurar no `.env`:**
```env
TEST_VIDEO_PATH=test_media/tiktok_test.mp4
```

---

## 🧪 **TESTAR:**

```bash
poetry run python pocs/tiktok_poc.py
```

---

## 📚 **GUIA COMPLETO:**

Veja `GUIA_CONFIGURACAO_TIKTOK.md` para detalhes completos.

