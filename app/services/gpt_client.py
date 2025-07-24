import os
from openai import OpenAI

class GPTClient:
    """
    Client wrapping the OpenAI API for:
      1) Classifying whether a user message is about fabric stock/BOM.
      2) Formatting database query results into a WhatsApp-friendly reply.
    """

    def __init__(self):
        # Instantiate the OpenAI client using the API key from the environment
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def is_relevant_question(self, text: str) -> bool:
        """
        Send a few-shot prompt to classify if `text` is about fabric stock, BOM,
        or related database queries. Returns True for 'YES', False for 'NO'.
        """
        # System prompt instructs the model to reply only 'YES' or 'NO'
        system_prompt = (
            "You are a strict classifier. Respond *only* with 'YES' or 'NO'.\n"
            "Reply 'YES' if the user is asking about fabric stock, BOM, database queries,\n"
            "or mentions textile terms such as 'linen', 'bluejeans', or 'riwaz', 'valencia'; otherwise 'NO'."
        )

        # Few‑shot examples to guide the classification behavior
        messages = [
            {"role": "system",    "content": system_prompt},
            {"role": "user",      "content": "What is the current stock level for SKU 12345?"},
            {"role": "assistant", "content": "YES"},
            {"role": "user",      "content": "Hello, how are you today?"},
            {"role": "assistant", "content": "NO"},
            {"role": "user",      "content": "Show me the BOM for part ABC678."},
            {"role": "assistant", "content": "YES"},
            # Finally, the actual user query to classify
            {"role": "user",      "content": text}
        ]

        # Call the chat completion endpoint with max_tokens=1 to get a single-token answer
        resp = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=1,
            timeout=5  # Fail quickly if the model doesn't respond
        )

        # Normalize the response and return True if it is 'YES'
        return resp.choices[0].message.content.strip().upper() == "YES"

    def format_response(
        self,
        question: str,
        sql: str,
        executed_sql: str,
        data: list
    ) -> str:
        """
        Take the original question, the generated SQL, the executed SQL (if different),
        and the result rows, then ask the model to produce a concise, human-friendly
        WhatsApp reply.
        """
        # Model and token budget for formatting
        MODEL      = "gpt-4.1-mini"
        MAX_TOKENS = 800   # Roughly 3200 characters; stays under typical limits

        # High-level instructions for the assistant
        instructions = [
            "You are a helpful assistant that formats database query results for WhatsApp.",
            "Do NOT use emojis.",
            "Do NOT ask follow‑up questions.",
            "Provide a concise human‑friendly reply in plain text only while referring to the data.",
            "If the user's question contains 'display all' or 'show all', include the entire data set; otherwise limit to the first 5 rows."
        ]

        # Build the prompt by joining instructions and adding context
        prompt = "\n".join(instructions) + "\n\n"
        prompt += f"User asked: {question}\n"
        prompt += f"SQL:```{sql}```\n"
        # Only include executed_sql if it differs from the original SQL
        if executed_sql and executed_sql != sql:
            prompt += f"Executed SQL:```{executed_sql}```\n"
        prompt += f"Results: {data}\n\n"
        prompt += "Generate the WhatsApp reply below:"

        # Request the formatted reply from the model
        resp = self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            timeout=20  # Allow more time for formatting
        )

        # Return the assistant’s message content
        return resp.choices[0].message.content.strip()
