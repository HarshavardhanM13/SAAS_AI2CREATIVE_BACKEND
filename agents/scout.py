"""
AGENT 1 - SCOUT
Top 3 trends → 2 news articles each → LLM picks best creative angle for the business.
"""

import json
from tools.trends import get_trending_keywords
from tools.search import google_news_search


PICK_PROMPT = """
You are a creative marketing strategist.

You have today's top trending news. Pick the BEST marketing opportunity for the business.
It does NOT have to be directly related — find the most creative, emotionally resonant connection.

Return ONLY this JSON. No prose. Start with {:
{
  "signals": [
    {
      "headline": "trending topic name",
      "real_details": "what is actually happening - specific facts",
      "creative_connection": "how to connect this trend to the business creatively",
      "emotion": "excitement | joy | nostalgia | urgency | pride | curiosity"
    }
  ]
}

Pick the top 2 best angles only.
"""


def run_scout(region: str, business_type: str, llm_client, model: str) -> list[dict]:

    # Step 1: Top 3 trending keywords
    print(f"      [Scout] fetching top 3 trends...")
    try:
        keywords = get_trending_keywords(region)
    except Exception as e:
        print(f"      [Scout] Trends failed: {e}. Using fallback.")
        keywords = [f"{region} events today", f"trending India today"]

    # Step 2: Top 2 news articles per keyword
    print(f"      [Scout] fetching news for {len(keywords)} trends...")
    all_news = []
    for kw in keywords:
        try:
            articles = google_news_search(kw)
            if articles:
                all_news.append({"trend": kw, "articles": articles})
                print(f"         '{kw}' → {len(articles)} articles")
        except Exception as e:
            print(f"         '{kw}' failed: {e}")

    if not all_news:
        raise RuntimeError("Scout: all news searches failed. Check SERP_API_KEY.")

    # Step 3: LLM picks best creative connections
    print(f"      [Scout] LLM picking best angles...")
    for attempt in range(4):
        resp = llm_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": PICK_PROMPT},
                {"role": "user", "content": (
                    f"Business: {business_type}\n"
                    f"Region: {region}\n\n"
                    f"TRENDING NEWS:\n{json.dumps(all_news, indent=2)}\n\n"
                    "Pick the top 2 most creatively marketable for this business."
                )},
            ],
            temperature=0.3,
        )

        content = resp.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1].lstrip("json").strip()
        start, end = content.find("{"), content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]
        try:
            signals = json.loads(content).get("signals", [])
            print(f"      [Scout] picked {len(signals)} signals:")
            for s in signals:
                print(f"         - {s.get('headline')} | {s.get('emotion')}")
            return signals
        except json.JSONDecodeError as e:
            print(f"      [Scout] parse error attempt {attempt+1}: {e}")
            continue

    return []