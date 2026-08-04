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
        
    async def setup_hook(self):
        # Sync the command tree with Discord
        await self.load_extension('module.danbooru')
        print("modules loaded successfully.")
        try:
            synced = await self.tree.sync()
            print(f"Đã đồng bộ {len(synced)} slash command(s) toàn cầu!")
        except Exception as e:
            print(f"Lỗi khi đồng bộ slash command: {e}")
    
    async def on_ready(self):
        print('------')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print(f'Danbooru Search Bot is ready and running!')

bot = Client()

@bot.event
async def on_guild_join(guild: discord.Guild):
    # Copy global commands to the new guild
    bot.tree.copy_global_to(guild=guild)

    # Sync slash commands for the new guild
    await bot.tree.sync(guild=guild)

    print(f"Đã auto-register slash commands cho guild mới: {guild.name}")
            
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

print(f"Đang chuẩn bị chạy bot với Token: {BOT_TOKEN}") # Thêm dòng này
bot.run(BOT_TOKEN)

