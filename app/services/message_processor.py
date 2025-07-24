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
    # call AYD
    start_time = time.time()
    result = ayd.ask(text)
    end_time = time.time()
    print(f"🔍 AYD result: {result} in {end_time - start_time} seconds", flush=True)
    if not result["success"]:
        return result

    # format via GPT
    start_time = time.time()
    formatted = gpt.format_response(
        question=text,
        sql=result["sql"],
        executed_sql=result["executedSql"],
        data=result["data"]
    )
    end_time = time.time()
    print(f"🔍 GPT result: {formatted} in {end_time - start_time} seconds", flush=True)
    # Truncate if needed
    return {"success": True, "aiResponse": formatted, "data": []}
