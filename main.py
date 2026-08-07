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
                print(f"Đã đồng bộ {len(synced)} lệnh Local cho server: {guild.name}")
            except Exception as e:
                print(f"Lỗi khi đồng bộ ở {guild.name}: {e}")

        # 2. XÓA bộ lệnh Global trên hệ thống Discord để tránh bị nhân đôi
        try:
            self.tree.clear_commands(guild=None) # Xóa lệnh global trong nội bộ tree
            await self.tree.sync()               # Push tree rỗng lên hệ thống -> Discord xóa lệnh thừa
            print("Đã dọn dẹp lệnh Global để hết bị trùng lặp!")
        except Exception as e:
            print(f"Lỗi khi dọn dẹp Global: {e}")

        print('------')

bot = Client()

@bot.event
async def on_guild_join(guild: discord.Guild):
    try:
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Đã đồng bộ {len(synced)} lệnh slash commands cho server mới: {guild.name}")
    except Exception as e:
        print(f"Lỗi khi đồng bộ ở {guild.name}: {e}")
            
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

