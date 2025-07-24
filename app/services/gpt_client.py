import os
from openai import OpenAI

class GPTClient:
    """
    Wraps OpenAI to format a database query response
    into a concise, no-emoji, no-follow-up WhatsApp message.
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def format_response(
        self,
        question: str,
        sql: str,
        executed_sql: str,
        ai_response: str,
        data: list
    ) -> str:
        MODEL      = "gpt-4.1-mini"
        MAX_TOKENS = 800

        instructions = [
            "You are a helpful assistant that formats/make sense of database query results for WhatsApp.",
            "Do NOT use emojis.",
            "Do NOT ask follow‑up questions.",
            "Provide a concise human‑friendly reply in plain text only while referring to the data.",
            "If the user's question contains 'display all' or 'show all', include the entire data set; otherwise limit to the first 5 rows."
        ]

        prompt = "\n".join(instructions) + "\n\n"
        prompt += f"User asked: {question}\n"
        prompt += f"SQL:```{sql}```\n"
        if executed_sql and executed_sql != sql:
            prompt += f"Executed SQL:```{executed_sql}```\n"
        prompt += f"AI response: {ai_response}\n"
        prompt += f"Results: {data}\n\n"
        prompt += "Generate the WhatsApp reply below:"

        resp = self.client.chat.completions.create(
            model      = MODEL,
            messages   = [{"role": "user", "content": prompt}],
            max_tokens = MAX_TOKENS,
            timeout    = 20
        )
        return resp.choices[0].message.content.strip()
