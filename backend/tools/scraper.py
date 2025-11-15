# backend/tools/scraper.py
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def fetch_simple(url, timeout=10):
    """
    Simple requests-based fetch. Good for static pages and small scrapes.
    """
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "agentic-bot/0.1"})
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.warning("fetch_simple failed for %s: %s", url, e)
        return ""

def parse_links(html, base_url=None):
    """
    Return list of (text, href) from html.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        text = (a.get_text() or "").strip()
        href = a["href"]
        links.append({"text": text, "href": href})
    return links

# Playwright example (commented): uncomment and use when playwright is installed.
# from playwright.sync_api import sync_playwright
# def fetch_with_playwright(url, headless=True, timeout=30000):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless)
#         page = browser.new_page()
#         page.goto(url, timeout=timeout)
#         html = page.content()
#         browser.close()
#         return html
