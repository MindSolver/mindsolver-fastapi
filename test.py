from openai import AsyncOpenAI
import os 
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

load_dotenv('env/.env')

client = AsyncOpenAI(api_key=os.getenv('OPEN_AI_KEY'))

async def main():
    response_data = ""
    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Give me 10 sentences with more than 20 words each"}],
        stream=True,
    )
    async for chunk in stream:
        response_data += chunk.choices[0].delta.content or ""
        # print("first:", chunk)
        # 여기에서 response_data를 작은 단위로 나누고 출력합니다.
        # 예를 들어, 각 글자 또는 단어 단위로 나누어 출력할 수 있습니다.
        for char in response_data:
            print(char, end="")

asyncio.run(main())