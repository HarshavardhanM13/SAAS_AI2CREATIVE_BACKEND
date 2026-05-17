"""
AGENT 3 - STRATEGIST
Pick the top 2 signals. Define exactly how to use them.
"""
import json

SYSTEM_PROMPT = """
You are a marketing strategist. Pick the TOP 2 most powerful opportunities from the signals.

Score each 0-100 based on:
  - Creative potential for the business (50pts)
  - Current emotional pull of the trend (50pts)

Return ONLY this JSON:
{
  "action": "finish",
  "opportunities": [
    {
      "rank": 1,
      "trend": "...",
      "score": 88,
      "real_context": "Specific facts about what is happening right now",
      "marketing_hook": "The exact creative angle - how to tie trend to business",
      "emotion": "...",
      "image_direction": "What the marketing image should show and feel - be vivid and specific"
    }
  ]
}
"""

def run_strategist(signals: list[dict], business_type: str, region: str, llm_client, model: str) -> list[dict]:
    if not signals:
        return []

    for _ in range(3):
        resp = llm_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"Business: {business_type}\nRegion: {region}\n\n"
                    f"Signals:\n{json.dumps(signals, indent=2)}\n\nPick top 2."
                )},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1].lstrip("json").strip()
        start, end = content.find("{"), content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]
        try:
            parsed = json.loads(content)
            if parsed.get("action") == "finish":
                opps = parsed.get("opportunities", [])
                print(f"      [Strategist] {len(opps)} opportunities.")
                for o in opps:
                    print(f"         #{o['rank']} [{o['score']}/100] {o['trend']}")
                return opps
        except json.JSONDecodeError:
            continue
    return []