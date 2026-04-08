import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import aiohttp
from dotenv import load_dotenv
from keep_alive import keep_alive

# โหลด Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- 1. หน้าต่างกรอกชื่อ (Modal) ---
class ScriptSearchModal(ui.Modal, title='RETH OFFICIAL - Get Script'):
    map_name = ui.TextInput(
        label='ชื่อแมพหรือสคริปต์ที่ต้องการ',
        placeholder='เช่น Blox Fruits, King Legacy...',
        min_length=2,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        query = self.map_name.value
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
                        script_code = s.get('script', 'No script found')
                        
                        embed = discord.Embed(title=f"🚀 พบสคริปต์: {title}", color=discord.Color.green())
                        embed.add_field(name="Game", value=game_name, inline=True)
                        
                        # ตัดโค้ดถ้ามันยาวเกินไปเพื่อไม่ให้ Embed พัง
                        short_code = script_code[:800] + "..." if len(script_code) > 800 else script_code
                        embed.add_field(name="Script", value=f"```lua\n{short_code}\n```", inline=False)
                        embed.set_footer(text="RETH OFFICIAL - ผลการค้นหา")
                        
                        await interaction.followup.send(embed=embed, ephemeral=True)
                    else:
                        await interaction.followup.send(f"❌ ไม่พบสคริปต์สำหรับ: {query}", ephemeral=True)
                else:
                    await interaction.followup.send("⚠️ API ScriptBlox มีปัญหา กรุณาลองใหม่", ephemeral=True)

# --- 2. ปุ่มกด (View) ---
class GetScriptView(ui.View):
    def __init__(self):
        super().__init__(timeout=None) # เพื่อให้ปุ่มทำงานตลอดเวลา

    @ui.button(label='Get Script', style=discord.ButtonStyle.primary, custom_id='get_script_btn', emoji='🔍')
    async def get_script(self, interaction: discord.Interaction):
        # เมื่อกดปุ่ม ให้ส่ง Modal (หน้าต่างกรอกข้อความ) ไปให้
        await interaction.response.send_modal(ScriptSearchModal())

# --- 3. ตัวบอทหลัก ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # ลงทะเบียน View ให้บอทจำปุ่มได้แม้จะรีสตาร์ท
        self.add_view(GetScriptView())
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    keep_alive()

# คำสั่ง /setup
@bot.tree.command(name="setup", description="ติดตั้งปุ่มค้นหาสคริปต์ในช่องนี้")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ RETH OFFICIAL LOADER",
        description="ยินดีต้อนรับสู่ระบบค้นหาสคริปต์\nคลิกปุ่มด้านล่างเพื่อเริ่มใช้งาน",
        color=discord.Color.blue()
    )
    # ส่ง Embed พร้อมกับ View (ที่มีปุ่ม)
    await interaction.response.send_message("ติดตั้งระบบเรียบร้อย!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=GetScriptView())

bot.run(TOKEN)
