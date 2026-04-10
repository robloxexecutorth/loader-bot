import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# --- CONFIGURATION ---
load_dotenv()
TOKEN = os.getenv('ANTISPAM_TOKEN')

class LoaderBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # บังคับ Sync คำสั่ง Slash Command ใหม่ทุกครั้งที่รัน
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = LoaderBot()

# --- COMMANDS ---

@bot.tree.command(name="setup", description="Initialize the hub in your current channel")
async def setup(interaction: discord.Interaction):
    """
    แก้ปัญหา Did not respond โดยการจองคิวตอบกลับทันที
    และถอนการเช็คสิทธิ์ Admin ออกเพื่อให้รันได้ไม่เอ๋
    """
    # 1. บอก Discord ให้รอ (ป้องกัน Error ภายใน 3 วินาที)
    await interaction.response.defer(ephemeral=True)
    
    try:
        # 2. จำลองการโหลดข้อมูลระบบ RETH OFFICIAL
        await asyncio.sleep(1.5) 
        
        # 3. ส่งคำตอบกลับผ่าน Followup
        embed = discord.Embed(
            title="Forest Fire HUB V2",
            description="**Status:** ✅ System Ready\n**Project:** RETH OFFICIAL",
            color=0xff4500
        )
        embed.set_footer(text=f"Authorized for {interaction.user.name}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Error in setup: {e}")
        await interaction.followup.send("❌ เกิดข้อผิดพลาดในการตั้งค่าระบบ")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    # ใช้ defer สำหรับคำสั่งที่อาจจะช้าในบางช่วงของ Server
    await interaction.response.defer()
    latency = round(bot.latency * 1000)
    await interaction.followup.send(f"🏓 Pong! {latency}ms")

# --- EVENTS ---

@bot.event
async def on_ready():
    print("==========================")
    print(f"LOADER BOT ONLINE: {bot.user}")
    print("STATUS: NO-ERROR MODE")
    print("==========================")
    await bot.change_presence(activity=discord.Game(name="RETH OFFICIAL HUB"))

if __name__ == "__main__":
    # รันระบบ Keep Alive เพื่อให้บอทไม่ดับบน Render
    keep_alive() 
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("ERROR: ANTISPAM_TOKEN NOT FOUND")
