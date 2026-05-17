"""
AGENT 4 — CREATIVE
"""

import json
import traceback


SYSTEM_PROMPT = """
You are a Creative Director for a marketing platform.

You receive a business, region, trend with real event details, marketing hook, and image direction.

Generate two outputs:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. IMAGE GENERATION PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONE flowing paragraph. Paste-ready for Midjourney or DALL-E.

MUST include real event details — name the event, the moment, the emotion.
  BAD: "a bakery during a festival"
  GOOD: "a Chennai bakery packed with families on the eve of Pongal 2025,
         fresh sweet pongal aroma drifting through the door, golden earthen pots
         stacked in the window display"

Describe: subject → setting → mood → lighting → colors → composition → quality
Write as one continuous paragraph. End with: --no text, logos, watermarks, blurry faces

Always add the current business relevant items in the images 

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. CAMPAIGN BRIEF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - Campaign name (3-5 words, tied to the event)
  - Headline (max 8 words)
  - Body (2 sentences, specific to event + business)
  - CTA (max 4 words)
  - Best channel: Instagram | Facebook | WhatsApp | Poster

OUTPUT FORMAT (strict JSON, no markdown):
{
  "action": "finish",
  "trend": "...",
  "image_prompt": "Full flowing paragraph. --no text, logos, watermarks, blurry faces",
  "campaign_brief": {
    "campaign_name": "...",
    "headline": "...",
    "body": "...",
    "cta": "...",
    "best_channel": "..."
  }
}
"""


def run_creative(opportunity: dict, business_type: str, region: str, llm_client, model: str) -> dict:

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Business: {business_type}\n"
                f"Region: {region}\n"
                f"Trend: {opportunity['trend']}\n"
                f"Real Context: {opportunity['real_context']}\n"
                f"Marketing Hook: {opportunity['marketing_hook']}\n"
                f"Image Direction: {opportunity['image_direction']}\n\n"
                "Generate the image prompt and campaign brief using the real event details."
            )
        },
    ]

    for attempt in range(5):
        try:
            response = llm_client.chat.completions.create(
                model=model, messages=messages, temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            print(f"      [Creative attempt {attempt+1}] raw: {content[:120]}...")

            if content.startswith("```"):
                content = content.split("```")[1].lstrip("json").strip()

            parsed = json.loads(content)
            if parsed.get("action") == "finish":
                if not parsed.get("image_prompt"):
                    raise ValueError("image_prompt is empty")
                print(f"      [Creative] done for trend: {parsed.get('trend')}")
                return parsed

        except (json.JSONDecodeError, ValueError) as e:
            print(f"      [Creative attempt {attempt+1}] error: {e} | content: {content[:200]}")
            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user",
                "content": f"Issue: {e}. Return only valid JSON. Start with {{."
            })

        except Exception as e:
            print(f"      [Creative] unexpected error: {traceback.format_exc()}")
            raise

    raise RuntimeError("Creative agent failed after 5 attempts.")