import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# --- [1] การตั้งค่า ---
load_dotenv()
TOKEN = os.getenv('MTQ0OTA5MTkwMjQwOTI4MTU0Ng.GwoCFw.o2vbeKERr_OJ71wwe6Wyv4JejOtZpg8UdGG5a0
')
WEB_LINK = "https://yourwebsite.com" 

setup_channels = set()

# --- [2] ระบบเลื่อนหน้า (Paginator) ---
class ScriptPaginator(ui.View):
    def __init__(self, scripts, query):
        super().__init__(timeout=300)
        self.scripts = scripts
        self.query = query
        self.current_page = 0
        self.add_item(ui.Button(label="View Web", url=WEB_LINK, style=discord.ButtonStyle.link))

    async def create_embed(self):
        s = self.scripts[self.current_page]
        title = s.get('title', 'No Title')
        game_name = s.get('game', {}).get('name', 'Unknown Game')
        
        embed = discord.Embed(title=title, description=f"**Game:** {game_name}", color=discord.Color.blue())
        stats = (f"**Verified:** {'✅ Yes' if s.get('verified') else '❌ No'}\n"
                 f"**Key:** {'🔑 Required' if s.get('key') else '🆓 No Key'}\n"
                 f"**Views:** {s.get('views', 0):,}\n"
                 f"**👍 Likes:** {s.get('likeCount', 0):,} | **👎 Dislikes:** {s.get('dislikeCount', 0):,}")
        embed.add_field(name="📊 Status & Stats", value=stats, inline=False)

        script_code = s.get('script', 'No script found')
        short_code = script_code[:800] + "..." if len(script_code) > 800 else script_code
        embed.add_field(name="📜 Script Content", value=f"```lua\n{short_code}\n```", inline=False)

        img = s.get('image', '')
        if img: embed.set_image(url=img if img.startswith('http') else f"https://scriptblox.com{img}")
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.scripts)} | RETH OFFICIAL")
        return embed

    @ui.button(label='Back', style=discord.ButtonStyle.gray, emoji='⬅️')
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=await self.create_embed(), view=self)

    @ui.button(label='Next', style=discord.ButtonStyle.gray, emoji='➡️')
    async def next_button(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page < len(self.scripts) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=await self.create_embed(), view=self)

# --- [3] ระบบค้นหา ---
async def search_logic(query, target):
    url = f"https://scriptblox.com/api/script/search?q={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                scripts = data.get('result', {}).get('scripts', [])
                if scripts:
                    view = ScriptPaginator(scripts, query)
                    embed = await view.create_embed()
                    # ตรวจสอบว่าเป็น Interaction หรือ Message
                    if isinstance(target, discord.Interaction):
                        msg = await target.followup.send(embed=embed, view=view)
                    else:
                        msg = await target.send(embed=embed, view=view)
                    
                    await asyncio.sleep(300)
                    try: await msg.delete()
                    except: pass
                else:
                    msg = "❌ No scripts found."
                    if isinstance(target, discord.Interaction): await target.followup.send(msg)
                    else: await target.send(msg, delete_after=10)

class ScriptSearchModal(ui.Modal, title='RETH OFFICIAL - Search'):
    map_name = ui.TextInput(label='Game Name', placeholder='Enter here...', min_length=2)
    async def on_submit(self, interaction: discord.Interaction):
        # แก้ Did not respond โดยการ Defer ก่อน [image_503067.jpg]
        await interaction.response.defer()
        await search_logic(self.map_name.value, interaction)

class GetScriptView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="View Web", url=WEB_LINK, style=discord.ButtonStyle.link))
    @ui.button(label='Get Script', style=discord.ButtonStyle.primary, custom_id='gs_btn', emoji='🔍')
    async def get_script(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ScriptSearchModal())

# --- [4] โครงสร้างบอท ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(GetScriptView())
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ Online: {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id not in setup_channels: return
    try: await message.delete()
    except: pass
    await search_logic(message.content, message.channel)

# --- [5] คำสั่งแก้ไข Error ---

@bot.tree.command(name="setup")
async def setup(interaction: discord.Interaction):
    # นำสิทธิ์แอดมินออกชั่วคราวเพื่อแก้ MissingPermissions [image_503848.jpg]
    await interaction.response.defer(ephemeral=True)
    setup_channels.add(interaction.channel.id)
    embed = discord.Embed(title="🛡️ RETH OFFICIAL LOADER", description="System Active!", color=discord.Color.green())
    await interaction.followup.send("Setup Done!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=GetScriptView())

if __name__ == "__main__":
    keep_alive() # ใช้คู่กับ keep_alive.py
    if TOKEN:
        bot.run(TOKEN)
