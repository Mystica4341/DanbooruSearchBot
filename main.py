import aiohttp
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands  
from discord import app_commands  

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # self.tree = app_commands.CommandTree(self)
        super().__init__(command_prefix='$', intents=intents)
        self.session: aiohttp.ClientSession = None
        
    async def setup_hook(self):
        # Create a single aiohttp session for the bot to use
        self.session = aiohttp.ClientSession()
        # Sync the command tree with Discord
        await self.load_extension('modules.danbooru')
        await self.load_extension('modules.nhentai')
        print("modules loaded successfully.")
    
    async def on_ready(self):
        print('------')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print(f'Danbooru Search Bot is ready and running!')
        print('------')

        # 1. Copy lệnh vào từng server (Local) để lệnh cập nhật ngay lập tức
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"Synced {len(synced)} local commands for server: {guild.name}")
            except Exception as e:
                print(f"Error syncing commands for {guild.name}: {e}")

        # 2. XÓA bộ lệnh Global trên hệ thống Discord để tránh bị nhân đôi
        try:
            self.tree.clear_commands(guild=None) # Xóa lệnh global trong nội bộ tree
            await self.tree.sync()               # Push tree rỗng lên hệ thống -> Discord xóa lệnh thừa
            print("Synced global commands and cleared duplicates!")
        except Exception as e:
            print(f"Error clearing global commands: {e}")

        print('------')

    async def close(self):
        # Đóng session an toàn khi bot tắt
        if self.session:
            await self.session.close()
        await super().close()

bot = Client()

@bot.event
async def on_guild_join(guild: discord.Guild):
    try:
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands for new server: {guild.name}")
    except Exception as e:
        print(f"Error syncing commands for {guild.name}: {e}")

@bot.command()
async def ping(ctx: commands.Context):
    """Responds with 'Pong!' when the command is invoked."""
    latency = bot.latency
    await ctx.channel.send(f"Pong! **`{latency:.2f}ms`**")

@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    """Responds with 'Pong!' and the bot's latency."""
    latency = bot.latency
    await interaction.response.send_message(f"Pong! **`{latency:.2f}ms`**")

print(f"Preparing to run bot with Token: {BOT_TOKEN}")
bot.run(BOT_TOKEN)

