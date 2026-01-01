from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a supportive, empathetic mental health assistant.
You do not diagnose or replace professional help.
You respond calmly, respectfully, and safely.
"""


def build_prompt(message: str, context: str) -> str:
    return f"""
Context (trusted information):
{context}

User message:
{message}

Respond with empathy, validation, and gentle guidance.
Avoid medical diagnosis.
"""


def generate_response(message: str, context: str) -> str:
    """
    Generates a grounded and empathetic response using RAG.
    """
    prompt = build_prompt(message, context)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()
