import os 
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import AsyncOpenAI

app = FastAPI()
load_dotenv('env/.env')

client = AsyncOpenAI(api_key=os.getenv('OPEN_AI_KEY'))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/gpt3.5")
async def test_gpt4():
    async def generator():
        stream = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "hello give me 20 sentence"}],
            stream=True,
        )
        async for chunk in stream:
            yield chunk.choices[0].delta.content or ""

    return StreamingResponse(generator(), media_type="text/event-stream")

@app.get("/gpt4-async")
async def test_gpt4():
    async def generator():
        stream = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Give me 10 sentences with more than 20 words each"}],
            stream=True,
        )
        async for chunk in stream:
            yield chunk.choices[0].delta.content or ""

    return StreamingResponse(generator(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)