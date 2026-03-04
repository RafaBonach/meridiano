RSS_FEEDS = [
    "https://feeds.folha.uol.com.br/poder/rss091.xml",  # Folha de S.Paulo - Poder
    "https://rss.app/feeds/LeBls41h3T952Ds5.xml" # Gazeta do Povo - Política
]
"""
RSS_FEEDS = [
    "https://feeds.folha.uol.com.br/poder/rss091.xml",  # Folha de S.Paulo - Poder
    "https://feeds.folha.uol.com.br/ciencia/rss091.xml",  # Folha de S.Paulo - Ciência
    "https://feeds.folha.uol.com.br/opiniao/rss091.xml",  # Folha de S.Paulo - Opinião
    "https://feeds.folha.uol.com.br/educacao/rss091.xml",  # Folha de S.Paulo - Educação
    "https://feeds.folha.uol.com.br/equilibrioesaude/rss091.xml",  # Folha de S.Paulo - Equilíbrio e Saúde
    "https://www.tribunapr.com.br/feed/",  # Tribuna PR
    "https://www.bahianoticias.com.br/principal/rss.xml",  # Bahia Notícias
    "https://www.bahianoticias.com.br/justica/rss.xml",  # Bahia Notícias - Justiça
    "https://jornaldaparaiba.com.br/feed/",  # Jornal da Paraíba
    "https://rss.uol.com.br/feed/noticias.xml",  # UOL Notícias
    "https://pox.globo.com/rss/oglobo", # O Globo
    "https://pox.globo.com/rss/extra/", # Extra
    "https://ndmais.com.br/feed/", # ND Mais
    "https://www.folhavitoria.com.br/feed/", # Folha Vitória
    "https://diariodorio.com/feed/", # Diário do Rio
    "https://www.brasildefato.com.br/feed/", # Brasil de Fato
    "https://www.aliadosbrasiloficial.com.br/rss.xml", # Aliados Brasil
    "https://www.metropoles.com/feed", # Metrópoles
    "https://tribunadonorte.com.br/feed/", # Tribuna do Norte
    "https://jovempan.com.br/jpnews/feed", # Jovem Pan - JPNews
    "https://www.aosfatos.org/noticias/feed/", # Aos Fatos
    "https://www.agencialupa.org/feed/", # Agência Lupa
    "https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/geral/?body=%7B%22layout%22:%22google-news%22%7D", # Estadão - Geral
    "https://apublica.org/feed/", # Agência Pública
    "https://www.nexojornal.com.br/rss.xml",  # Nexo Jornal
    "http://agenciabrasil.ebc.com.br/rss/geral/feed.xml", # Agência Brasil - Geral
    "http://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml", # Agência Brasil - Últimas Notícias
    "http://agenciabrasil.ebc.com.br/rss/politica/feed.xml", # Agência Brasil - Política
    "http://agenciabrasil.ebc.com.br/rss/educacao/feed.xml", # Agência Brasil - Educação
    "http://agenciabrasil.ebc.com.br/rss/saude/feed.xml", # Agência Brasil - Saúde
]
"""
data_context = "Responda baseado neste contexto:\n {database_context}.\n\n"

pt_br = " Responda em português brasileiro."

# Used in process_articles (operates globally, so uses default)
""" A ideia aqui é pegar uma notícia e transformá-la em uma manchete.
    Essa manchete deve apresentar todos os pontos principais da notícia."""
PROMPT_ARTICLE_SUMMARY = (
    "Analise o artigo a seguir e resuma o conteúdo em uma manchete clara e concisa, que capture os pontos principais e o tom do artigo. "
    "A manchete deve ser neutra, apresentando exclusivamente o que é aprentado no artigo, sem fazer juizo de valores ou adicionar informações externas."
    "\n\nArtigo:\n{article_content}." + pt_br
)


