import math
from datetime import date, timedelta

import streamlit as st

from meridiano import config_base as config
from meridiano import database
from meridiano.utils import format_datetime


PRESET_OPTIONS = {
    "": "Nenhum",
    "yesterday": "Ontem",
    "last_week": "Última semana",
    "last_30d": "Últimos 30 dias",
    "last_3m": "Últimos 3 meses",
    "last_12m": "Últimos 12 meses",
}


def _apply_preset_dates(preset_key: str) -> tuple[date | None, date | None]:
    today = date.today()

    if preset_key == "yesterday":
        start_date = today - timedelta(days=1)
        return start_date, start_date
    if preset_key == "last_week":
        return today - timedelta(days=6), today
    if preset_key == "last_30d":
        return today - timedelta(days=29), today
    if preset_key == "last_3m":
        return today - timedelta(days=89), today
    if preset_key == "last_12m":
        return today - timedelta(days=364), today

    return None, None


def _sync_dates_from_preset() -> None:
    selected_preset = st.session_state.get("articles_preset", "")
    start_date, end_date = _apply_preset_dates(selected_preset)
    st.session_state["articles_start_date"] = start_date
    st.session_state["articles_end_date"] = end_date
    st.session_state["articles_page"] = 1


def _reset_date_filters() -> None:
    st.session_state["articles_preset"] = ""
    st.session_state["articles_start_date"] = None
    st.session_state["articles_end_date"] = None
    st.session_state["articles_page"] = 1


def _initialize_state() -> None:
    st.session_state.setdefault("articles_page", 1)
    st.session_state.setdefault("articles_sort_by", "published_date")
    st.session_state.setdefault("articles_direction", "desc")
    st.session_state.setdefault("articles_feed_profile", "")
    st.session_state.setdefault("articles_search", "")
    st.session_state.setdefault("articles_preset", "")
    st.session_state.setdefault("articles_start_date", None)
    st.session_state.setdefault("articles_end_date", None)

def _change_page(total_pages: int, current_page: int, key_prefix: str) -> None:
    if total_pages > 1:
        nav_col_1, nav_col_2, nav_col_3 = st.columns([1, 2, 1])

        with nav_col_1:
            if st.button("◀ Anterior", key=f"{key_prefix}_prev", disabled=current_page <= 1):
                st.session_state["articles_page"] = current_page - 1
                st.rerun()

        with nav_col_2:
            st.write(f"Página {current_page} de {total_pages}")

        with nav_col_3:
            if st.button("Próxima ▶", key=f"{key_prefix}_next", disabled=current_page >= total_pages):
                st.session_state["articles_page"] = current_page + 1
                st.rerun()


