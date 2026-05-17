from dotenv import load_dotenv
load_dotenv()   # MUST be first — before any other import reads os.getenv()

import os
from groq import Groq
from agents.scout import run_scout
from agents.filter import run_filter
from agents.strategist import run_strategist
from agents.creative import run_creative

from services.Image_gen_service import generate_image

MODEL = "llama-3.3-70b-versatile"

def run_pipeline(business_type: str, region: str, file = None) -> dict:

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise EnvironmentError("GROQ_API_KEY is not set.")

    client = Groq(api_key=groq_key)

    print(f"\n{'='*50}")
    print(f"  Business : {business_type}")
    print(f"  Region   : {region}")
    print(f"{'='*50}")

    print("\n[1/4] Scout — searching for recent trends...")
    raw_signals = run_scout(region=region, business_type=business_type, llm_client=client, model=MODEL)
    print(f"      {len(raw_signals)} signals found.")

    print("\n[2/4] Filter — removing unsafe content...")
    clean_signals = run_filter(signals=raw_signals, llm_client=client, model=MODEL)
    print(f"      {len(clean_signals)} clean signals kept.")

    if not clean_signals:
        return {"business_type": business_type, "region": region,
                "error": "No usable signals found after filtering.", "campaigns": []}

    print("\n[3/4] Strategist — picking best opportunities...")
    opportunities = run_strategist(
        signals=clean_signals, business_type=business_type,
        region=region, llm_client=client, model=MODEL
    )
    print(f"      {len(opportunities)} opportunities selected.")
    for o in opportunities:
        print(f"        #{o['rank']} [{o['score']}/100] {o['trend']}")

    if not opportunities:
        return {"business_type": business_type, "region": region,
                "error": "No strong trend-business matches found.", "campaigns": []}

    print("\n[4/4] Creative — generating prompts and briefs...")
    campaigns = []
    for opp in opportunities:
        print(f"      → {opp['trend']}")
        creative = run_creative(
            opportunity=opp, business_type=business_type,
            region=region, llm_client=client, model=MODEL
        )
        campaigns.append(creative)

    print(f"\n✓ Done. {len(campaigns)} campaigns ready.")\
    
    results = []
    print("file : ",file)
    for campaign in campaigns:
        results.append(generate_image(data=campaign['image_prompt'], file=file))
    return results
    # return {"business_type": business_type, "region": region, "campaigns": campaigns}