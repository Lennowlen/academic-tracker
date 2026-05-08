import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv('/home/tifa/Kuliah/sains_data/academic-tracker/.env')

async def test():
    sess = os.getenv('MOODLE_SESSION')
    key = os.getenv('MOODLE_SESSKEY')
    url = f'https://elearning.ut.ac.id/lib/ajax/service.php?sesskey={key}&info=core_calendar_get_action_events_by_timesort'
    payload = [{'index': 0, 'methodname': 'core_calendar_get_action_events_by_timesort', 'args': {'limitnum': 10}}]
    headers = {
        'Cookie': f'MoodleSession={sess}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
    }
    async with httpx.AsyncClient() as c:
        try:
            r = await c.post(url, json=payload, headers=headers)
            print(f"Status: {r.status_code}")
            data = r.json()
            if data and data[0].get('error'):
                print(f"Error: {data[0]['exception']}")
            else:
                events = data[0]['data']['events']
                print(f"Found {len(events)} events.")
                for ev in events:
                    print(f"- {ev['name']} ({ev['course']['fullname']})")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == '__main__':
    asyncio.run(test())
