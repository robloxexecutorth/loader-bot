import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from keep_alive import keep_alive  # นำเข้าฟังก์ชันจาก keep_alive.py

# โหลดค่า Token จากไฟล์ .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # อนุญาตให้บอทอ่านข้อความ (ถ้าจำเป็น)
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)
        self.setup_channels = {} # เก็บ ID ห้องที่เลือกไว้

    async def setup_hook(self):
        # Sync slash commands กับ Discord
        await self.tree.sync()
        print(f"✅ บอท {self.user} พร้อมทำงานและซิงค์คำสั่งแล้ว!")

bot = MyBot()

# --- UI ส่วน Modal สำหรับกรอกชื่อเกม ---
class ScriptModal(discord.ui.Modal, title="ค้นหาสคริปต์จาก ScriptBlox"):
    game_input = discord.ui.TextInput(
        label="ชื่อเกมที่ต้องการ",
        placeholder="เช่น Blox Fruits, King Legacy...",
        min_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        search_query = self.game_input.value
        url = f"https://scriptblox.com/api/script/search?q={search_query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    scripts = data.get("result", {}).get("scripts", [])
                    
                    if not scripts:
                        return await interaction.followup.send(f"❌ ไม่พบสคริปต์สำหรับเกม: **{search_query}**")

                    # ดึงสคริปต์ 3 ตัวแรกมาแสดง (เพื่อไม่ให้ Embed ยาวเกินไป)
                    for script in scripts[:3]:
                        embed = discord.Embed(
                            title=script.get("title", "ไม่มีชื่อ"),
                            url=f"https://scriptblox.com/script/{script.get('slug')}",
                            color=discord.Color.blue()
                        )
                        
                        # ข้อมูลจาก JSON
                        game_data = script.get("game", {})
                        is_verified = "✅ ใช่" if script.get("verified") else "❌ ไม่"
                        has_key = "🔑 ต้องใช้ Key" if script.get("key") else "🔓 ไม่ใช้ Key"
                        is_patched = "⚠️ ใช้งานไม่ได้ (Patched)" if script.get("isPatched") else "✅ ใช้งานได้"
                        
                        embed.add_field(name="ชื่อเกม", value=game_data.get("name", "ไม่ระบุ"), inline=True)
                        embed.add_field(name="ประเภท", value=script.get("scriptType", "N/A"), inline=True)
                        embed.add_field(name="ยอดเข้าชม", value=f"{script.get('views', 0):,}", inline=True)
                        embed.add_field(name="สถานะ", value=f"Verified: {is_verified}\nStatus: {is_patched}", inline=True)
                        embed.add_field(name="ระบบ Key", value=has_key, inline=True)
                        embed.add_field(name="Universal", value="ใช่" if script.get("isUniversal") else "ไม่ใช่", inline=True)
                        
                        # ส่วนของเนื้อหาสคริปต์
                        content = script.get("script", "")
                        if len(content) > 1000:
                            content = content[:997] + "..."
                        embed.add_field(name="Script (ย่อ)", value=f"```lua\n{content}\n```", inline=False)
                        
                        # รูปภาพประกอบ
                        img = script.get("image")
                        if img:
                            full_img_url = f"https://scriptblox.com{img}" if img.startswith("/") else img
                            embed.set_image(url=full_img_url)

                        embed.set_footer(text=f"อัปเดตเมื่อ: {script.get('updatedAt')[:10]}")
                        await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("⚠️ ติดต่อ API ไม่สำเร็จ กรุณาลองใหม่ภายหลัง")

# --- UI ส่วนปุ่มกดหน้าแรก ---
class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # ปุ่มอยู่ถาวร

    @discord.ui.button(label="Get Script", style=discord.ButtonStyle.primary, emoji="🔥")
    async def get_script(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ตรวจสอบว่าใช้งานถูกห้องไหม
        target_channel_id = bot.setup_channels.get(interaction.guild_id)
        if target_channel_id and interaction.channel_id != target_channel_id:
            return await interaction.response.send_message(f"❌ กรุณาใช้ในห้องที่ตั้งค่าไว้เท่านั้น!", ephemeral=True)
        
        await interaction.response.send_modal(ScriptModal())

# --- Slash Command ---
@bot.tree.command(name="setup", description="ตั้งค่าห้องสำหรับรันระบบบอทสคริปต์")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    bot.setup_channels[interaction.guild_id] = interaction.channel_id
    
    embed = discord.Embed(
        title="🌟 ScriptBlox Bot System",
        description="ยินดีต้อนรับสู่ระบบค้นหาสคริปต์! กดปุ่มด้านล่างเพื่อเริ่มค้นหา",
        color=discord.Color.green()
    )
    embed.set_footer(text="ระบบตั้งค่าให้ใช้งานเฉพาะห้องนี้แล้ว")
    
    await interaction.response.send_message("✅ ตั้งค่าสำเร็จ!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=MainView())

# รันระบบ Keep Alive (สำหรับ Replit/Uptime)
keep_alive()

# เริ่มการทำงานของบอท
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ไม่พบ DISCORD_TOKEN ในไฟล์ .env หรือระบบ Secrets")
