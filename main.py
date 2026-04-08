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

    url = f"https://scriptblox.com/api/script/search?q={query}&max=1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                scripts = data.get('result', {}).get('scripts', [])
                
                if scripts:
                    s = scripts[0]
                    title = s.get('title', 'No Title')
                    game_name = s.get('game', {}).get('name', 'Unknown Game')
                    game_img = s.get('game', {}).get('imageUrl', '')
                    script_img = s.get('image', '')
                    is_verified = "✅ Verified" if s.get('verified') else "❌ Not Verified"
                    has_key = "🔑 Key Required" if s.get('key') else "🆓 No Key"
                    views = s.get('views', 0)
                    script_code = s.get('script', 'No script found')

                    embed = discord.Embed(
                        title=title,
                        description=f"**Game:** {game_name}\n**Status:** {is_verified} | {has_key}",
                        color=discord.Color.blue()
                    )

                    if script_img:
                        img_url = script_img if script_img.startswith('http') else f"https://scriptblox.com{script_img}"
                        embed.set_image(url=img_url)

                    if game_img:
                        thumb_url = game_img if game_img.startswith('http') else f"https://scriptblox.com{game_img}"
                        embed.set_thumbnail(url=thumb_url)

                    embed.add_field(name="Views", value=f"👁️ {views:,}", inline=True)
                    
                    # แก้ไขส่วนที่ Error โดยใช้ตัวแปรแยกออกมาให้ชัดเจน
                    short_code = script_code[:800] + "..." if len(script_code) > 800 else script_code
                    clean_code = f"```lua\n{short_code}\n```"
                    
                    embed.add_field(name="Script Content", value=clean_code, inline=False)
                    embed.set_footer(text=f"RETH OFFICIAL | ID: {s.get('_id')}")

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"🔍 ไม่พบสคริปต์สำหรับ: **{query}**")
            else:
                await interaction.followup.send("⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อ API")

bot.run(TOKEN)
