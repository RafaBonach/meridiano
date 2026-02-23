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
PROMPT_ARTICLE_SUMMARY = (
    data_context +
    "Analise o conteúdo desta notícia e verifique se ela se categoriza em uma notícia Verdadeira, Parcialmente verdadeira, Falsa ou Indeterminado (receita de bolo, instrução, entre outros artigos que não são notícias)."
    "Durante essa analise, deve ser identificada as principais caracteristicas que enquandrem-as nos tópicos anteriores."
    "Apresente claramente se a notícia é Verdadeira, Parcialmente verdadeira, Falsa ou Indeterminado e"
    "elabre uma descrião de 2 a 6 frases explicando o motivo da classificação, destacando os aspectos que podem indicar a presença de informação falsa ou enganosa, como recorte tendencioso, ausência de contraponto, reprodução de falas desinformativas sem apresentação de especialistas ou vozes dissonantes, uso de adjetivações fortes sem indicação de que se trata de opinião, ou linguagem chula e ataques diretos em artigos de opinião."
    "Caso seja necessário, utilize trechos da notícia para exemplificar os pontos destacados na descrição. Seja claro e objetivo em sua análise, fornecendo uma avaliação crítica e fundamentada do conteúdo da notícia."
    "Finalmente, identifique e indique os principais tópicos abordados.\n\nArtigo:\n{article_content}." + pt_br
)


# Used in rate_articles (operates globally, so uses default)
PROMPT_IMPACT_RATING = """Analise o descrição da notícia a seguir e estime o quão enganosa ela é.
Verifique fatores como a presença de informações falsas ou enganosas, recorte tendencioso, ausência de contraponto, reprodução de falas desinformativas sem apresentação de especialistas ou vozes dissonantes, uso de adjetivações fortes sem indicação de que se trata de opinião, 
ou linguagem chula e ataques diretos em artigos de opinião. Seja extremamente crítico e conservador ao atribuir pontuações — pontuações mais altas devem refletir notícias verdadeiramente enganosas ou com forte potencial de desinformação.

Avalie o grau de veracidade em uma escala de 1 a 4, usando estas diretrizes:

1: Verdadeira. A descrição da notícia indica que a notícia é verdadeira, baseada em evidências claras e verificáveis, sem sinais de desinformação ou engano.
2: Parcialmente verdadeira. A descrição da notícia sugere que a notícia contém elementos de verdade, mas também apresenta informações enganosas ou imprecisas. Pode haver uma mistura de fatos e desinformação, ou a notícia pode ser tendenciosa, mas não completamente falsa.
3: Falsa. A descrição da notícia indica que a notícia é notadamente falsa, com evidências claras de desinformação, engano ou falta de veracidade. A notícia pode conter informações fabricadas, distorcidas ou completamente infundadas com intuito de desinformar o leitor.
4: Indeterminado. Não se trata de uma notícia, mas sim de um conteúdo que não pode ser classificado como verdadeiro ou falso, como uma receita de bolo, instrução ou outro tipo de artigo que não tem a intenção de informar sobre um evento ou fato específico. 

Resumo:
"{summary}"

Digite SOMENTE o número inteiro que representa sua classificação (1 a 4).
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
