import os, requests
from dotenv import load_dotenv
load_dotenv()

GEO_MAP = {
    "tamil nadu": "IN-TN", "chennai": "IN-TN",
    "maharashtra": "IN-MH", "mumbai": "IN-MH",
    "karnataka": "IN-KA", "bangalore": "IN-KA", "bengaluru": "IN-KA",
    "delhi": "IN-DL", "kerala": "IN-KL",
    "telangana": "IN-TG", "hyderabad": "IN-TG",
}

def _geo(region):
    r = region.lower()
    for k, v in GEO_MAP.items():
        if k in r: return v
    return "IN"

def get_trending_keywords(region: str) -> list[str]:
    key = os.getenv("SERP_API_KEY")
    if not key: raise EnvironmentError("SERP_API_KEY not set.")

    r = requests.get("https://serpapi.com/search", params={
        "engine": "google_trends_trending_now",
        "geo": _geo(region),
        "hours": "24",
        "api_key": key,
    }, timeout=20)
    r.raise_for_status()

    trends = r.json().get("trending_searches", [])
    sorted_trends = sorted(trends, key=lambda x: x.get("search_volume", 0), reverse=True)
    keywords = [t.get("query", "") for t in sorted_trends[:3] if t.get("query")]
    print(f"      [Trends] top 3: {keywords}")
    return keywords