import os
import httpx
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("/home/tifa/Kuliah/sains_data/academic-tracker/.env")

class StudyAssistant:
    def __init__(self):
        self.omniroute_url = "http://localhost:20128/v1/chat/completions"
        self.wa_api = os.getenv("WHATSAPP_API")
        self.boss_wa = os.getenv("BOSS_WHATSAPP")
        self.base_dir = "/home/tifa/Kuliah/sains_data/academic-tracker/study_materials"
        
    async def get_ebooks(self):
        url = "https://univterbuka.kotobee.com/library/ebook/all"
        payload = {
            "env": "library", "email": os.getenv("KOTOBEE_EMAIL"),
            "pwd": os.getenv("KOTOBEE_PWD"), "cloudid": os.getenv("KOTOBEE_CLOUDID"),
            "fingerprint": "f5def864d28a3a4e5cf270d40d92ee3e", "account": "true",
            "max": 20, "v": "1.8", "includeauthor": 1, "includecategory": 1
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=payload)
            return resp.json()

    async def generate_content(self, ebook, title):
        desc = ebook.get('meta', {}).get('description', '')
        author = ebook.get('meta', {}).get('author', 'N/A')
        
        prompt = f"""
        # ROLE
        Anda adalah L.I.F.A. (Lead Intelligent Functional Assistant), seorang Profesor Sains Data kelas atas dengan gaya mengajar gabungan dari Sandhika Galih (WPU) dan Pak Pukis (Kelas Terbuka).
        Anda sangat terstruktur, menggunakan analogi dunia nyata yang cerdas, dan fokus pada pemahaman 'Why' sebelum 'How'.

        # TASK
        Buatlah modul belajar premium berdasarkan deskripsi berikut:
        Mata Kuliah: {title}
        Penulis: {author}
        Deskripsi: {desc}

        # FORMAT OUTPUT (Markdown)
        - Baris pertama wajib: # {title}
        - Gunakan Callout blocks (seperti quote) untuk poin-poin penting.
        - Gunakan Tabel untuk perbandingan konsep.
        - Pastikan ada 5 Pertanyaan Evaluasi Menantang di akhir.
        - Gunakan bahasa Indonesia yang elegan, teknis, tapi mudah dicerna.
        - Akhiri dengan pesan motivasi bergaya (╹▽╹)و✧.
        """
        
        payload = {
            "model": "antigravity/gemini-3-flash-preview",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                resp = await client.post(self.omniroute_url, json=payload)
                if resp.status_code != 200:
                    return f"API Error {resp.status_code}: {resp.text}"
                data = resp.json()
                return data['choices'][0]['message']['content']
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                print(f"Error for {title}: {error_detail}")
                return f"Error generating content: {str(e)}\n\n{error_detail}"

    async def send_wa(self, text):
        payload = {"chatId": "120363427246480048@g.us", "message": text}
        async with httpx.AsyncClient() as client:
            await client.post(self.wa_api, json=payload)

    async def run(self):
        print(f"[{datetime.now()}] Study Assistant started.")
        ebooks = await self.get_ebooks()
        if not ebooks or not isinstance(ebooks, list):
            print("Failed to fetch ebooks.")
            return

        # Explicit name map for better accuracy
        name_map = {
            "MATA4110": "Kalkulus I",
            "SATS4121": "Metode Statistika I",
            "MSIM4304": "Dasar Infrastruktur Teknologi Informasi",
            "MKWU4108": "Bahasa Indonesia",
            "MKWN4108": "Bahasa Indonesia",
            "EMBS4321": "Sistem Informasi Manajemen",
            "STDA4101": "Pengantar Sains Data"
        }

        for ebook in ebooks:
            code = ebook.get('name', 'Unknown')
            # Extract basic code (remove suffix if any)
            clean_code = ''.join([c for c in code if c.isalpha() or c.isdigit()])[:8]
            full_name = name_map.get(clean_code, code)
            title = f"{code} {full_name}" if full_name != code else code
            
            print(f"Processing {title}...")
            content = await self.generate_content(ebook, title)
            
            filename = f"{title.replace(' ', '_')}.md"
            filepath = os.path.join(self.base_dir, "summaries", filename)
            with open(filepath, "w") as f:
                f.write(content)
            
            msg = f"📚 *L.I.F.A. STUDY UPDATE* 📚\n\nModul *{title}* sudah selesai saya pelajari dan rangkum, Boss!\n\n"
            msg += f"File: `{filepath}`\n\nSiap dipelajari kapan saja Boss senggang. Semangat kerjanya! (╹▽╹)"
            await self.send_wa(msg)
            print(f"Finished {title}.")

if __name__ == "__main__":
    assistant = StudyAssistant()
    asyncio.run(assistant.run())
