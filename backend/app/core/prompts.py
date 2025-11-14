from __future__ import annotations

import json
from textwrap import dedent
from typing import Iterable, Mapping


QaPair = Mapping[str, str]


def _qa_pairs_to_json(qa_pairs: Iterable[QaPair]) -> str:
    """
    Converte uma lista de pares {"pergunta": "...", "resposta": "..."}
    em JSON bonitinho com indentação (apenas para exibir no prompt).
    """
    return json.dumps(list(qa_pairs), ensure_ascii=False, indent=2)


# =====================================================================
# 1) PROMPT: GERAR PERFIL COMPLETO DA EMPRESA
# =====================================================================


def build_company_profile_prompt(qa_pairs: Iterable[QaPair]) -> str:
    """
    Gera o prompt para o modelo montar o perfil estruturado da empresa
    a partir de perguntas e respostas já coletadas no onboarding.
    """
    qa_json = _qa_pairs_to_json(qa_pairs)

    prompt = f"""
    Você receberá perguntas e respostas fornecidas por uma empresa
    sobre seu posicionamento, público e comunicação.

    Use essas informações para montar um PERFIL ESTRUTURADO da empresa,
    voltado para curadoria de notícias e produção de conteúdo.

    As respostas serão usadas para:
    - decidir se uma notícia é relevante ou não
    - definir tom de voz da comunicação
    - escolher temas prioritários e temas proibidos
    - guiar a geração de roteiros e conteúdos

    Perguntas e respostas (JSON):

    {qa_json}

    Responda APENAS em JSON válido, SEM texto fora do JSON,
    seguindo EXATAMENTE este formato:

    {{
      "segmento": "descrição curta do segmento/mercado da empresa",
      "publico_alvo": "descrição do público-alvo principal",
      "tom_comunicacao": "descrição do tom de voz da marca (formalidade, vocabulário, emoções etc.)",
      "canais": ["lista", "de", "canais", "de comunicação"],
      "temas_prioritarios": ["lista", "de", "temas", "importantes", "com base nas respostas"],
      "temas_evitar": ["lista", "de", "assuntos", "a evitar", "com base nas respostas"],
      "objetivo_conteudo": "qual é o objetivo principal da presença de conteúdo da empresa",
      "resumo": "um parágrafo resumindo o perfil geral da empresa e seu posicionamento"
    }}

    Não inclua comentários, explicações nem texto fora do JSON.
    """
    return dedent(prompt).strip()


# =====================================================================
# 2) PROMPT: AVALIAR SE PRECISA DE MAIS PERGUNTAS (OPÇÃO A)
# =====================================================================

MAX_QUESTIONS = 12

