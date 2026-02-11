# meridiano/app_streamlit.py

import json
import math
from datetime import date, datetime, timedelta

import os
import markdown
import streamlit as st
from sqlmodel import select

from meridiano import config_base as config
from meridiano import database
from meridiano.utils import format_datetime, scrape_single_article_details


def init_session_state():
    """Initialize session state variables"""
    if "page" not in st.session_state:
        st.session_state.page = "briefings"
    if "selected_brief_id" not in st.session_state:
        st.session_state.selected_brief_id = None
    if "selected_article_id" not in st.session_state:
        st.session_state.selected_article_id = None


def show_briefings_page():
    """Displays a list of briefings, filterable by feed profile."""
    st.title("📋 Briefings")
    
    # Get available profiles
    available_profiles = database.get_distinct_feed_profiles(table="briefs")
    
    # Filter by feed profile
    col1, col2 = st.columns([3, 1])
    with col1:
        current_feed_profile = st.selectbox(
            "Feed Profile",
            ["All"] + available_profiles,
            key="briefings_feed_filter"
        )
    
    # Fetch briefings
    feed_filter = None if current_feed_profile == "All" else current_feed_profile
    briefs_metadata = database.get_all_briefs_metadata(feed_profile=feed_filter)
    
    if not briefs_metadata:
        st.info("Nenhum briefing encontrado.")
        return
    
    st.write(f"**{len(briefs_metadata)}** briefings encontrados")
    
    # Display briefings
    for brief in briefs_metadata:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(f"Briefing #{brief['id']}")
                st.write(f"**Feed Profile:** {brief['feed_profile']}")
                st.write(f"**Gerado em:** {format_datetime(brief['generated_at'], '%Y-%m-%d %H:%M:%S UTC')}")
            with col2:
                if st.button("Ver", key=f"brief_{brief['id']}"):
                    st.session_state.selected_brief_id = brief["id"]
                    st.session_state.page = "view_brief"
                    st.rerun()
            st.divider()


def show_brief_detail():
    """Displays a single specific briefing."""
    brief_id = st.session_state.selected_brief_id
    
    if st.button("← Voltar para Briefings"):
        st.session_state.page = "briefings"
        st.session_state.selected_brief_id = None
        st.rerun()
    
    brief_data = database.get_brief_by_id(brief_id)
    
    if brief_data is None:
        st.error(f"Briefing #{brief_id} não encontrado.")
        return
    
    st.title(f"📋 Briefing #{brief_data['id']}")
    st.write(f"**Feed Profile:** {brief_data['feed_profile']}")
    st.write(f"**Gerado em:** {format_datetime(brief_data['generated_at'], '%Y-%m-%d %H:%M:%S UTC')}")
    
    st.divider()
    
    # Render markdown content
    st.markdown(brief_data["brief_markdown"], unsafe_allow_html=True)


