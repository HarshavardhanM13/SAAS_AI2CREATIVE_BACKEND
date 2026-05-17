import os, requests
from dotenv import load_dotenv
load_dotenv()

def google_news_search(query: str, region_code: str = "in") -> list[dict]:
    key = os.getenv("SERP_API_KEY")
    if not key: raise EnvironmentError("SERP_API_KEY not set.")

    r = requests.get("https://serpapi.com/search", params={
        "engine": "google", "q": query, "tbm": "nws",
        "api_key": key, "gl": region_code, "hl": "en", "num": 2,
    }, timeout=20)
    r.raise_for_status()

    results = []
    for item in r.json().get("news_results", [])[:2]:
        t = item.get("title", "").strip()
        s = item.get("snippet", "").strip()
        if t and s:
            results.append({
                "title": t,
                "snippet": s,
                "date": item.get("date", ""),
            })
    return results