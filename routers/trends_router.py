from fastapi import FastAPI, HTTPException,APIRouter
from dotenv import load_dotenv
from groq import Groq

import requests
import os
import json
import re

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================================================
# APP
# =========================================================

app = APIRouter()

# =========================================================
# LLM
# =========================================================

client = Groq(
    api_key=GROQ_API_KEY
)

# =========================================================
# GOOGLE SEARCH TOOL
# =========================================================

def google_search_tool(query):

    url = "https://serpapi.com/search"

    params = {

        "engine": "google",

        "q": query,

        "api_key": SERP_API_KEY,

        "gl": "in",

        "hl": "en"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    data = response.json()

    organic_results = data.get(
        "organic_results",
        []
    )

    cleaned = []

    for result in organic_results[:5]:

        cleaned.append({

            "title": result.get(
                "title",
                ""
            ),

            "snippet": result.get(
                "snippet",
                ""
            ),

            "source": result.get(
                "displayed_link",
                ""
            )
        })

    return cleaned


# =========================================================
# TOOL EXECUTOR
# =========================================================

def execute_tool(tool_name, arguments):

    if tool_name == "google_search":

        query = arguments.get("query")

        return google_search_tool(query)

    return {
        "error": "Unknown tool"
    }


# =========================================================
# AGENT LOOP
# =========================================================

def run_agent(

    business_type,
    region

):

    system_prompt = f"""
You are an autonomous marketing intelligence agent.

You have access to tools.

AVAILABLE TOOL:
1. google_search

TOOL FORMAT:
{{
  "tool": "google_search",
  "arguments": {{
      "query": "Tamil Nadu gaming events"
  }}
}}

BUSINESS:
{business_type}

REGION:
{region}

YOUR JOB:
1. Decide what searches to perform
2. Collect market signals
3. Analyze opportunities
4. Rank best trends
5. Generate campaigns

IMPORTANT RULES:
- Never hallucinate
- Only use tool results
- Ignore irrelevant politics
- Ignore accidents/crime
- Ignore unrelated celebrity gossip
- Focus on business opportunities
- Focus on customer attention

WORKFLOW:
Step 1:
Call tools.

Step 2:
After enough information,
return FINAL JSON.

FINAL OUTPUT FORMAT:
{{
  "ranked_trends": [
    {{
      "rank": 1,
      "trend": "...",
      "score": 95,
      "why_relevant": "...",
      "marketing_angle": "..."
    }}
  ],

  "campaigns": [
    {{
      "trend": "...",
      "campaign_name": "...",
      "ad_angle": "...",
      "visual_idea": "...",
      "target_emotion": "..."
    }}
  ]
}}

IMPORTANT:
- Do not hallucinate
- Use ONLY gathered signals
- Return ONLY JSON
"""

    messages = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": (
                f"Find market opportunities for "
                f"{business_type} in {region}"
            )
        }
    ]

    for _ in range(5):

        completion = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=messages,

            temperature=0
        )

        response = (
            completion
            .choices[0]
            .message
            .content
        )

        # =====================================
        # TRY TOOL CALL
        # =====================================

        try:

            tool_data = json.loads(response)

            if "tool" in tool_data:

                tool_name = tool_data["tool"]

                arguments = tool_data["arguments"]

                tool_result = execute_tool(
                    tool_name,
                    arguments
                )

                messages.append({

                    "role": "assistant",
                    "content": response
                })

                messages.append({

                    "role": "user",

                    "content": (
                        "TOOL RESULT:\n"
                        f"{json.dumps(tool_result)}"
                    )
                })

                continue

            else:
                return tool_data

        except:
            pass

        # =====================================
        # FINAL OUTPUT
        # =====================================

        try:
            return json.loads(response)

        except:
            continue

    raise Exception(
        "Agent failed"
    )


# =========================================================
# API
# =========================================================

@app.get("/agent-marketing")

def agent_marketing(

    business_type: str,
    region: str

):

    if not SERP_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="SERP_API_KEY missing"
        )

    if not GROQ_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY missing"
        )

    try:

        result = run_agent(

            business_type=business_type,

            region=region
        )

        return {

            "business_type": business_type,

            "region": region,

            "agent_output": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )