import discord
import os
from discord.ext import commands
from discord import app_commands
from utils import send_error
import aiohttp

class ViewImage(discord.ui.View):
    def __init__(self, posts, tags):
        super().__init__(timeout=180) # Giao diện sẽ hết hạn sau 3 phút không ai bấm
        self.posts = posts
        self.tags = tags
        self.current_index = 0
        self.update_buttons()
        
    # Hàm tạo khung Embed hiển thị ảnh hiện tại
    def create_embed(self):
      try:
        post = self.posts[self.current_index]
        image_url = post.get('file_url')
        post_id = post.get('id')
        author = post.get('tag_string_artist', 'Unknown Artist')
        character = post.get('tag_string_character', 'Unknown Character')
        
        # Tiêu đề hiển thị số trang (vd: 1/10)
        embed = discord.Embed(
            title=f"Kết quả cho: {self.tags} ({self.current_index + 1}/{len(self.posts)})", 
            color=discord.Color.blue()
        )

        embed.set_image(url=image_url)
        embed.add_field(name="Artist", value=author, inline=True)
        embed.add_field(name="Character", value=character, inline=True)
        embed.description = f"[Xem bài gốc trên Danbooru](https://danbooru.donmai.us/posts/{post_id})"
        return embed
      
      except Exception as e:
          return discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())

    # Button disabled if at the first or last post
    def update_buttons(self):
        self.prev_button.disabled = (self.current_index == 0)
        self.next_button.disabled = (self.current_index == len(self.posts) - 1)

    # Implement "Prev" button
    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.primary, custom_id="prev_btn")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_index -= 1
        self.update_buttons()
        # Edit old message with new image
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    # Implement "Next" button
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary, custom_id="next_btn")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_index += 1
        self.update_buttons()
        # Edit old message with new image
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

class DanbooruModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('DANBOORU_API_KEY')
        self.api_login = os.getenv('DANBOORU_USERNAME')

    @app_commands.command(name='tag_search', description='Searches Danbooru for tags based on the provided query.')
    @app_commands.describe(query='The tag query to search for', limit='Number of results to return (max 100)', category='general, artist, character, copyright')
    async def tag_search(self, interaction: discord.Interaction, query: str, limit: int, category: str):
        """Searches Danbooru for tags based on the provided query."""
        await interaction.response.defer()

        if category not in ['general', 'artist', 'character', 'copyright']:
            await interaction.followup.send("Invalid category. Please choose from 'general', 'artist', 'character', or 'copyright'.")
            return

        if category == 'general':
            category_value = 0
        elif category == 'artist':
            category_value = 1
        elif category == 'character':
            category_value = 3
        elif category == 'copyright':
            category_value = 4

        params = {
            'search[tag]': query,
            'limit': limit,
            'search[category]': category_value  # You can change this to 'artist', 'character', etc. if needed
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'MyDiscordBot/1.0 (by Mirera on Discord)'
                }
                
                async with session.get("https://danbooru.donmai.us/tags.json", params=params, headers=headers) as response:
                    
                    if response.status == 200:
                        data = await response.json()

                        if len(data) > 0:
                            tag_list = [tag['name'] for tag in data]
                            embed = discord.Embed(
                                title=f"Found {len(tag_list)} tags for query: '{query}'",
                                description=', '.join(tag_list),
                                color=discord.Color.green()
                            )
                            await interaction.followup.send(embed=embed)
                        else:
                            await interaction.followup.send("No tags found for the given query.")

                    else:
                        await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

            except Exception as e:
                await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")
    
    @app_commands.command(name='danbooru', description='Searches Danbooru for images based on the provided tags.')
    @app_commands.describe(tags='The tags to search for', limit='Number of results to return (max 100)')
    async def danbooru_search(self, interaction: discord.Interaction, tags: str, limit: int):
        """Searches Danbooru for images based on the provided tags."""

        await interaction.response.defer()

        params = {
            'tags': tags,
            'limit': limit | 10,
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        # check if the channel is NSFW and if the tags contain NSFW content
        if not interaction.channel.is_nsfw():
            if 'rating:e' in tags or 'rating:q' in tags:
                # If the channel is not NSFW and the user is trying to search for NSFW content, send a warning message and return
                await interaction.followup.send("NSFW content is not allowed in this channel.")
                return 
            
            # Automatically add 'rating:safe' if the channel is not NSFW and the user hasn't specified a rating
            if 'rating:' not in tags:
                params['tags'] += ' rating:safe'

        # check if the number of tags exceeds 2 (for free accounts)
        # Tách chuỗi tags thành danh sách để đếm (dựa theo khoảng trắng)
        tag_list = params['tags'].split()
        if len(tag_list) > 2:
            await interaction.followup.send(
                f"⚠️ **Limit:** Free Account only allows up to 2 tags/search. "
                f"You are searching for {len(tag_list)} tags (including the automatic `rating:safe` tag added to non-NSFW channels). "
                f"Please reduce the number of tags."
            )
            return

        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'MyDiscordBot/1.0 (by Mirera on Discord)'
                }
                
                async with session.get("https://danbooru.donmai.us/posts.json", params=params, headers=headers) as response:
                    
                    if response.status == 200:
                        data = await response.json()

                        # Filter out posts that don't have a valid file_url (exclude posts that are deleted or have no image or premium content)
                        valid_posts = [post for post in data if post.get('file_url') is not None]

                        if len(valid_posts) > 0:
                            view = ViewImage(valid_posts, tags)
                            await interaction.followup.send(embed=view.create_embed(), view=view)

                        else:
                            await interaction.followup.send("No results found for the given tags.")

                    else:
                        await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

            except Exception as e:
                await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")

async def setup(bot):
    await bot.add_cog(DanbooruModule(bot))