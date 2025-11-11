# 🎵 Passo a Passo: Preencher Campos no TikTok Developer Portal

## 📋 **VISÃO GERAL DOS CAMPOS**

Você precisa preencher campos em 4 seções:
1. ✅ **App details** (Detalhes da App)
2. ✅ **Products** (Produtos)
3. ✅ **Scopes** (Permissões)
4. ✅ **App review** (Revisão da App)

---

## 📝 **SEÇÃO 1: APP DETAILS (Detalhes da App)**

### **1.1. Category (Categoria)** ✅
**Status:** Você já selecionou "News" - está correto!

### **1.2. Description (Descrição)** ⚠️ **OBRIGATÓRIO**
**O que colocar:**
```
Gerador automático de conteúdo para redes sociais. 
Utiliza inteligência artificial para criar imagens e vídeos 
que são publicados automaticamente no TikTok através da API.
```

**Ou se preferir mais simples:**
```
App para gerar e publicar conteúdo automaticamente no TikTok usando IA.
```

### **1.3. Terms of Service URL** ⚠️ **OBRIGATÓRIO**
**O que colocar:**

Se você não tem um site próprio, pode usar um serviço gratuito ou temporário:

**Opção 1 - GitHub Pages (GRATUITO):**
1. Crie um arquivo `TERMS.md` no seu repositório GitHub
2. Coloque conteúdo simples de termos de serviço
3. Use a URL: `https://seu-usuario.github.io/gerador-conteudo/TERMS.md`

**Opção 2 - URL temporária simples:**
```
https://github.com/seu-usuario/gerador-conteudo/blob/main/TERMS.md
```

**Opção 3 - Criar página simples:**
Se você tem um domínio, pode criar uma página simples.

**Conteúdo básico para o arquivo TERMS.md:**
```markdown
# Terms of Service

Este aplicativo permite gerar e publicar conteúdo no TikTok.

## Uso
O usuário é responsável pelo conteúdo gerado e publicado.

## Limitações
Este é um aplicativo de teste/desenvolvimento.
```

### **1.4. Privacy Policy URL** ⚠️ **OBRIGATÓRIO**
**O que colocar:**

Seguindo o mesmo padrão:

**Opção 1 - GitHub Pages:**
```
https://seu-usuario.github.io/gerador-conteudo/PRIVACY.md
```

**Opção 2 - URL temporária:**
```
https://github.com/seu-usuario/gerador-conteudo/blob/main/PRIVACY.md
```

**Conteúdo básico para PRIVACY.md:**
```markdown
# Privacy Policy

## Dados Coletados
Este aplicativo coleta apenas os dados necessários para autenticação com TikTok.

## Como Usamos
- Dados de autenticação são usados apenas para publicação de conteúdo
- Não compartilhamos dados com terceiros

## Segurança
Seus dados são armazenados localmente e não são transmitidos para servidores externos.
```

### **1.5. Platforms** ⚠️ **OBRIGATÓRIO**
**O que marcar:**
- ✅ **Web** (deve marcar pelo menos este)
- ⬜ Desktop (opcional)
- ⬜ Android (opcional)
- ⬜ iOS (opcional)

**IMPORTANTE:** Marque pelo menos **Web**!

---

## 🛠️ **SEÇÃO 2: PRODUCTS (Produtos)**

### **2.1. Login Kit - Redirect URI** ⚠️ **OBRIGATÓRIO**

**Ação:**
1. Na seção **Login Kit**
2. Clique na aba **"Web"** (não Desktop!)
3. No campo **Redirect URI**, digite:
   ```
   http://localhost:8000/callback
   ```
4. Clique em **"Add"** ou **"Save"**

**IMPORTANTE:**
- ✅ Use aba **"Web"** (não Desktop)
- ✅ URL exata: `http://localhost:8000/callback`
- ✅ Sem espaço no final

### **2.2. Content Posting API - Direct Post**

**O que fazer:**
1. Na seção **Content Posting API**
2. Procure o toggle **"Direct Post"**
3. **LIGUE o toggle** (mude de OFF para ON) ⚠️ **IMPORTANTE!**

**Por quê?**
- **OFF (padrão):** Vídeos vão como rascunho
- **ON:** Vídeos são publicados diretamente ✅

Para automação, você precisa de **Direct Post ON**!

### **2.3. Verify domains** (OPCIONAL - pode pular por enquanto)

Se você vai usar `pull_by_url` (buscar vídeo de URL), precisa verificar.
**Para agora, pode deixar sem verificar.**

---

## 🔐 **SEÇÃO 3: SCOPES (Permissões)**

### **Verificar Scopes Adicionados:**

Você já tem:
- ✅ `user.info.basic` - OK
- ✅ `video.upload` - OK

### **Adicionar Scope Adicional (RECOMENDADO):**

1. Clique em **"+ Add scopes"**
2. Procure e adicione:
   - ✅ `video.publish` - Para publicar vídeos diretamente