def show_articles_page():
    """Displays a paginated list of stored articles with search, sorting and date filtering."""
    st.title("📰 Artigos")
    
    # Initialize session state for pagination
    if "articles_page" not in st.session_state:
        st.session_state.articles_page = 1
    
    # Filters in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Search
        search_term = st.text_input("🔍 Buscar", key="search_articles")
    
    with col2:
        # Feed Profile Filter
        available_profiles = database.get_distinct_feed_profiles(table="articles")
        feed_profile = st.selectbox(
            "Feed Profile",
            ["All"] + available_profiles,
            key="articles_feed_filter"
        )
    
    with col3:
        # Date preset
        preset = st.selectbox(
            "Período",
            ["", "yesterday", "last_week", "last_30d", "last_3m", "last_12m"],
            format_func=lambda x: {
                "": "Custom",
                "yesterday": "Ontem",
                "last_week": "Última Semana",
                "last_30d": "Últimos 30 dias",
                "last_3m": "Últimos 3 meses",
                "last_12m": "Últimos 12 meses"
            }.get(x, x),
            key="date_preset"
        )
    
    # Date range filters
    col1, col2 = st.columns(2)
    with col1:
        start_date_input = st.date_input("Data Início", value=None, key="start_date")
    with col2:
        end_date_input = st.date_input("Data Fim", value=None, key="end_date")
    
    # Calculate dates based on preset
    start_date, end_date = None, None
    if preset:
        today = date.today()
        if preset == "yesterday":
            start_date = today - timedelta(days=1)
            end_date = start_date
        elif preset == "last_week":
            start_date = today - timedelta(days=6)
            end_date = today
        elif preset == "last_30d":
            start_date = today - timedelta(days=29)
            end_date = today
        elif preset == "last_3m":
            start_date = today - timedelta(days=89)
            end_date = today
        elif preset == "last_12m":
            start_date = today - timedelta(days=364)
            end_date = today
    else:
        start_date = start_date_input
        end_date = end_date_input
    
    # Sorting
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox(
            "Ordenar por",
            ["published_date", "title", "feed_source"],
            key="sort_by"
        )
    with col2:
        direction = st.selectbox(
            "Direção",
            ["desc", "asc"],
            format_func=lambda x: "Decrescente" if x == "desc" else "Crescente",
            key="sort_direction"
        )
    
    # Pagination settings
    per_page = getattr(config, "ARTICLES_PER_PAGE", 25)
    
    # Prepare filters
    feed_filter = None if feed_profile == "All" else feed_profile
    search_filter = search_term.strip() if search_term else None
    
    # Fetch total count
    total_articles = database.get_total_article_count(
        start_date=start_date,
        end_date=end_date,
        feed_profile=feed_filter,
        search_term=search_filter,
    )
    
    if total_articles == 0:
        st.info("Nenhum artigo encontrado com os filtros aplicados.")
        return
    
    # Calculate total pages
    total_pages = math.ceil(total_articles / per_page)
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Anterior", disabled=st.session_state.articles_page <= 1):
            st.session_state.articles_page -= 1
            st.rerun()
    with col2:
        st.write(f"Página {st.session_state.articles_page} de {total_pages} ({total_articles} artigos)")
    with col3:
        if st.button("Próxima ➡️", disabled=st.session_state.articles_page >= total_pages):
            st.session_state.articles_page += 1
            st.rerun()
    
    st.divider()
    
    # Fetch articles
    articles_data = database.get_all_articles(
        page=st.session_state.articles_page,
        per_page=per_page,
        sort_by=sort_by,
        direction=direction,
        start_date=start_date,
        end_date=end_date,
        feed_profile=feed_filter,
        search_term=search_filter,
    )
    
    # Display articles
    for article in articles_data:
        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.subheader(article["title"])
                st.write(f"**Fonte:** {article['feed_source']} | **Profile:** {article['feed_profile']}")
                st.write(f"**Publicado em:** {format_datetime(article['published_date'], '%Y-%m-%d %H:%M')}")
                
                if article.get("processed_content"):
                    # Show preview of processed content
                    preview = article["processed_content"][:200] + "..." if len(article["processed_content"]) > 200 else article["processed_content"]
                    st.write(preview)
            
            with col2:
                if st.button("Ver detalhes", key=f"article_{article['id']}"):
                    st.session_state.selected_article_id = article["id"]
                    st.session_state.page = "view_article"
                    st.rerun()
            
            st.divider()


def show_article_detail():
    """Displays details for a single specific article."""
    article_id = st.session_state.selected_article_id
    
    if st.button("← Voltar para Artigos"):
        st.session_state.page = "articles"
        st.session_state.selected_article_id = None
        st.rerun()
    
    article_data_immutable = database.get_article_by_id(article_id)
    
    if article_data_immutable is None:
        st.error(f"Artigo #{article_id} não encontrado.")
        return
    
    article_data = dict(article_data_immutable)
    
    st.title(article_data["title"])
    
    # Article metadata
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Feed Source:** {article_data['feed_source']}")
        st.write(f"**Feed Profile:** {article_data['feed_profile']}")
    with col2:
        st.write(f"**Publicado em:** {format_datetime(article_data['published_date'], '%Y-%m-%d %H:%M:%S')}")
        st.write(f"**ID:** {article_data['id']}")
    
    # URL
    if article_data.get("url"):
        st.write(f"**URL:** [{article_data['url']}]({article_data['url']})")
    
    # Image
    if article_data.get("image_url"):
        st.image(article_data["image_url"], use_container_width=True)
    
    st.divider()
    
    # Processed content
    if article_data.get("processed_content"):
        st.subheader("📝 Conteúdo Processado")
        st.markdown(article_data["processed_content"], unsafe_allow_html=True)
    
    # Raw content (expandable)
    if article_data.get("raw_content"):
        with st.expander("Ver conteúdo bruto"):
            st.text(article_data["raw_content"][:1000] + "..." if len(article_data["raw_content"]) > 1000 else article_data["raw_content"])
    
    # Embedding status
    embedding_status = "Not Generated"
    if article_data.get("embedding"):
        try:
            embed_data = json.loads(article_data["embedding"])
            if embed_data:
                embedding_status = f"Present ({len(embed_data)} dimensions)"
            else:
                embedding_status = "Present (Empty)"
        except (json.JSONDecodeError, TypeError):
            embedding_status = "Present (Invalid Format)"
    
    st.info(f"**Embedding Status:** {embedding_status}")


