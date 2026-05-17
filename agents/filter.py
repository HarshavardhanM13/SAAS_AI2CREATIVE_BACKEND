"""
AGENT 2 - FILTER
Remove brand-unsafe signals. Keep everything else.
"""
import json

SYSTEM_PROMPT = """
Remove signals where the creative_connection involves: crime, violence, tragedy, political controversy.
Keep everything else — even indirect or unexpected connections are fine.

Return ONLY this JSON:
{
  "action": "finish",
  "clean_signals": [
    {
      "headline": "...",
      "real_details": "...",
      "creative_connection": "...",
      "emotion": "..."
    }
  ]
}
"""

def run_filter(signals: list[dict], llm_client, model: str) -> list[dict]:
    if not signals:
        return []

    for _ in range(3):
        resp = llm_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Filter:\n{json.dumps(signals, indent=2)}"},
            ],
            temperature=0,
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
                result = parsed.get("clean_signals", [])
                print(f"      [Filter] kept {len(result)}/{len(signals)} signals.")
                return result
        except json.JSONDecodeError:
            continue
    return signals  # if filter fails, pass through