def build_onboarding_evaluator_prompt(qa_pairs: Iterable[QaPair]) -> str:
    qa_list = list(qa_pairs)
    qa_json = _qa_pairs_to_json(qa_list)
    qtd_perguntas = len(qa_list)

    prompt = f"""
    Você é um avaliador de ONBOARDING de marca focado em comunicação
    e curadoria de conteúdo (decidir o que postar, monitorar ou descartar).

    Já existem {qtd_perguntas} perguntas respondidas.
    Existe um limite recomendado de aproximadamente {MAX_QUESTIONS} perguntas no total.
    O objetivo NÃO é ter um dossiê perfeito, e sim um perfil prático,
    suficientemente bom para orientar decisões de conteúdo.

    =========================
    FASE 1 – PERGUNTAS BÁSICAS
    =========================

    Existem 6 perguntas BÁSICAS OBRIGATÓRIAS. Elas são:

    1) "Qual é o setor/mercado da empresa?"
    2) "Quem é o público-alvo principal?"
    3) "Qual é o tom da comunicação desejado?"
    4) "Em quais canais a empresa costuma postar conteúdo?"
    5) "Quais temas principais são relevantes para a empresa?"
    6) "Quais temas devem ser evitados pela empresa?"

    REGRAS IMPORTANTES SOBRE ESSAS 6:

    - Você NUNCA deve refazer essas perguntas do zero.
    - Você NUNCA deve gerar versões genéricas delas de novo.
    - Você DEVE verificar, olhando o JSON de perguntas e respostas,
      se cada uma das 6 perguntas acima já aparece como pergunta feita
      (mesmo que com pequenas variações de texto).

    SE ALGUMA DAS 6 AINDA NÃO APARECER CLARAMENTE NAS PERGUNTAS JÁ FEITAS:

      - Você DEVE responder obrigatoriamente:
        {{
          "precisa_mais": true,
          "novas_perguntas": [
            "lista das perguntas BÁSICAS que ainda não foram feitas, usando exatamente o texto original ou uma variação mínima"
          ]
        }}

      - Nessa situação, você NÃO deve tentar aprofundar nem sofisticar.
      - Foque APENAS em completar as 6 perguntas obrigatórias.
      - Gere no máximo 2 perguntas por vez (se faltam várias, envie as próximas 1 ou 2).

    Você NUNCA deve responder "precisa_mais": false enquanto alguma das 6 perguntas
    básicas ainda não tiver sido feita.

    =========================
    FASE 2 – APROFUNDAMENTO
    =========================

    Essa fase só acontece SE as 6 perguntas básicas já tiverem sido feitas.

    Agora você deve avaliar se as informações já são suficientes nas áreas:

    1. Posicionamento da marca
       - Nicho específico
       - Diferenciais
       - Proposta de valor

    2. Público-alvo
       - Perfil geral (faixa etária aproximada, classe social, cargos mais comuns)
       - Principais dores e necessidades
       - Objetivos desse público

    3. Tom de comunicação
       - Nível de formalidade
       - Estilo desejado (técnico, acessível, didático etc.)
       - Sensação que a marca quer transmitir (segurança, proximidade, autoridade etc.)

    4. Canais principais
       - Onde a empresa publica
       - Formatos principais (texto, vídeo, carrossel, newsletter etc.)

    5. Temas prioritários
       - Listados com clareza
       - Ligados às dores e interesses do público

    6. Temas proibidos / sensíveis
       - Assuntos delicados a evitar (política, polêmicas etc.)
       - Questões de risco, compliance ou reputação

    7. Objetivos do conteúdo
       - Educação, autoridade, geração de demanda, relacionamento etc.

    REGRAS PARA EVITAR REDUNDÂNCIA:

    - NÃO faça perguntas que sejam apenas reformulações de perguntas anteriores.
    - NÃO volte a perguntar algo que já tenha uma resposta clara e útil.
    - NÃO aprofunde infinitamente o mesmo tema.
    - Se já há informação suficiente para decidir se uma notícia deve ser
      postada / monitorada / descartada, considere o tema FECHADO.

    REGRAS DE QUANTIDADE:

    - O número ideal de perguntas totais fica entre 6 e 10.
    - O limite absoluto é de {MAX_QUESTIONS} perguntas.
    - Quanto maior o número atual de perguntas ({qtd_perguntas}),
      mais rigoroso você deve ser antes de pedir novas.
    - Se já estiver próximo de {MAX_QUESTIONS}, só peça novas perguntas
      se houver uma lacuna REALMENTE crítica.

    FORMATO DA RESPOSTA (SEM TEXTO EXTRA):

    Sua resposta DEVE ser SEMPRE um JSON válido, seguindo exatamente:

    {{
      "precisa_mais": true ou false,
      "novas_perguntas": ["pergunta 1", "pergunta 2"]
    }}

    - Se "precisa_mais" for true:
        - Gere NO MÁXIMO 2 novas perguntas.
        - As perguntas devem ser:
          - específicas,
          - complementares,
          - focadas em lacunas REAIS que atrapalham a curadoria.
        - NÃO repita as 6 perguntas básicas.
        - NÃO repita perguntas que já foram feitas.

    - Se as informações já forem suficientes para um perfil FUNCIONAL,
      responda exatamente:

      {{
        "precisa_mais": false,
        "novas_perguntas": []
      }}

    Não inclua comentários, explicações nem texto fora do JSON.

    Perguntas e respostas já fornecidas (JSON):

    {qa_json}
    """
    return dedent(prompt).strip()


