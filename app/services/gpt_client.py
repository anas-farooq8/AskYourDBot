import os
from openai import OpenAI

class GPTClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def is_relevant_question(self, text: str) -> bool:
        # Use gpt-3.5-turbo for fast classification
        system_prompt = (
            "You are a strict classifier. Respond *only* with 'YES' or 'NO'.\n"
            "Reply 'YES' if the user is asking about fabric stock, BOM, database queries,\n"
            "or mentions textile terms such as 'linen', 'bluejeans', or 'riwaz', 'valencia'; otherwise 'NO'."
        )
        messages = [
            {"role": "system",    "content": system_prompt},

            # existing few‑shot examples
            {"role": "user",      "content": "What is the current stock level for SKU 12345?"},
            {"role": "assistant", "content": "YES"},
            {"role": "user",      "content": "Hello, how are you today?"},
            {"role": "assistant", "content": "NO"},
            {"role": "user",      "content": "Show me the BOM for part ABC678."},
            {"role": "assistant", "content": "YES"},
            # actual query
            {"role": "user",      "content": text}
        ]
        resp = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1,
            timeout=5
        )
        return resp.choices[0].message.content.strip().upper() == "YES"

    def format_response(
        self,
        question: str,
        sql: str,
        executed_sql: str,
        data: list
    ) -> str:
        # Use GPT‑4 for high-fidelity formatting
        MODEL      = "gpt-4.1-mini"
        MAX_TOKENS = 800   # ≈ 3200 chars; safe under 4096‑char limit

        instructions = [
            "You are a helpful assistant that formats database query results for WhatsApp.",
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
        prompt += f"Results: {data}\n\n"
        prompt += "Generate the WhatsApp reply below:"

        resp = self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            timeout=20
        )
        return resp.choices[0].message.content.strip()
