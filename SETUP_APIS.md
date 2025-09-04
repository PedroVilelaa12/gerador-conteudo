# Configuração das APIs para Upload de Vídeos

Este documento explica como obter as chaves de API necessárias para usar os scripts de upload de vídeos no TikTok e Instagram.

## 📋 Pré-requisitos

- Conta de desenvolvedor nas respectivas plataformas
- Aplicação registrada em cada plataforma
- Vídeo de teste hospedado publicamente (para Instagram)

## 🎵 TikTok API

### 1. Criar uma Aplicação TikTok for Developers

1. Acesse [TikTok for Developers](https://developers.tiktok.com/)
2. Faça login com sua conta TikTok
3. Vá para "Manage Apps" e clique em "Create an app"
4. Preencha as informações da aplicação:
   - **App name**: Nome da sua aplicação
   - **App description**: Descrição do propósito
   - **Category**: Escolha a categoria apropriada
   - **Platform**: Web

### 2. Configurar Permissões

1. Na página da sua aplicação, vá para "Add products"
2. Adicione o produto **"Login Kit"**
3. Adicione o produto **"Content Posting API"**
4. Configure as permissões necessárias:
   - `user.info.basic`
   - `video.upload`
   - `video.publish`

### 3. Obter Credenciais

1. Anote o **Client Key** e **Client Secret**
2. Configure a **Redirect URI** (ex: `http://localhost:8000/callback`)

### 4. Processo de Autenticação

Para obter o `access_token` e `open_id`, você precisa implementar o fluxo OAuth 2.0:

```python
# URL de autorização
auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={CLIENT_KEY}&scope=user.info.basic,video.upload&response_type=code&redirect_uri={REDIRECT_URI}"

# Após autorização, troque o código pelo token
token_url = "https://open.tiktokapis.com/v2/oauth/token/"
```

### 5. Variáveis de Ambiente

```env
TIKTOK_ACCESS_TOKEN=seu_access_token_aqui
TIKTOK_OPEN_ID=seu_open_id_aqui
```

## 📸 Instagram API (Meta)

### 1. Criar uma Aplicação Facebook

1. Acesse [Meta for Developers](https://developers.facebook.com/)
2. Vá para "Meus Apps" e clique em "Criar App"
3. Escolha o tipo "Consumidor"
4. Preencha as informações básicas

### 2. Configurar Instagram Basic Display

1. Na dashboard do app, adicione o produto **"Instagram Basic Display"**
2. Vá para "Instagram Basic Display" > "Basic Display"
3. Clique em "Create New App"
4. Configure:
   - **Valid OAuth Redirect URIs**: `https://localhost/`
   - **Deauthorize Callback URL**: `https://localhost/`
   - **Data Deletion Request URL**: `https://localhost/`

### 3. Adicionar Conta de Teste

1. Em "Roles" > "Roles", adicione sua conta Instagram como "Instagram Tester"
2. Aceite o convite no app Instagram

### 4. Obter Access Token

#### Método 1: Graph API Explorer
1. Vá para [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Selecione sua aplicação
3. Gere um token com as permissões:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`

#### Método 2: Fluxo OAuth Manual
```bash
# 1. URL de autorização
https://api.instagram.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user_profile,user_media&response_type=code

# 2. Trocar código por token
curl -X POST https://api.instagram.com/oauth/access_token \
  -F client_id={CLIENT_ID} \
  -F client_secret={CLIENT_SECRET} \
  -F grant_type=authorization_code \
  -F redirect_uri={REDIRECT_URI} \
  -F code={CODE}
```

### 5. Obter Instagram Account ID

```bash
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token={ACCESS_TOKEN}"
```

### 6. Variáveis de Ambiente

```env
INSTAGRAM_ACCESS_TOKEN=seu_access_token_aqui
INSTAGRAM_ACCOUNT_ID=seu_account_id_aqui
```

## 🎬 Configuração do Vídeo de Teste

### Requisitos do Vídeo

#### TikTok:
- Formato: MP4, MOV, MPEG, 3GPP, WEBM
- Duração: 3 segundos a 10 minutos
- Tamanho máximo: 4GB
- Resolução: mínimo 480x480, máximo 4096x4096
- Taxa de quadros: máximo 60fps

#### Instagram (Reels):
- Formato: MP4, MOV
- Duração: 3 segundos a 90 segundos
- Tamanho máximo: 1GB
- Resolução: mínimo 500x888, recomendado 1080x1920
- Taxa de quadros: máximo 30fps
- Proporção: 9:16 (vertical)

### Hospedagem do Vídeo (Instagram)

O Instagram API requer que o vídeo esteja hospedado em uma URL pública acessível. Opções:

1. **AWS S3**: Bucket público
2. **Google Cloud Storage**: Bucket público
3. **Cloudinary**: Serviço de mídia
4. **Servidor próprio**: Com HTTPS

```env
TEST_VIDEO_PATH=caminho/local/video_teste.mp4
TEST_VIDEO_URL=https://seu-servidor.com/video_teste.mp4
```

## 🚀 Executando os Scripts

### Instalação das Dependências

```bash
# Instalar dependências do grupo social
poetry install --with social

# Ou instalar todas as dependências
poetry install --with dev,data,api,automation,social
```

### Configuração do Ambiente

1. Copie o arquivo de exemplo:
```bash
cp env.example .env
```

2. Edite o arquivo `.env` com suas credenciais

### Executar TikTok POC

```bash
poetry run python pocs/tiktok_poc.py
```

### Executar Instagram POC

```bash
poetry run python pocs/instagram_poc.py
```

## 🔧 Solução de Problemas

### Erros Comuns

#### TikTok:
- **"Invalid access token"**: Verifique se o token não expirou
- **"Insufficient permissions"**: Certifique-se de ter as permissões corretas
- **"Video format not supported"**: Verifique o formato e tamanho do vídeo

#### Instagram:
- **"Media not ready"**: O vídeo ainda está sendo processado, aguarde
- **"Invalid media URL"**: Verifique se a URL é pública e acessível
- **"Permission denied"**: Verifique as permissões do token

### Logs e Debug

Os scripts incluem logging detalhado. Para debug adicional:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📚 Recursos Adicionais

- [TikTok for Developers Documentation](https://developers.tiktok.com/doc/)
- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)
- [Meta for Developers](https://developers.facebook.com/)

## ⚠️ Limitações e Considerações

### Rate Limits
- **TikTok**: Varia por endpoint, geralmente 100-1000 requests/dia
- **Instagram**: 200 requests/hora por usuário

### Ambiente de Produção
- Use HTTPS para todas as URLs
- Implemente refresh token para tokens de longa duração
- Monitore logs e erros
- Implemente retry logic para falhas temporárias

### Segurança
- Nunca commite tokens no código
- Use variáveis de ambiente
- Rotacione tokens regularmente
- Monitore uso das APIs
