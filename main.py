import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Storage for active search channels
setup_channels = set()

# --- 1. Pagination & Result View ---
class ScriptPaginator(ui.View):
    def __init__(self, scripts, query):
        super().__init__(timeout=300)
        self.scripts = scripts
        self.query = query
        self.current_page = 0

    async def create_embed(self):
        s = self.scripts[self.current_page]
        title = s.get('title', 'No Title')
        game_name = s.get('game', {}).get('name', 'Unknown Game')
        
        # Statistics
        verified = "✅ Yes" if s.get('verified') else "❌ No"
        has_key = "🔑 Required" if s.get('key') else "🆓 No Key"
        views = s.get('views', 0)
        likes = s.get('likeCount', 0)
        dislikes = s.get('dislikeCount', 0)
        created = s.get('createdAt', '')[:10]
        updated = s.get('updatedAt', '')[:10]

        embed = discord.Embed(
            title=title,
            description=f"**Game:** {game_name}",
            color=discord.Color.blue()
        )

        status_text = (
            f"**Verified:** {verified}\n"
            f"**Key:** {has_key}\n"
            f"**Views:** {views:,}\n"
            f"**👍 Likes:** {likes:,} | **👎 Dislikes:** {dislikes:,}\n"
            f"**📅 Created:** {created} | **🔄 Updated:** {updated}"
        )
        embed.add_field(name="📊 Status & Stats", value=status_text, inline=False)

        # Script Content
        script_code = s.get('script', 'No script found')
        short_code = script_code[:800] + "..." if len(script_code) > 800 else script_code
        embed.add_field(name="📜 Script Content", value=f"```lua\n{short_code}\n```", inline=False)

        # Images
        script_img = s.get('image', '')
        if script_img:
            img_url = script_img if script_img.startswith('http') else f"https://scriptblox.com{script_img}"
            embed.set_image(url=img_url)

        game_img = s.get('game', {}).get('imageUrl', '')
        if game_img:
            thumb_url = game_img if game_img.startswith('http') else f"https://scriptblox.com{game_img}"
            embed.set_thumbnail(url=thumb_url)

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

# --- 2. Logic & UI Components ---
async def search_script_logic(query, channel_or_interaction):
    url = f"https://scriptblox.com/api/script/search?q={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                scripts = data.get('result', {}).get('scripts', [])
                
                if scripts:
                    view = ScriptPaginator(scripts, query)
                    # ADDING VIEW WEB BUTTON (Edit URL below)
                    view.add_item(ui.Button(label="View Web", url="https://robloxexecutorth.github.io/SCRETH/", style=discord.ButtonStyle.link))
                    
                    embed = await view.create_embed()
                    
                    if isinstance(channel_or_interaction, discord.Interaction):
                        msg = await channel_or_interaction.followup.send(embed=embed, view=view)
                    else:
                        msg = await channel_or_interaction.send(embed=embed, view=view)
                    
                    await asyncio.sleep(300)
                    try: await msg.delete()
                    except: pass
                else:
                    target = channel_or_interaction.followup if isinstance(channel_or_interaction, discord.Interaction) else channel_or_interaction
                    await target.send(f"❌ No scripts found for: **{query}**", delete_after=10)

class ScriptSearchModal(ui.Modal, title='RETH OFFICIAL - Search'):
    map_name = ui.TextInput(label='Game Name', placeholder='Type here...', min_length=2)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await search_script_logic(self.map_name.value, interaction)

class GetScriptView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label='Get Script', style=discord.ButtonStyle.primary, custom_id='get_script_btn', emoji='🔍')
    async def get_script(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ScriptSearchModal())

# --- 3. Main Bot Setup ---
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
    print(f'Logged in as {bot.user}')
    keep_alive()

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.channel.id in setup_channels:
        try: await message.delete()
        except: pass
        await search_script_logic(message.content, message.channel)
    await bot.process_commands(message)

# --- 4. Slash Commands ---
@bot.tree.command(name="setup", description="Activate the search system in this channel")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    setup_channels.add(interaction.channel.id)
    embed = discord.Embed(
        title="🛡️ RETH OFFICIAL LOADER",
        description="**System Status: ACTIVE**\n\n• Use the **Get Script** button\n• Or **Type the game name** directly here.",
        color=discord.Color.green()
    )
    # Adding Link Button to Setup Message too
    view = GetScriptView()
    view.add_item(ui.Button(label="View Web", url="https://robloxexecutorth.github.io/SCRETH/", style=discord.ButtonStyle.link))
    
    await interaction.response.send_message("System installed successfully!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

@bot.tree.command(name="unset", description="Disable and clear the search system in this channel")
@app_commands.checks.has_permissions(administrator=True)
async def unset(interaction: discord.Interaction):
    if interaction.channel.id in setup_channels:
        setup_channels.remove(interaction.channel.id)
        await interaction.response.send_message("❌ **System Disabled.** This channel will no longer process searches.", ephemeral=True)
    else:
        await interaction.response.send_message("This channel is not currently set up.", ephemeral=True)

@bot.tree.command(name="getscript", description="Quick search for a script")
async def getscript(interaction: discord.Interaction, query: str):
    await interaction.response.defer(ephemeral=False)
    await search_script_logic(query, interaction)

bot.run(TOKEN)