**Scopes que você DEVE ter:**
- ✅ `user.info.basic`
- ✅ `video.upload`
- ✅ `video.publish` (adicione se não tiver)

---

## 📋 **SEÇÃO 4: APP REVIEW (Revisão da App)**

### **4.1. Explanation (Explicação)** ⚠️ **OBRIGATÓRIO**

**O que escrever:**

```markdown
Esta aplicação utiliza os seguintes produtos e scopes:

**Login Kit:**
- Permite autenticação de usuários via TikTok
- Utilizado para obter acesso às credenciais necessárias para publicação

**Content Posting API:**
- Permite upload e publicação de vídeos no TikTok
- Os vídeos são gerados automaticamente via IA e publicados na conta do usuário autorizado

**Scopes utilizados:**
- user.info.basic: Obtém informações básicas do perfil do usuário para identificação
- video.upload: Faz upload de vídeos para a conta do usuário
- video.publish: Publica vídeos diretamente no perfil do usuário

**Fluxo de uso:**
1. Usuário autoriza a aplicação via OAuth
2. Sistema gera conteúdo de vídeo usando IA
3. Vídeo é enviado via Content Posting API
4. Vídeo é publicado automaticamente no perfil do usuário
```

**Ou versão mais curta (até 1000 caracteres):**

```markdown
App de automação que gera e publica vídeos no TikTok usando IA.

**Login Kit:** Autenticação OAuth para acesso à conta do usuário.
**Content Posting API:** Upload e publicação automática de vídeos gerados.
**user.info.basic:** Identificação do usuário conectado.
**video.upload:** Envio de vídeos para a conta.
**video.publish:** Publicação direta dos vídeos no perfil.

Fluxo: Usuário autoriza → Sistema gera vídeo via IA → Vídeo é publicado automaticamente.
```

### **4.2. Demo Video** ⚠️ **OBRIGATÓRIO**

**O que fazer:**

1. **Grave um vídeo mostrando:**
   - Você abrindo o navegador
   - Acessando a aplicação
   - Fazendo login/autorização no TikTok
   - Gerando um vídeo/conteúdo
   - Publicando no TikTok
   - Mostrando o vídeo publicado no TikTok

2. **Requisitos do vídeo:**
   - ✅ Formato: `.mp4` ou `.mov`
   - ✅ Máximo: 50MB
   - ✅ Deve mostrar o fluxo COMPLETO end-to-end
   - ✅ Deve mostrar a interface real da sua app

3. **Dicas:**
   - Grave a tela inteira
   - Mostre claramente cada etapa
   - Narre o que está fazendo (opcional)
   - Se possível, mostre o código/publicação no TikTok final

4. **Upload:**
   - Clique em **"Upload"**
   - Selecione seu arquivo de vídeo
   - Aguarde o upload completar

---

## ✅ **CHECKLIST FINAL:**

Antes de clicar em **"Submit for review"**, verifique:

### **App Details:**
- [ ] Category: "News" ✅
- [ ] Description: Preenchida
- [ ] Terms of Service URL: Preenchida
- [ ] Privacy Policy URL: Preenchida
- [ ] Platforms: Web marcado ✅

### **Products:**
- [ ] Login Kit: Redirect URI configurado (`http://localhost:8000/callback`) na aba **Web**
- [ ] Content Posting API: Direct Post **LIGADO** (ON) ✅

### **Scopes:**
- [ ] `user.info.basic` ✅
- [ ] `video.upload` ✅
- [ ] `video.publish` (recomendado)

### **App Review:**
- [ ] Explanation preenchida (explica produtos e scopes)
- [ ] Demo video enviado

---

## 🚀 **DEPOIS DE PREENCHER:**

1. **Clique em "Save"** para salvar o progresso
2. **Revise tudo novamente**
3. **Clique em "Submit for review"** quando estiver pronto

⚠️ **IMPORTANTE:** A revisão pode levar alguns dias. Enquanto isso, você pode usar o ambiente **Sandbox** para testes!

---

## 📚 **NOTAS IMPORTANTES:**

### **URLs de Termos e Privacidade:**
Se você não tem um site ainda, pode:
1. Criar arquivos `.md` no seu repositório GitHub
2. Ou usar um serviço gratuito como GitHub Pages
3. Ou criar uma página simples em qualquer servidor

### **Demo Video:**
- Pode gravar com OBS, QuickTime, ou qualquer gravador de tela
- Mostre o fluxo completo: login → geração → publicação
- O vídeo é essencial para aprovação!

### **Sandbox vs Production:**
- **Sandbox:** Para testes sem aprovação
- **Production:** Requer aprovação da revisão

Você pode começar testando em **Sandbox** enquanto aguarda a aprovação!

---

## 🆘 **PRECISA DE AJUDA?**

Se tiver dúvidas sobre algum campo específico, me avise que eu ajudo! 🚀

