from openai import OpenAI

from com.hakaton.quest import content
from config import API_KEY

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")


def ask_question(question):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system",
             "content": content.guard},
            {"role": "user", "content": question},
        ]
    )
    return response.choices[0].message.content
