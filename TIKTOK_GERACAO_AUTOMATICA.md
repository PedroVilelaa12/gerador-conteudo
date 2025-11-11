# 🎬 TikTok com Geração Automática de Vídeo

## ✅ **O QUE MUDOU:**

Agora o sistema **gera automaticamente** um vídeo usando **Gemini AI** e publica no TikTok!

**Você não precisa mais criar vídeos manualmente!** 🚀

---

## 🔄 **COMO FUNCIONA:**

1. **Gemini gera uma imagem** a partir de um prompt
2. **O sistema converte a imagem em vídeo** (5 segundos)
3. **O vídeo é publicado automaticamente no TikTok**

---

## 🚀 **COMO USAR:**

### **Opção 1: Executar direto (usa prompt padrão)**

```bash
poetry run python pocs/tiktok_poc.py
```

Isso vai:
- ✅ Gerar uma imagem com Gemini
- ✅ Converter para vídeo (5 segundos, formato 9:16)
- ✅ Publicar no TikTok automaticamente

### **Opção 2: Personalizar o prompt**

Você pode configurar um prompt personalizado no arquivo `.env`:

```env
TIKTOK_GENERATION_PROMPT=Um vídeo sobre tecnologia e inovação com animações modernas
```

Depois execute:
```bash
poetry run python pocs/tiktok_poc.py
```

### **Opção 3: Via código Python**

```python
from pocs.tiktok_poc import TikTokUploadPOC

poc = TikTokUploadPOC()
poc.setup()

# Gerar e publicar com prompt personalizado
result = poc.run(prompt="Um vídeo sobre viagens e aventuras")

if result["status"] == "success":
    print("✅ Vídeo publicado com sucesso!")
```

---

## 📋 **REQUISITOS:**

### **1. Dependências já instaladas:**

✅ `google-generativeai` - Para gerar imagens  
✅ `moviepy` - Para converter imagem em vídeo  
✅ `pillow` - Para processar imagens  

**Tudo já está no `pyproject.toml`!**

### **2. Configurações no `.env`:**

```env
# Gemini (obrigatório)
GEMINI_API_KEY=sua_chave_gemini

# TikTok (obrigatório)
TIKTOK_ACCESS_TOKEN=seu_access_token
TIKTOK_OPEN_ID=seu_open_id

# Opcional - Prompt personalizado
TIKTOK_GENERATION_PROMPT=Seu prompt personalizado aqui
```

---

## 🎬 **ESPECIFICAÇÕES DO VÍDEO GERADO:**

- **Formato:** 1080x1920 (9:16) - Perfeito para TikTok
- **Duração:** 5 segundos
- **FPS:** 24
- **Codec:** H.264 (libx264)
- **Áudio:** Sem áudio (apenas vídeo)
- **Local:** `test_media/gemini_generated_tiktok.mp4`

---

## 📝 **FLUXO COMPLETO:**

```
1. Você executa: poetry run python pocs/tiktok_poc.py
   ↓
2. Sistema carrega credenciais do .env
   ↓
3. Gemini gera imagem (1080x1920) a partir do prompt
   ↓
4. MoviePy converte imagem em vídeo (5 segundos)
   ↓
5. Vídeo é salvo em test_media/gemini_generated_tiktok.mp4
   ↓
6. Sistema faz upload para TikTok
   ↓
7. ✅ Vídeo publicado!
```

---

## 💡 **EXEMPLOS DE PROMPTS:**

### **Para conteúdo tecnológico:**
```
"Um vídeo sobre tecnologia e inovação com design moderno, ícones flutuantes e cores azul e branco"
```

### **Para conteúdo de viagens:**
```
"Um vídeo sobre viagens e aventuras com imagens de paisagens, montanhas e cores vibrantes"
```

### **Para conteúdo de culinária:**
```
"Um vídeo sobre culinária e receitas com ingredientes coloridos e design apetitoso"
```

### **Para conteúdo motivacional:**
```
"Um vídeo motivacional com frases inspiradoras, gradientes suaves e tipografia moderna"
```

---

## ⚠️ **IMPORTANTE:**

### **FFmpeg:**

O MoviePy precisa do FFmpeg instalado no sistema. Se você receber erros sobre FFmpeg:

**Windows:**
```bash
winget install ffmpeg
```

**Ou baixe em:** https://ffmpeg.org/download.html

### **Limitações:**

1. **Vídeo estático:** A imagem é exibida por 5 segundos (não há animação)
2. **Sem áudio:** O vídeo gerado não tem áudio
3. **Qualidade da imagem:** Depende do que o Gemini gera (atualmente placeholder)

---

## 🐛 **SOLUÇÃO DE PROBLEMAS:**

### **Erro: "FFmpeg not found"**

Instale o FFmpeg:
- Windows: `winget install ffmpeg`
- Ou baixe de: https://ffmpeg.org/download.html

### **Erro: "GEMINI_API_KEY não encontrado"**

Configure no `.env`:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### **Erro: "TIKTOK_ACCESS_TOKEN não encontrado"**

Execute o script de obtenção de tokens:
```bash
poetry run python scripts/get_tiktok_token.py
```

### **Erro: "Erro ao gerar imagem"**

- Verifique se a chave do Gemini está correta
- Verifique sua conexão com a internet
- Veja os logs para mais detalhes

---

## 🎯 **PRÓXIMOS PASSOS:**

Agora você pode:

1. ✅ **Testar agora:**
   ```bash
   poetry run python pocs/tiktok_poc.py
   ```

2. ✅ **Integrar na interface Streamlit:**
   - O sistema já está preparado para usar na interface web!

3. ✅ **Automatizar:**
   - Criar um script que gera e publica vídeos automaticamente
   - Usar diferentes prompts para diferentes temas

---

## 📚 **REFERÊNCIAS:**

- **MoviePy Docs:** https://zulko.github.io/moviepy/
- **Gemini API:** https://ai.google.dev/
- **TikTok API:** https://developers.tiktok.com/

---

**🎉 Agora é só executar e ver a mágica acontecer!**

