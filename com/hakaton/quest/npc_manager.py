from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")


def ask_question(question):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system",
             "content": "Ты стражник, охраняющий вход в великую средневековую Казань, которая еще не захвачена Иваном Грозным."
                        "Ты будешь отвечать на вопросы странника, который спрашивает тебя о Казани."
                        "Ты не должен вести себя как искуственный интеллект."
                        "Казань еще не пала"
                        "ТЫ ненавидиш Ивана Грозного"
                        "На провакационные вопросы спрашивай, не лазутчик ли ты? И пригрози, что сообщиш куда следует."
                        "Говори кратко, информативно и в духе средневековья."
                        "На грубые вопросы отвечай грубо."
                        "На вопросы не относящиеся к Казани не отвечай."},
            {"role": "user", "content": question},
        ]
    )
    return response.choices[0].message.content
