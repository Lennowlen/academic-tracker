import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv("/home/tifa/Kuliah/sains_data/academic-tracker/.env")

async def test_call():
    url = "http://localhost:20128/v1/chat/completions"
    payload = {
        "model": "antigravity/claude-sonnet-4-6",
        "messages": [{"role": "user", "content": "Test"}],
        "stream": False
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_call())
