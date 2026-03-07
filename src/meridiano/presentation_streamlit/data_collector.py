import streamlit as st
import os

from meridiano import config_base as config
from meridiano.run_briefing import extern_execution


def _reset_scraping_state():
    st.session_state.show_scraping_confirm = False
    st.session_state.scrape_confirmed = False
    st.session_state.scrape_cancelled = False
    st.session_state.pending_feed = ""
    st.session_state.selected_feed = ""
    

def show():
    st.header("📰 Coletor de Dados")

    if "show_scraping_confirm" not in st.session_state:
        st.session_state.show_scraping_confirm = False
    if "scrape_confirmed" not in st.session_state:
        st.session_state.scrape_confirmed = False
    if "scrape_cancelled" not in st.session_state:
        st.session_state.scrape_cancelled = False
    if "pending_feed" not in st.session_state:
        st.session_state.pending_feed = ""
    if "selected_feed" not in st.session_state:
        st.session_state.selected_feed = ""

    available_feeds = os.listdir("src/meridiano/feeds")
    available_feeds = [feed for feed in available_feeds if feed.endswith(".py") and not feed.startswith("_")]
    profile_options = [""] + available_feeds
    profile_labels = {"": "Nenhum feed", **{feed: feed.replace(".py", "").replace("_", " ").title() for feed in available_feeds}}

    st.session_state.selected_feed = st.selectbox(
        "Selecione o feed:",
        options=profile_options,
        format_func=lambda x: profile_labels.get(x, x),
        index=profile_options.index(st.session_state.get("data_collector_feed", ""))
        if st.session_state.get("data_collector_feed") in profile_options
        else 0,
    )

    @st.dialog("Confirmar scraping")
    def confirm_scraping_dialog():
        pending_feed = st.session_state.get("pending_feed", "")
        st.error(
            f"O processo de scraping do feed {profile_labels.get(pending_feed, pending_feed)} irá iniciar. Deseja continuar?"
        )

        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Confirmar", key="confirm_scraping"):
                st.session_state.show_scraping_confirm = False
                st.session_state.scrape_confirmed = True

        with col_cancel:
            if st.button("Cancelar", key="cancel_scraping"):
                st.session_state.show_scraping_confirm = False
                st.session_state.scrape_cancelled = True
                st.session_state.pending_feed = ""

    # botão para iniciar o processo de scraping
    if st.button("Iniciar Scraping"):
        if st.session_state.selected_feed and st.session_state.selected_feed != "":
            st.session_state.pending_feed = st.session_state.selected_feed
            st.session_state.show_scraping_confirm = True

        else:
            st.warning("Por favor, selecione um feed para iniciar o processo de scraping.")
            _reset_scraping_state()
            return

    if st.session_state.show_scraping_confirm:
        confirm_scraping_dialog()
        return

    if st.session_state.scrape_cancelled:
        st.session_state.scrape_cancelled = False
        st.warning("Processo de scraping cancelado.")
        _reset_scraping_state()
        return

    if st.session_state.scrape_confirmed:
        selected_confirmed_feed = st.session_state.pending_feed

        st.write(f"Iniciando o processo de scraping para o feed: {profile_labels[selected_confirmed_feed]}")

        st.session_state.arg.scrape = True
        st.session_state.arg.feed = selected_confirmed_feed.replace(".py", "")
        st.session_state.feed_profile_name = st.session_state.arg.feed
        """"""
        with st.spinner("Executando o processo de scraping..."):
            try:
                success = extern_execution(
                    st.session_state.arg,
                    st.session_state.feed_profile_name,
                    st.session_state.effective_config,
                )
                if success:
                    st.success("Processo de scraping concluído com sucesso!")
                    return

                st.error("O processo de scraping falhou. Verifique os logs para mais detalhes.")
                return
            finally:
                _reset_scraping_state()



if __name__ == "__main__":
    show()