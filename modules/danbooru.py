import discord
import os
from discord.ext import commands
from discord import app_commands
from helpers.danbooru_embed import ImageEmbed, TextEmbed, VideoEmbed
import aiohttp
from typing import Optional
from cachetools import TTLCache

class DanbooruModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = TTLCache(maxsize=100, ttl=900)
        self.session = bot.session  # Use the shared aiohttp session from the bot
        self.api_key = os.getenv('DANBOORU_API_KEY')
        self.api_login = os.getenv('DANBOORU_USERNAME')

    danbooru_modules = app_commands.Group(name='danbooru', description='Danbooru search commands')

    @danbooru_modules.command(name='tag_search', description='Searches tags on Danbooru based on the provided query.')
    @app_commands.describe(query='The tag query to search for', limit='Number of results to return (max 100)', category='input of these: general[0], artist[1], copyright[3], character[4]')
    async def tag_search(self, interaction: discord.Interaction, query: str, category: str, limit: Optional[int] = 10):
        """Searches tags on Danbooru based on the provided query and category."""
        await interaction.response.defer()

        category_mapping = {
            'general': 0,
            'artist': 1,
            'copyright': 3,
            'character': 4,
            'meta': 5
        }

        # check if user input is a number, if so, use it directly; otherwise, map the string to its corresponding number
        if category.isdigit():
            category_value = int(category)
        else:
            category_lower = category.lower() # Convert to lowercase for case-insensitive matching
            if category_lower in category_mapping:
                category_value = category_mapping[category_lower]
            else:
                # return an error message if the category is invalid
                await interaction.followup.send("Invalid category. Please input a valid ID (0, 1, 3, 4) or choose from 'general', 'artist', 'copyright', 'character'")
                return

        params = {
            'search[name_matches]': f'*{query}*',
            'limit': limit or 10,
            'search[category]': category_value  # You can change this to 'artist', 'character', etc. if needed
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        session = self.bot.session
        try:
            headers = {
                'User-Agent': 'MyDiscordBot/1.0 (by Mirera on Discord)'
            }
            
            async with session.get("https://danbooru.donmai.us/tags.json", params=params, headers=headers) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Fetched {len(data)} tags from Danbooru for query '{query}' in category '{category_value}'.")

                    if len(data) > 0:
                        tag_list = [tag['name'] for tag in data]
                        view = TextEmbed(tag_list, query)
                        await interaction.followup.send(embed=view.create_embed(), view=view)
                    else:
                        await interaction.followup.send("No tags found for the given query.")

                else:
                    await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")
    
    @danbooru_modules.command(name='search', description='Searches images on Danbooru based on the provided tags.')
    @app_commands.describe(tags='The tags to search for', limit='Number of results to return (max 100)')
    async def danbooru_search(self, interaction: discord.Interaction, tags: str, limit: Optional[int] = 10):
        """Searches images on Danbooru based on the provided tags."""

        await interaction.response.defer()

        exact_tag = await auto_resolve_tag(tags, self.session)
        if not exact_tag:
            await interaction.followup.send(f"❌ No results found for the given tags. `{tags}` on Danbooru.")
            return

        print(f"Resolved user input '{tags}' to exact tag '{exact_tag}' for Danbooru search.")
        exact_tag = await NSFW_check(interaction, exact_tag)  # Check if the channel is NSFW and adjust tags accordingly
        if exact_tag is None:
            return  # Exit if the channel is not NSFW and the user tried to search for NSFW content

        # Caching the resolved tag to avoid repeated API calls for the same query within a short time frame
        cache_key = f"danbooru_search_{exact_tag}_{limit}"
        await caching_images(interaction, self.cache, cache_key, exact_tag)

        params = {
            'tags': exact_tag,
            'limit': limit or 10,
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        session = self.bot.session
        try:
            headers = {
                'User-Agent': 'MyDiscordBot/1.0 (by Mirera on Discord)'
            }
            
            async with session.get("https://danbooru.donmai.us/posts.json", params=params, headers=headers) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Fetched {len(data)} posts from Danbooru for tags '{tags}' with limit {limit}.")
                    # Filter out posts that don't have a valid file_url (exclude posts that are deleted or have no image or premium content)
                    valid_posts = [post for post in data if post.get('file_url') is not None]

                    self.cache[cache_key] = valid_posts  # Cache the results for future requests

                    if len(valid_posts) > 0:
                        view = ImageEmbed(valid_posts, tags)
                        await interaction.followup.send(embed=view.create_embed(), view=view)

                    else:
                        await interaction.followup.send("No results found for the given tags.")

                else:
                    await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")

    @danbooru_modules.command(name='random', description='Give a list of random images from Danbooru based on the provided tags.')
    @app_commands.describe(tags='The tags to limit the pool', limit='Number of results to return (max 100)')
    async def random(self, interaction: discord.Interaction, tags: Optional[str] = '', limit: Optional[int] = 10):
        """Gives a list of random images from Danbooru based on the provided tags."""
        
        await interaction.response.defer()

        exact_tag = await auto_resolve_tag(tags, self.session)
        if not exact_tag:
            await interaction.followup.send(f"❌ No results found for the given tags. `{tags}` on Danbooru.")
            return

        print(f"Resolved user input '{tags}' to exact tag '{exact_tag}' for Danbooru search.")
        exact_tag = await NSFW_check(interaction, exact_tag)  # Check if the channel is NSFW and adjust tags accordingly
        if exact_tag is None:
            return  # Exit if the channel is not NSFW and the user tried to search for NSFW content
        
        params = {
            'tags': exact_tag,
            'limit': limit or 10,
            'random': 'true'
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        session = self.bot.session
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
                        view = ImageEmbed(valid_posts, "Random")
                        await interaction.followup.send(embed=view.create_embed(), view=view)

                    else:
                        await interaction.followup.send("No results found for random images.")

                else:
                    await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")

    @danbooru_modules.command(name='random_nsfw', description='Gives a list of random NSFW images from Danbooru')
    @app_commands.describe(limit='Number of results to return (max 100)')
    async def random_nsfw(self, interaction: discord.Interaction, limit: Optional[int] = 10):
        """Gives a list of random NSFW images from Danbooru"""

        await interaction.response.defer()

        tags = await NSFW_check(interaction, 'rating:e')
        if tags is None:
            return  # Exit if the channel is not NSFW and the user tried to search for NSFW content

        params = {
            'tags': 'rating:e',  # Explicit ratings
            'limit': limit or 10,
            'random': 'true'
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        session = self.bot.session
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
                        view = ImageEmbed(valid_posts, "Random NSFW")
                        await interaction.followup.send(embed=view.create_embed(), view=view)

                    else:
                        await interaction.followup.send("No results found for random NSFW images.")

                else:
                    await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")

    @danbooru_modules.command(name='video', description='Searches Danbooru for videos based on the provided query.')
    @app_commands.describe(tags='The tags to search for', limit='Number of results to return (max 100)')
    async def video(self, interaction: discord.Interaction, tags: str, limit: Optional[int] = 10):
        """Searches Danbooru for videos based on the provided tags."""

        await interaction.response.defer()

        exact_tag = await auto_resolve_tag(tags, self.session)
        if not exact_tag:
            await interaction.followup.send(f"❌ No results found for the given tags. `{tags}` on Danbooru.")
            return

        print(f"Resolved user input '{tags}' to exact tag '{exact_tag}' for Danbooru search.")
        exact_tag = await NSFW_check(interaction, exact_tag)  # Check if the channel is NSFW and adjust tags accordingly
        if exact_tag is None:
            return  # Exit if the channel is not NSFW and the user tried to search for NSFW content

        params = {
            'tags': f'{exact_tag} animated',
            'limit': limit or 10,
        }

        # Add API key and login if they are set in the environment variables
        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        session = self.bot.session
        try:
            headers = {
                'User-Agent': 'MyDiscordBot/1.0 (by Mirera on Discord)'
            }
            
            async with session.get("https://danbooru.donmai.us/posts.json", params=params, headers=headers) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Fetched {len(data)} posts from Danbooru for tags '{tags}' with limit {limit}.")
                    # Filter out posts that don't have a valid file_url (exclude posts that are deleted or have no image or premium content)
                    valid_posts = [post for post in data if post.get('file_url') is not None]

                    if len(valid_posts) > 0:
                        view = VideoEmbed(valid_posts, tags)
                        result = await view.create_embed()
                        await interaction.followup.send(content=result['content'], embed=result['embed'], view=view)

                    else:
                        await interaction.followup.send("No results found for the given tags.")

                else:
                    await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")

    @danbooru_modules.command(name='video_nsfw', description='Fetches a list of random videos from Danbooru')
    @app_commands.describe(tag='Tag to search for', limit='Number of results to return (max 100)')
    async def video_nsfw(self, interaction: discord.Interaction, tag: str, limit: Optional[int] = 10):
        """Search Danbooru for random NSFW videos based on the provided tag."""

        await interaction.response.defer()

        exact_tag = await auto_resolve_tag(tag, self.session)
        if not exact_tag:
            await interaction.followup.send(f"❌ No results found for the given tag. `{tag}` on Danbooru.")
            return

        print(f"Resolved user input '{tag}' to exact tag '{exact_tag}' for Danbooru search.")
        exact_tag = await NSFW_check(interaction, exact_tag)  # Check if the channel is NSFW and adjust tags accordingly
        if exact_tag is None:
            return  # Exit if the channel is not NSFW and the user tried to search for NSFW content

        params = {
            'tags': f'{exact_tag} animated rating:e',  # Explicit ratings
            'limit': limit or 10
        }

        if self.api_key and self.api_login:
            params['api_key'] = self.api_key
            params['login'] = self.api_login

        session = self.bot.session
        try:
            header = {
                'User-Agent': 'MyDiscordBot/1.0 (by Mirera on Discord)'
            }

            async with session.get("https://danbooru.donmai.us/posts.json", params=params, headers=header) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Fetched {len(data)} posts from Danbooru for tags '{tag}' with limit {limit}.")
                    # Filter out posts that don't have a valid file_url (exclude posts that are deleted or have no image or premium content)
                    valid_posts = [post for post in data if post.get('file_url') is not None]

                    if len(valid_posts) > 0:
                        view = VideoEmbed(valid_posts, tag)
                        result = await view.create_embed()
                        await interaction.followup.send(content=result['content'], embed=result['embed'], view=view)

                    else:
                        await interaction.followup.send("No results found for the given tags.")

                else:
                    await interaction.followup.send(f"Error: Unable to fetch data from Danbooru (Status Code: {response.status}: {response.reason})")

        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching data from Danbooru: {e}")

async def setup(bot):
    await bot.add_cog(DanbooruModule(bot))

async def NSFW_check(interaction, tags):
    # check if the channel is NSFW and if the tags contain NSFW content
    if not interaction.channel.is_nsfw():
        if 'rating:e' in tags or 'rating:q' in tags:
            # If the channel is not NSFW and the user is trying to search for NSFW content, send a warning message and return
            await interaction.followup.send("NSFW content is not allowed in this channel.")
            return None
        
        if 'rating:' not in tags:
            print(f"User input '{tags}' does not contain a rating tag. Adding 'rating:safe'.")
            tags = f"{tags} rating:safe".strip()
    return tags

async def check_tag_limit(interaction, params):
    # check if the number of tags exceeds 2 (for free accounts)
    # Tách chuỗi tags thành danh sách để đếm (dựa theo khoảng trắng)
    tag_list = params['tags'].split()
    if len(tag_list) > 2:
        await interaction.followup.send(
            f"⚠️ **Limit:** Free Account only allows up to 2 tags/search. "
            f"You are searching for {len(tag_list)} tags (including the automatic `rating:safe` tag added to non-NSFW channels). "
            f"Please reduce the number of tags."
        )

async def auto_resolve_tag(query: str, session) -> str:
    """
    Hàm này dịch từ khóa gõ tay của người dùng thành Tag chuẩn của Danbooru.
    Ví dụ: 'miku project sekai' -> 'hatsune_miku_(project_sekai)'
    """

    # Thay thế dấu cách bằng dấu * để quét rộng. 
    # Ví dụ: "miku project sekai" -> "*miku*project*sekai*"
    formatted_query = "*".join(query.strip().split())
    
    params = {
        'search[name_or_alias_matches]': f'{formatted_query}*',
        'search[order]': 'count', # pioritize tags with higher post counts
        'limit': 1
    }
    
    async with session.get("https://danbooru.donmai.us/tags.json", params=params) as resp:
        if resp.status == 200:
            data = await resp.json()
            if data: # Nếu tìm thấy ít nhất 1 tag
                # Trả về tên chuẩn xác (không có dấu sao)
                return data[0]['name']
            
    # if no tags found, return None
    return None

async def caching_images(interaction, cache, cache_key, tags):
    if cache_key in cache:
        print(f"Caching results for tags: {tags}")
        results = cache[cache_key]
        if len(results) > 0:
            view = ImageEmbed(results, tags)
            await interaction.followup.send(embed=view.create_embed(), view=view)
        else:
            await interaction.followup.send("No results found for the given tags.")
        return # Gửi xong rồi mới thoát hàm