def show_add_article_page():
    """Form to manually add an article."""
    st.title("➕ Adicionar Artigo Manualmente")
    
    # Get available profiles
    available_profiles = database.get_distinct_feed_profiles(table="articles")
    manual_profile_name = getattr(config, "MANUALLY_ADDED_PROFILE_NAME", "manual")
    
    with st.form("add_article_form"):
        article_url = st.text_input("URL do Artigo", placeholder="https://exemplo.com/article")
        
        feed_profile_to_assign = st.selectbox(
            "Feed Profile",
            [manual_profile_name] + available_profiles
        )
        
        submit_button = st.form_submit_button("Adicionar Artigo")
        
        if submit_button:
            if not article_url:
                st.error("URL do artigo é obrigatória.")
                return
            
            if not (article_url.startswith("http://") or article_url.startswith("https://")):
                st.error("URL inválida. Por favor, inclua http:// ou https://.")
                return
            
            # Check if article already exists
            with database.get_db_connection() as session:
                stmt = select(database.Article).where(database.Article.url == article_url)
                existing_article = session.exec(stmt).first()
            
            if existing_article:
                st.warning(f'Artigo da URL "{article_url}" já existe (ID: {existing_article.id}).')
                return
            
            # Scrape article details
            with st.spinner("Extraindo detalhes do artigo..."):
                scraped_details = scrape_single_article_details(article_url)
            
            if scraped_details["error"] and not (scraped_details["title"] or scraped_details["raw_content"]):
                st.error(f"Erro ao extrair artigo: {scraped_details['error']}")
                return
            elif scraped_details["error"]:
                st.warning(f"Aviso durante extração: {scraped_details['error']}")
            
            try:
                final_title = scraped_details["title"] if scraped_details["title"] else "Manually Added - Pending Title"
                final_raw_content = scraped_details["raw_content"]
                final_image_url = scraped_details["image_url"]
                
                article_id = database.add_article(
                    url=article_url,
                    title=final_title,
                    published_date=datetime.now(),
                    feed_source="Manual Addition",
                    raw_content=final_raw_content,
                    feed_profile=feed_profile_to_assign,
                    image_url=final_image_url,
                )
                
                if article_id:
                    if final_raw_content:
                        st.success(
                            f'Artigo "{final_title}" adicionado e extraído com sucesso para o profile '
                            f'"{feed_profile_to_assign}" (ID: {article_id}). '
                            "Será processado para resumo/impacto em breve."
                        )
                    else:
                        st.warning(
                            f'URL do artigo "{article_url}" adicionada ao profile "{feed_profile_to_assign}" '
                            f"(ID: {article_id}). Extração de conteúdo falhou, será tentada novamente pelo processo em lote."
                        )
                    
                    # Navigate to the article
                    if st.button("Ver artigo adicionado"):
                        st.session_state.selected_article_id = article_id
                        st.session_state.page = "view_article"
                        st.rerun()
                else:
                    st.error(
                        "Falha ao adicionar artigo ao banco de dados. Pode já existir com um erro diferente "
                        "ou houve um problema desconhecido."
                    )
            except Exception as e:
                print(f"ERROR adding manual article {article_url} to DB: {e}")
                st.error(f"Ocorreu um erro ao adicionar o artigo ao banco de dados: {e}")

def show_chatbot_page():
    """Displays the chatbot interface."""
    st.title("✍️ Verificador de Fake News")
    

    st.divider()
    
    

    

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Meridiano",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    database.init_db()
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📰 Meridiano")
        st.divider()
        
        if st.button("📋 Briefings", use_container_width=True):
            st.session_state.page = "briefings"
            st.session_state.articles_page = 1
            st.rerun()
        
        if st.button("📰 Artigos", use_container_width=True):
            st.session_state.page = "articles"
            st.session_state.articles_page = 1
            st.rerun()
        
        if st.button("➕ Adicionar Artigo", use_container_width=True):
            st.session_state.page = "add_article"
            st.rerun()

        if st.button("✍️ Chatbot", use_container_width=True):
            st.session_state.page = "chatbot"
            st.rerun()
        
        st.divider()
        st.caption("Sistema de agregação e análise de notícias")
    
    # Page routing
    if st.session_state.page == "briefings":
        show_briefings_page()
    elif st.session_state.page == "view_brief":
        show_brief_detail()
    elif st.session_state.page == "articles":
        show_articles_page()
    elif st.session_state.page == "view_article":
        show_article_detail()
    elif st.session_state.page == "add_article":
        show_add_article_page()
    elif st.session_state.page == "chatbot":
        show_chatbot_page()
    
    # Initialize chatbot session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "collection" not in st.session_state:
        st.session_state.collection = None


if __name__ == "__main__":
    main()