# Used in rate_articles (operates globally, so uses default)
PROMPT_IMPACT_RATING = """Analise a manchete a seguir e avalie o grau de veracidade da notícia.

Considere aspectos importantes como presença de palavras de alto impacto que visem chamar a atenção de um publico específico, 
uso de adjetivações fortes, linguagem sensacionalista, ou elementos que visam gerar indignação ou medo, sem apresentar evidências claras ou contrapontos.

Avalie o grau de veracidade em uma escala de 0 a 2, usando estas diretrizes:

0: Verdadeira - A manchete é precisa, confiável e baseada em fatos verificáveis. Não apresenta carater sensacionalista, adjetivações fortes ou elementos que visam engajar o leitor de forma tendenciosa. Tem baixo potencial de desinformação. 
Exemplo: "O Brasil tem mais de 16 mil sindicatos. E, aliás, uma outra coisa estranha. Dos 16 mil, 11,5 mil mais ou menos são sindicatos de trabalhadores. E mais de 5.000 patronais".

1: Falsa - A manchete adota de palavras de alto impacto, adjetivações fortes, ou linguagem sensacionalista que visa gerar engajamento, indignação ou medo, mas carece de evidências claras ou contrapontos. Tem potencial moderado a alto de desinformação. 
Exemplo: "Não existe nenhum lugar do mundo que tenha aplicado essa medida teto de gastos"

2: Indeterminada - Não se trata de uma manchete que deve ser verificada a veracidade, é o caso de receita de bolo, instrução, ou outro tipo de artigo que não tem a função de informar sobre um evento ou fato específico. 
Exemplo: "6 maneiras de reinventar a ida ao cinema em São Paulo" ou "Como escolher a impressora ideal gastando pouco? Confira dicas e modelos"

Manchete:
"{summary}"

Digite SOMENTE o número inteiro que representa sua classificação (0 a 2).
"""

PROMPT_CLUSTER_ANALYSIS = (
    """
Estes são artigos de notícia potencialmente relacionados de um contexto '{feed_profile}':

{cluster_summaries_text}

QUal é o evento ou tópico principal discutido? Esse artigo contém informações falsas ou enganosas?
Resuma os principais desenvolvimentos e indique se há desinformação expliando em 3 a 5 frases, com base *apenas* no texto fornecido. 
Se os artigos parecerem não relacionados, informe isso claramente."""
+ pt_br
)

PROMPT_BRIEF_SYNTHESIS = """
Você é um assistente de IA identificando notícias falsas e e descrevendo em markdown o motivo dessas notícias serem falsas e qual seria a verdade por trás do assunto tratado, 
caso haja, especificamente para a categoria '{feed_profile}. 
Elabora essas analises utilizando uma linguagem clara e acessível, evitando jargões técnicos, para que o público geral possa entender facilmente.

EM seguida, aprese  nte fontes confiáveis que desmentem as notícias falsas, incluindo links para artigos de checagem de fatos, estudos científicos ou declarações oficiais que refutem as alegações enganosas.
Se não houver evidências suficientes para classificar a notícia como falsa, explique por que ela é considerada verdadeira ou precisa, destacando as evidências que sustentam sua veracidade.

Grupo de notícias analisadas:
{cluster_analyses_text}
"""

# Used in chatbot (can be overridden per profile)
PROMPT_CHATBOT_RESPONSE = ("""
Você é um assistente de IA especializado em identificar e explicar notícias falsas, 
comparando as informações fornecidas nas fontes a seguir com evidências confiáveis para determinar a veracidade das alegações.

Responda se a pergunta do usuário é verdadeira ou falsa baseada no contexto fornecido, 
e explique o motivo da classificação, indicando a fonte ao qual você se baseou e o método que adotou
para chegar a conclusão. 
Se a pergunta não puder ser respondida com base nas informações fornecidas, explique por que e indique quais informações adicionais seriam necessárias para uma avaliação mais precisa.

<context>
{context}
</context>

Pergunta: {user_question}
                           
""" + pt_br)