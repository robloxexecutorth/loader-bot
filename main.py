import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # นำเข้าระบบเปิดเว็บเซิร์ฟเวอร์เล็กๆ

# โหลดค่าจากไฟล์ .env (ถ้ามี)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# ตั้งค่า Prefix และ Intents (สิทธิ์การเข้าถึงข้อมูล)
intents = discord.Intents.default()
intents.message_content = True  # จำเป็นต้องเปิดเพื่อให้บอทอ่านข้อความได้
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def hello(ctx):
    await ctx.send('สวัสดีครับ! ผมออนไลน์ 24 ชม. แล้วนะ')

# เรียกใช้ฟังก์ชันรักษาชีวิตบอท
keep_alive()

# รันบอท
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: ไม่พบ DISCORD_TOKEN ใน Environment Variables")
