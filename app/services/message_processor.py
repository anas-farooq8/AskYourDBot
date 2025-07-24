import time
import json
from app.services.ask_your_database import AskYourDatabaseClient
from app.services.gpt_client         import GPTClient

ayd = AskYourDatabaseClient()
gpt = GPTClient()

def process_incoming(text: str) -> dict:
    """
    1) Send the raw text to AskYourDatabase.
    2) Take its SQL, executedSql, aiResponse, and data.
    3) Ask GPT to format a WhatsApp‑friendly reply.
    """
    # 1) AskYourDatabase call
    start = time.time()
    result = ayd.ask(text)
    duration = time.time() - start
    print(f"🔍 AYD call took {duration:.2f}s, success={result.get('success')}", flush=True)
    print(json.dumps(result, indent=2), flush=True)

    if not result["success"]:
        return result

    # 2) GPT formatting
    start = time.time()
    formatted = gpt.format_response(
        question     = text,
        sql          = result["sql"],
        executed_sql = result.get("executedSql", ""),
        ai_response  = result.get("aiResponse", ""),
        data         = result.get("data", [])
    )
    duration = time.time() - start
    print(f"🔍 GPT formatting took {duration:.2f}s", flush=True)
    print(formatted, flush=True)

    return {"success": True, "aiResponse": formatted}
