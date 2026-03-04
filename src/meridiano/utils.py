import argparse
import importlib
import logging
import os
import json
from datetime import datetime
from urllib.parse import urljoin

import requests
import trafilatura
from bs4 import BeautifulSoup

from meridiano import config_base as config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger()


# Helper function for date formatting (optional but nice)
def format_datetime(value, format="%Y-%m-%d %H:%M"):
    if value is None:
        return "N/A"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value  # Return original string if parsing fails
    if isinstance(value, datetime):
        return value.strftime(format)
    return value


def fetch_article_content_and_og_image(url):
    """
    Fetches HTML, extracts main content using Trafilatura,
    and extracts the og:image URL using BeautifulSoup.

    Returns:
        dict: {'content': str|None, 'og_image': str|None}
    """
    content = None
    og_image = None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "referer": "https://www.google.com",
        }
        response = requests.get(url, headers=headers, timeout=20)  # Increased timeout slightly
        response.raise_for_status()
        html_content = response.text

        # 1. Extract text content
        content = trafilatura.extract(html_content, include_comments=False, include_tables=False)

        # 2. Extract og:image using BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")  # Use lxml or html.parser
        og_image_tag = soup.find("meta", property="og:image")
        if og_image_tag and og_image_tag.get("content"):
            og_image = og_image_tag["content"]
            # Optionally resolve relative URLs - less common for og:image but possible
            og_image = urljoin(url, og_image)

        return {"content": content, "og_image": og_image}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {"content": None, "og_image": None}
    except Exception as e:
        # Catch potential BeautifulSoup errors or others
        print(f"Error processing content/og:image from {url}: {e}")
        # Still return content if it was extracted before the error
        return {"content": content, "og_image": None}


