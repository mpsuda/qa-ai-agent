import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("ERRO: API Key não encontrada.")
    exit()

print("API Key encontrada.")

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": "Responda apenas: Conexão com Claude realizada com sucesso."
        }
    ]
)

for block in message.content:
    if block.type == "text":
        print(block.text)