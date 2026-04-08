import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    keep_alive()

@bot.tree.command(name="search", description="ค้นหาสคริปต์จาก ScriptBlox")
@app_commands.describe(query="ชื่อเกมหรือสคริปต์")
async def search(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    # ดึงข้อมูลจาก API (เพิ่ม max=1 เพื่อเอาผลลัพธ์ที่ตรงที่สุดอันเดียว)
    url = f"https://scriptblox.com/api/script/search?q={query}&max=1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                scripts = data.get('result', {}).get('scripts', [])
                
                if scripts:
                    s = scripts[0] # ดึงสคริปต์ตัวแรก
                    
                    # เตรียมข้อมูลสำหรับ Embed
                    title = s.get('title', 'No Title')
                    game_name = s.get('game', {}).get('name', 'Unknown Game')
                    game_img = s.get('game', {}).get('imageUrl', '')
                    script_img = s.get('image', '')
                    is_verified = "✅ Verified" if s.get('verified') else "❌ Not Verified"
                    has_key = "🔑 Key Required" if s.get('key') else "🆓 No Key"
                    views = s.get('views', 0)
                    script_code = s.get('script', 'No script found')

                    # สร้าง Embed สวยๆ
                    embed = discord.Embed(
                        title=title,
                        description=f"**Game:** {game_name}\n**Status:** {is_verified} | {has_key}",
                        color=discord.Color.green() if s.get('verified') else discord.Color.blue()
                    )

                    # ใส่รูปภาพสคริปต์ (ถ้ามี)
                    if script_img:
                        # ถ้า URL รูปไม่มี https: นำหน้า ให้เติมให้มัน (บางครั้ง API ส่งมาแค่ /images/...)
                        if script_img.startswith('/'):
                            script_img = f"https://scriptblox.com{script_img}"
                        embed.set_image(url=script_img)

                    # ใส่รูปไอคอนเกมเล็กๆ (Thumbnail)
                    if game_img:
                        if game_img.startswith('/'):
                            game_img = f"https://scriptblox.com{game_img}"
                        embed.set_thumbnail(url=game_img)

                    embed.add_field(name="Views", value=f"👁️ {views:,}", inline=True)
                    embed.add_field(name="Type", value=s.get('scriptType', 'Unknown'), inline=True)
                    
                    # แสดงโค้ดสคริปต์ (จำกัดความยาวเพื่อไม่ให้ Embed พัง)
                    clean_code = f"
http://googleusercontent.com/immersive_entry_chip/0

---

### รายละเอียดที่เพิ่มเข้ามา:
* **`set_image`**: แสดงรูปภาพหน้าปกของสคริปต์ (ตัวใหญ่ตรงกลาง)
* **`set_thumbnail`**: แสดงรูปภาพของเกม (ตัวเล็กมุมขวาบน)
* **`verified` & `key`**: บอกให้ผู้ใช้รู้ว่าสคริปต์นี้ปลอดภัยไหม และต้องหา Key หรือเปล่า
* **`views`**: แสดงจำนวนคนดูสคริปต์นั้นๆ
* **Logic ตรวจสอบ URL**: ผมเพิ่มโค้ดเช็คว่าถ้า URL รูปภาพที่ API ส่งมาเป็นแบบย่อ (เช่น `/images/...`) บอทจะเติม `https://scriptblox.com` ให้โดยอัตโนมัติเพื่อให้รูปขึ้นโชว์ใน Discord ครับ

---

### วิธีอัปเดต:
1.  แก้ไฟล์ `main.py` ใน GitHub ตามโค้ดด้านบน
2.  รอ Render ทำการ Deploy (ประมาณ 1 นาที)
3.  ลองใช้คำสั่ง `/search` ใน Discord ได้เลยครับ!

ถ้าอยากให้เวลาคนกดปุ่มแล้ว "ก๊อปปี้สคริปต์" ได้เลย หรืออยากให้บอทส่งไฟล์สคริปต์แยกให้ บอกได้นะครับ!