def scrape_single_article_details(article_url):
    """
    Fetches and extracts details (title, raw_content, image_url) for a single article URL.

    Args:
        article_url (str): The URL of the article to scrape.

    Returns:
        dict: {'title': str|None, 'raw_content': str|None, 'image_url': str|None, 'error': str|None}
              'error' key will be present if fetching/processing failed.
    """
    print(f"Attempting to scrape single article: {article_url}")
    fetched_title = None
    raw_content = None
    final_image_url = None
    error_message = None

    try:
        # Use the existing fetch_article_content_and_og_image helper
        fetch_result = fetch_article_content_and_og_image(article_url)  # This already logs its own errors

        raw_content = fetch_result["content"]
        og_image_url = fetch_result["og_image"]

        if not raw_content:
            # fetch_article_content_and_og_image might have already logged, but good to have a specific error here
            error_message = "Failed to extract main content from the article."
            logger.warning(f"{error_message} URL: {article_url}")
            # Even if content fails, we might still get a title or image from OG tags if fetch worked partially
            # So, continue to try and extract title if possible.

        # --- Attempt to get a title from the page if not from RSS ---
        # We need to re-fetch or use the already fetched HTML if available from fetch_article_content_and_og_image
        # Let's assume fetch_article_content_and_og_image doesn't return the full soup object.
        # If it did, we could reuse it. For now, we might need a minimal re-fetch or a helper modification.
        # Simplification: If trafilatura got content, it often implies page was fetched.
        # We could parse the title from the raw_content's source HTML (if fetch_... stored it)
        # or do another small HEAD request or parse from a snippet.
        # For now, we'll use a placeholder if the feed didn't provide it.
        # A more robust solution would be to enhance fetch_article_content_and_og_image
        # to also return the <title> tag content.

        if raw_content:  # If we got content, try to get title from HTML
            try:
                # Need to parse the HTML again if not already available from previous fetch
                headers = {"User-Agent": "Mozilla/5.0 ..."}  # Your headers
                response = requests.get(article_url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")
                title_tag = soup.find("title")
                if title_tag and title_tag.string:
                    fetched_title = title_tag.string.strip()
                # Fallback to OG title if HTML title is poor/missing
                if not fetched_title:
                    og_title_tag = soup.find("meta", property="og:title")
                    if og_title_tag and og_title_tag.get("content"):
                        fetched_title = og_title_tag["content"].strip()
            except Exception as title_e:
                logger.warning(f"Could not extract title for {article_url}: {title_e}")
                # Continue without title if it fails

        final_image_url = og_image_url  # For a single manual add, OG image is the primary target

        if not raw_content and not fetched_title and not final_image_url:
            # If absolutely nothing was fetched, it's a more significant error
            error_message = "Failed to fetch any content, title, or image from the URL."

    except Exception as e:
        error_message = f"General error scraping single article {article_url}: {e}"
        logger.error(error_message, exc_info=True)

    return {"title": fetched_title, "raw_content": raw_content, "image_url": final_image_url, "error": error_message}

def agrupate_context_and_prompt(prompt: str, context="/home/rafael/Projetos/meridiano/src/meridiano/rag_training_data.json"):
    if "{database_context}" not in prompt:
        return prompt
    
    
    elif "{database_context}" in prompt and not os.path.exists(context):
        prompt = prompt.replace("{database_context}", "Don't have any context available. Disconsider this information.")
        print("Skipping context aggregation for prompt: 'rag_training_data.json' not found.")
        return prompt
    
    with open(context,"r") as f:
        data = json.load(f)

    context = "\n\n".join(
        f"topico: {item['topico']}\n\nexplicação: {item['explicação']}\n\ndesinformativo: {item['desinformativo']}\n\ninformativo: {item['informativo']}\n" for item in data
    )

    prompt = prompt.replace("{database_context}", context)
    
    return prompt


def str_to_parser(
    feed: str,
    scrape: bool,
    process: bool,
    generate: bool,
    rate: bool,
    run_all: bool = False,
    model: str | None = None,
    limit: int = 1000,
):
    """
    Returns a tuple of (args, feed_profile_name, effective_config) based on the provided parameters and configuration files.

    :param feed: The feed profile name to use (e.g. "Brasil").
    :param scrape: True if the scraping stage should be executed
    :param process: True if the processing stage should be executed
    :param generate: True if the briefing generation stage should be executed
    :param rate: True if the rating stage should be executed
    :param run_all: True if all stages should be executed (overrides individual stage flags)
    :param model: Optional model name to override the default LLM chat model
    :param limit: Optional limit for number of articles to process/scrape

    :return: A tuple of (args, feed_profile_name, effective_config)
    """
    feed_profile_name = feed or config.DEFAULT_FEED_PROFILE

    args = argparse.Namespace(
        feed=feed_profile_name,
        scrape=bool(scrape),
        process=bool(process),
        generate=bool(generate),
        rate=bool(rate),
        run_all=bool(run_all),
        model=model,
        limit=int(limit),
    )

    feed_config = None
    rss_feeds = None

    try:
        feed_module_name = f".feeds.{feed_profile_name}"
        feed_config = importlib.import_module(feed_module_name, package="meridiano")
    except ImportError:
        try:
            feed_module_name = f"feeds.{feed_profile_name}"
            feed_config = importlib.import_module(feed_module_name)
        except ImportError as exc:
            raise ValueError(
                f"Não foi possível importar a configuração do feed '{feed_profile_name}'. "
                f"Verifique se o arquivo 'src/meridiano/feeds/{feed_profile_name}.py' existe."
            ) from exc

    if feed_config:
        rss_feeds = getattr(feed_config, "RSS_FEEDS", [])

    effective_config_dict = {k: v for k, v in config.__dict__.items() if not k.startswith("__")}
    if feed_config:
        for key, value in feed_config.__dict__.items():
            if not key.startswith("__"):
                effective_config_dict[key] = value

    class EffectiveConfig:
        def __init__(self, dictionary):
            for key, value in dictionary.items():
                setattr(self, key, value)

    effective_config = EffectiveConfig(effective_config_dict)

    if rss_feeds is not None:
        effective_config.RSS_FEEDS = rss_feeds

    if args.model:
        if args.model.startswith("ollama:") and "/" not in args.model:
            args.model = args.model.replace("ollama:", "ollama/", 1)

        effective_config.LLM_CHAT_MODEL = args.model

    return args, feed_profile_name, effective_config


""" --- Minhas adições --- """
""" Criador de database """
def cria_arquivo_veracidade(artigos: dict) -> None:
    with open("veracidade_discrepancias.csv", "w") as f:
        f.write("id,veracidade_final,veracidade_llm,veracidade_kmeans,url,conteudo\n")
        for id, article in artigos.items():
            f.write(f"{id},{article['veracidade']},{article['veracidade_llm']},{article['veracidade_kmeans']},{article['url']},\"{article['raw_content'].replace('\"', '\"\"')}...\"\n")