def show() -> None:
    _initialize_state()
    per_page = getattr(config, "ARTICLES_PER_PAGE", 25)

    st.header("📰 Notícias")

    available_profiles = database.get_distinct_feed_profiles(table="articles")
    profile_options = [""] + available_profiles
    profile_labels = {"": "Todos os perfis", **{profile: profile for profile in available_profiles}}

    filter_col_1, filter_col_2, filter_col_3 = st.columns([2, 3, 2])

    with filter_col_1:
        selected_profile = st.selectbox(
            "Perfil",
            options=profile_options,
            format_func=lambda option: profile_labels.get(option, option),
            index=profile_options.index(st.session_state["articles_feed_profile"])
            if st.session_state["articles_feed_profile"] in profile_options
            else 0,
        )

    with filter_col_2:
        search_term = st.text_input(
            "Buscar no título e conteúdo",
            value=st.session_state["articles_search"],
            placeholder="Digite para filtrar...",
        ).strip()

    with filter_col_3:
        sort_by = st.selectbox(
            "Ordenar por",
            options=["published_date", "impact_score"],
            format_func=lambda option: "Data de publicação" if option == "published_date" else "Impacto",
            index=0 if st.session_state["articles_sort_by"] == "published_date" else 1,
        )

    date_expanded = bool(st.session_state["articles_start_date"] or st.session_state["articles_end_date"])
    with st.expander("Filtros de data", expanded=date_expanded):
        date_col_1, date_col_2, date_col_3 = st.columns([2, 2, 1])

        with date_col_1:
            start_date = st.date_input("De", value=st.session_state["articles_start_date"])

        with date_col_2:
            end_date = st.date_input("Até", value=st.session_state["articles_end_date"])

        with date_col_3:
            direction = st.selectbox(
                "Direção",
                options=["desc", "asc"],
                format_func=lambda option: "Mais recentes" if option == "desc" else "Mais antigas",
                index=0 if st.session_state["articles_direction"] == "desc" else 1,
            )

        preset = st.selectbox(
            "Período rápido",
            options=list(PRESET_OPTIONS.keys()),
            format_func=lambda option: PRESET_OPTIONS[option],
            index=list(PRESET_OPTIONS.keys()).index(st.session_state["articles_preset"])
            if st.session_state["articles_preset"] in PRESET_OPTIONS
            else 0,
        )

        action_col_1, action_col_2 = st.columns([1, 1])
        with action_col_1:
            apply_dates = st.button("Aplicar filtros")
        with action_col_2:
            clear_dates = st.button("Limpar datas")

    if clear_dates:
        _reset_date_filters()
        st.rerun()

    if preset != st.session_state["articles_preset"]:
        st.session_state["articles_preset"] = preset
        _sync_dates_from_preset()
        st.rerun()

    if apply_dates:
        st.session_state["articles_start_date"] = start_date
        st.session_state["articles_end_date"] = end_date
        st.session_state["articles_page"] = 1

    filters_changed = any(
        [
            selected_profile != st.session_state["articles_feed_profile"],
            search_term != st.session_state["articles_search"],
            sort_by != st.session_state["articles_sort_by"],
            direction != st.session_state["articles_direction"],
        ]
    )

    st.session_state["articles_feed_profile"] = selected_profile
    st.session_state["articles_search"] = search_term
    st.session_state["articles_sort_by"] = sort_by
    st.session_state["articles_direction"] = direction

    if filters_changed:
        st.session_state["articles_page"] = 1

    start_date = st.session_state.get("articles_start_date")
    end_date = st.session_state.get("articles_end_date")
    current_feed_profile = st.session_state.get("articles_feed_profile")
    current_search_term = st.session_state.get("articles_search", "").strip()
    current_page = max(st.session_state.get("articles_page", 1), 1)

    total_articles = database.get_total_article_count(
        start_date=start_date,
        end_date=end_date,
        feed_profile=current_feed_profile or None,
        search_term=current_search_term or None,
    )

    total_pages = math.ceil(total_articles / per_page) if total_articles > 0 else 0
    if total_pages > 0 and current_page > total_pages:
        current_page = total_pages
        st.session_state["articles_page"] = total_pages

    articles_data = database.get_all_articles(
        page=current_page,
        per_page=per_page,
        sort_by=st.session_state["articles_sort_by"],
        direction=st.session_state["articles_direction"],
        start_date=start_date,
        end_date=end_date,
        feed_profile=current_feed_profile or None,
        search_term=current_search_term or None,
    )

    _change_page(total_pages=total_pages, current_page=current_page, key_prefix="top")
    st.divider()

    if total_articles > 0:
        start_item = (current_page - 1) * per_page + 1
        end_item = min(current_page * per_page, total_articles)
        st.caption(f"Mostrando artigos {start_item} - {end_item} de {total_articles} (com filtros ativos)")
    else:
        st.info("Nenhum artigo encontrado com os filtros atuais.")

    for article in articles_data:
        with st.container(border=True):
            content_col_1, content_col_2 = st.columns([1, 4])

            with content_col_1:
                image_url = article.get("image_url")
                if image_url:
                    st.image(image_url, use_container_width=True)
                else:
                    st.caption("Sem imagem")

            with content_col_2:
                feed_profile = article.get("feed_profile") or "N/A"
                impact_score = article.get("impact_score")
                impact_text = str(impact_score) if impact_score is not None else "-"

                st.markdown(f"**[{article.get('title') or 'Untitled Article'}]({article.get('url')})**")
                st.caption(
                    f"Perfil: {feed_profile} | Impacto: {impact_text} | "
                    f"Fonte: {article.get('feed_source') or 'Unknown Source'} | "
                    f"Publicado em: {format_datetime(article.get('published_date'))}"
                )

                processed_content = article.get("processed_content") or "_Sem resumo processado._"
                st.markdown(processed_content)
    
    st.divider()
    _change_page(total_pages=total_pages, current_page=current_page, key_prefix="bottom")

if __name__ == "__main__":
    show()