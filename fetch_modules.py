import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def fetch_ebooks():
    url = "https://univterbuka.kotobee.com/library/ebook/all"
    payload = {
        "env": "library",
        "email": os.getenv("KOTOBEE_EMAIL"),
        "pwd": os.getenv("KOTOBEE_PWD"),
        "cloudid": os.getenv("KOTOBEE_CLOUDID"),
        "fingerprint": "f5def864d28a3a4e5cf270d40d92ee3e",
        "account": "true",
        "max": 20,
        "v": "1.8",
        "includeauthor": 1,
        "includecategory": 1
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, data=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            data = resp.json()
            if data and "ebooks" in data:
                print(f"Found {len(data['ebooks'])} ebooks.")
                for ebook in data["ebooks"]:
                    print(f"- {ebook['title']} (ID: {ebook['id']})")
            else:
                print("No ebooks found or unexpected response.")
                print(data)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_ebooks())
