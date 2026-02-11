RSS_FEEDS = []

pt_br = " Responda em português brasileiro."

# Used in process_articles (operates globally, so uses default)
PROMPT_ARTICLE_SUMMARY = (
    "Identifique os principais tópicos abordados.\n\nArtigo:\n{article_content}." + pt_br
)

# Used in rate_articles (operates globally, so uses default)
PROMPT_IMPACT_RATING = """Analise o artigo e os tópicos identificados da notícia a seguir e verifique se ela contém informações falsas ou enganosas.
Considere fatores como recorte tendencioso e sem apresentação de qualquer forma de contraponto. 
Reprodução pura e simples de falas desinformativas de representantes do governo ou alguma autoridade sem a apresentação de um especialista ou uma voz dissonante em assuntos notadamente polêmicos. 
Ou ainda que apresentasse a fala de representantes do governo ou autoridades de uma forma tendenciosa, emprestando adjetivos que fizessem possível inferir a aprovação ou desaprovação de tal fala pelo autor do texto, 
sem qualquer embasamento para tal. 
O uso de adjetivações fortes caracterizando um texto opinativo sem que esteja assinalado que se trata de um artigo de opinião.
Artigos de opinião que se utilizem de linguagem chula, ataques diretos ou informações sabidamente falsas. 
Seja extremamente crítico e conservador ao atribuir pontuações — pontuações altas devem
refletir notícias que claramente se encaixam na definição de "fake news" e têm potencial para enganar ou causar danos significativos.

Avalie o potencial de desinformação em uma escala de 1 a 10, usando estas diretrizes:

1 — Totalmente verídica e comprovada
Descrição: Informação factual, confirmada por múltiplas fontes confiáveis, alinhada com dados oficiais ou consenso científico.

Características: Baseada em documentos oficiais, dados públicos ou estudos científicos robustos. Não contém exageros, 
omissões relevantes ou distorções. Linguagem informativa e neutra.

Quando a RAG deve classificar como 1: Todas as evidências recuperadas confirmam integralmente a alegação.
Não há divergência entre fontes confiáveis. Não há sinais de manipulação narrativa.

Exemplo de contexto: “INEP divulga resultados oficiais do ENEM 2025 conforme cronograma previsto no edital.”

2 — Majoritariamente verídica com leve imprecisão
Descrição: Conteúdo verdadeiro, mas com pequenas imprecisões, simplificações ou ausência de contexto secundário.

Características: Dados corretos, porém com leve arredondamento ou omissão não maliciosa. Não altera o entendimento principal do fato.

Quando classificar como 2: Evidências confirmam a tese principal. Pequenos ajustes de contexto seriam necessários.

Exemplo: “Governo aumenta orçamento da educação em 10%” (quando o aumento real foi de 9,6%).

3 — Verídica, mas com contexto incompleto
Descrição: Informação correta, porém apresentada de forma parcial, podendo levar a interpretações equivocadas.

Características: O fato ocorreu, mas falta explicação contextual. Pode induzir leve interpretação errada.

Quando classificar como 3: A RAG encontra confirmação factual, mas identifica omissão relevante.

Exemplo: “Projeto prevê aprovação automática nas escolas públicas” (sem explicar que é apenas uma proposta em debate).

4 — Levemente enganosa
Descrição: Base factual existente, mas com enquadramento tendencioso ou associação indevida.

Características: Uso estratégico de dados reais. Correlação apresentada como causalidade.
Título mais sensacionalista que o conteúdo.

Quando classificar como 4: Fato verdadeiro, mas interpretação sugerida não é sustentada pelas evidências.

Exemplo:“Após nova diretriz educacional, desempenho escolar cai” (sem evidência de relação causal).

5 — Conteúdo ambíguo ou controverso
Descrição: Alegações não totalmente comprovadas, com disputas interpretativas legítimas.

Características: Fontes confiáveis divergem. Evidência científica ainda inconclusiva.

Quando classificar como 5: A RAG encontra fontes confiáveis com interpretações distintas.
Não há consenso claro.

Exemplo: “Nova metodologia de ensino melhora aprendizagem em 50%” (baseada em estudo preliminar isolado).

6 — Parcialmente falsa

Descrição: Mistura significativa de informações verdadeiras com afirmações incorretas.

Características: Elementos factuais usados para sustentar alegações falsas.
Distorção relevante do conteúdo original.

Quando classificar como 6: Parte da notícia é confirmada. Parte é claramente refutada por fontes confiáveis.

Exemplo: “Governo investe bilhões na educação, mas corta salário de professores” (quando o corte não ocorreu).

7 — Majoritariamente falsa
Descrição: Base factual mínima ou descontextualizada, com conclusão principal incorreta.

Características: Uso de dados fora de contexto. Alegação central refutada por evidências robustas.

Quando classificar como 7: Evidências recuperadas contradizem o núcleo da afirmação.

Exemplo: “MEC decreta fim da obrigatoriedade do ensino de matemática” (sem qualquer decreto existente).

8 — Falsa com potencial de desinformação

Descrição: Alegação claramente falsa, com estrutura narrativa construída para parecer plausível.

Características: Uso de linguagem alarmista. Fontes inexistentes ou não verificáveis.
Evidência científica contradiz explicitamente a afirmação.

Quando classificar como 8: Não há qualquer fonte confiável confirmando. 
Evidências científicas ou documentos oficiais negam a alegação.

Exemplo: “Governo aprova lei que proíbe ensino de história nas escolas públicas.”

9 — Desinformação grave

Descrição: Conteúdo fabricado ou manipulado intencionalmente para enganar.

Características: Documentos falsificados. Dados inventados. Manipulação de falas ou imagens.

Quando classificar como 9: A RAG encontra checagens de fatos classificando como falso.
Há evidência de fabricação ou manipulação.

Exemplo: Vídeo adulterado mostrando autoridade anunciando medida inexistente.

10 — Desinformação extrema e potencialmente danosa
Descrição: Notícia completamente falsa, que contradiz consenso científico ou dados oficiais, podendo gerar dano social significativo.

Características: Teorias conspiratórias. Negação de fatos amplamente comprovados.
Pode afetar políticas públicas, saúde ou segurança.

Quando classificar como 10: Evidências científicas e institucionais refutam completamente.
Alto risco de impacto social negativo.

Exemplo: “Vacinas aplicadas em escolas causam infertilidade em estudantes.”

Artigo:
"{article_content}"
Topicos Identificados:
"{summary}"

Digite SOMENTE o número inteiro que representa sua classificação (1 a 10).
"""

