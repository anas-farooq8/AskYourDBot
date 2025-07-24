import time
from app.services.gpt_client import GPTClient
from app.services.ask_your_database import AskYourDatabaseClient

gpt = GPTClient()
ayd = AskYourDatabaseClient()

def process_incoming(text: str) -> dict:
    """
    1) Classify: is this a stock/BOM question?
    2) If yes: forward to AskYourDatabase.
    3) Use GPT to format the AYD response.
    """
    # 1) Classification step
    start = time.time()
    is_question = gpt.is_relevant_question(text)
    duration = time.time() - start
    print(f"🔍 Classification: {'YES' if is_question else 'NO'} in {duration:.2f}s", flush=True)

    if not is_question:
        # If it's not a stock/BOM query, give a canned reply
        return {"success": True, "aiResponse": "Ask me about fabric stock or BOM."}

    # 2) Call AskYourDatabase
    start = time.time()
    result = ayd.ask(text)
    duration = time.time() - start
    print(f"🔍 AYD result: {result} in {duration:.2f}s", flush=True)

    if not result["success"]:
        # Propagate errors (e.g. timeout, HTTPError, AYD error payloads)
        return result

    # 3) Format via GPT
    start = time.time()
    formatted = gpt.format_response(
        question=text,
        sql=result["sql"],
        executed_sql=result["executedSql"],
        data=result["data"]
    )
    duration = time.time() - start
    print(f"🔍 GPT formatting in {duration:.2f}s:\n{formatted}", flush=True)

    # Return only the human‑friendly reply
    return {"success": True, "aiResponse": formatted, "data": []}
