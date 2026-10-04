import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
import re

def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    指定URLのHTMLを取得する。

    Args:
        url: 取得対象URL
        timeout: タイムアウト秒数
    
    Returns:
        HTML文字列。失敗時は None
    """
    try:
        headers = {"User-Agent": "Tech0SearchBot/1.0 (Educational Purpose)"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except requests.RequestException as e:
        print(f"✖ 取得エラー: {e}")
        return None

def parse_html(html: str, url: str) -> dict:
    """
    HTMLを解析してページ情報を抽出する。

    Args:
        html: HTML文字列
        url: 元URL
    
    Returns:
        抽出した情報の辞書
    """

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = "No Title"
    if soup.find("title"):
        title = soup.find("title").get_text().strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()

    description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        description = meta["content"][:200]

    keywords = []
    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    if meta_kw and meta_kw.get("content"):
        keywords = [kw.strip() for kw in meta_kw["content"].split(",")][:10]

    elems = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td"])
    full_text = " ".join(e.get_text().strip() for e in elems)
    full_text = re.sub(r"\s+", " ", full_text).strip()

    links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith("http")
    ][:20]

    return {
        "url": url,
        "title": title,
        "description": description,
        "keywords": keywords,
        "full_text": full_text,
        "links": links,
        "word_count": len(full_text.split()),
        "crawl_at": datetime.now().isoformat(),
        "crawl_status": "success",
    }

def crawl_url(url: str) -> dict:
    """
    URLをクロールして情報を返す（fetch → parseのワンストップ）。

    Args:
        url: クロール対象URL

    Returns:
        ページ情報の辞書（失敗時も crawl_status で判別可能）
    """

    html = fetch_page(url)

    if not html:
        return {
            "url": url,
            "crawl_status": "failed",
            "crawled_at": datetime.now().isoformat(),
            "error": "Failed to fetch page",
        }

    try:
        return parse_html(html, url)
    except Exception as e:
        return {
            "url": url,
            "crawl_status": "error",
            "crawled_at": datetime.now().isoformat(),
            "error": str(e),
        }
