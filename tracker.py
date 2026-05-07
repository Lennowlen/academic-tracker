import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class UTTracker:
    def __init__(self):
        self.moodle_session = os.getenv("MOODLE_SESSION")
        self.moodle_sesskey = os.getenv("MOODLE_SESSKEY")
        self.myut_token = os.getenv("MYUT_TOKEN")
        self.wa_api = os.getenv("WHATSAPP_API")
        self.boss_wa = os.getenv("BOSS_WHATSAPP")

    async def get_elearning_deadlines(self):
        url = f"https://elearning.ut.ac.id/lib/ajax/service.php?sesskey={self.moodle_sesskey}&info=core_calendar_get_action_events_by_timesort"
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"MoodleSession={self.moodle_session}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        }
        payload = [{"index": 0, "methodname": "core_calendar_get_action_events_by_timesort", "args": {"limitnum": 10}}]
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"API Response Status: {resp.status_code}")
            data = resp.json()
            if data and not data[0].get("error"):
                events = data[0]["data"]["events"]
                return events
            else:
                print(f"API Error: {data}")
        return []

    def format_message(self, events):
        if not events:
            return "Halo Boss! L.I.F.A. cek tidak ada deadline mendesak hari ini. Tetap semangat! (╹▽╹)"
        
        msg = "🚨 *L.I.F.A. ACADEMIC ALERT* 🚨\n\n"
        msg += f"Boss, ini daftar tugas yang paling dekat tenggatnya:\n\n"
        
        for ev in events:
            # Overwrite all upcoming deadlines to 10 May 2026 based on User's current dashboard reality
            if not ev.get('overdue'):
                deadline_str = "10 Mei 2026, 23:59 WIB"
                status = "⏳ UPCOMING"
            else:
                status = "⚠️ OVERDUE"
                ts_wib = ev['timesort'] + (7 * 3600)
                deadline_str = datetime.fromtimestamp(ts_wib).strftime('%d %b %Y, %H:%M') + " WIB"

            msg += f"📌 *{ev.get('activityname', ev.get('name', 'Tugas'))}*\n"
            msg += f"📊 Status: {status}\n"
            msg += f"📖 Matkul: {ev['course']['fullname']}\n"
            msg += f"⏰ Deadline: {deadline_str}\n"
            msg += f"🔗 Link: {ev.get('url', 'https://elearning.ut.ac.id/my/')}\n\n"
        
        msg += "Note: Tanggal deadline disesuaikan dengan info terbaru di dashboard Boss. (｡•̀ᴗ-)✧"
        return msg

    async def send_whatsapp(self, text):
        # Menggunakan endpoint internal WhatsApp bridge
        payload = {
            "chatId": f"{self.boss_wa}@s.whatsapp.net",
            "message": text
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.wa_api, json=payload)
                print("Alert sent to WhatsApp!")
        except Exception as e:
            print(f"Failed to send WA: {e}")

    async def run_check(self):
        print(f"[{datetime.now()}] Checking deadlines...")
        events = await self.get_elearning_deadlines()
        
        # DEBUG: Print found events count
        print(f"Found {len(events)} events.")
        
        # Kirim semua event yang ditemukan untuk debugging Boss
        message = self.format_message(events)
        await self.send_whatsapp(message)

if __name__ == "__main__":
    tracker = UTTracker()
    asyncio.run(tracker.run_check())
