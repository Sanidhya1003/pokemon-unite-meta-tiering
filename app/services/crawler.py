import requests
from bs4 import BeautifulSoup


def crawl_website(url: str) -> dict:
    """
    Crawl a website and extract basic page-level metrics.
    This is the first version. Later we will expand this into
    a proper extraction strategy node inside LangGraph.
    """

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 AgenticWebTieringBot/1.0"
            },
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else None

        text = soup.get_text(separator=" ", strip=True)
        words = text.split()

        links = soup.find_all("a")
        images = soup.find_all("img")
        headings = soup.find_all(["h1", "h2", "h3"])

        return {
            "url": url,
            "title": title,
            "word_count": len(words),
            "link_count": len(links),
            "image_count": len(images),
            "heading_count": len(headings),
            "status": "success",
        }

    except requests.RequestException as error:
        return {
            "url": url,
            "title": None,
            "word_count": 0,
            "link_count": 0,
            "image_count": 0,
            "heading_count": 0,
            "status": f"error: {str(error)}",
        }