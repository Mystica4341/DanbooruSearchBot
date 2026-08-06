import discord
import os
from discord.ext import commands
from discord import app_commands
from typing import Optional
from helpers.nhentai_embed import ImageEmbed
from helpers.nsfw_check import isNSFW
import aiohttp

class NhentaiModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.search_url = "https://nhentai.net/api/v2/search"

    @app_commands.command(name="n_search", description="Search doujinshi on nhentai.net")
    @app_commands.describe(query=f"The search query (\"\" for exact search) ('artist:', 'tag:') ('-' for exclude)", language="Optional language filter", offset="Optional offset for pagination 25 results per page")
    async def n_search(self, interaction: discord.Interaction, query: str, language: Optional[str] = '',  offset: Optional[int] = 1):
        """Search doujinshi on nhentai.net based on the provided query."""

        await interaction.response.defer()  # Defer the response to give time for processing

        if not await isNSFW(interaction):  # Check if the channel is NSFW
          return

        params = {
           "query": query + (f" language:{language}" if language else ""), 
           "page": offset
          }

        async with aiohttp.ClientSession() as session:
            try:
              async with session.get(self.search_url, params=params) as response:

                if response.status == 200:
                  data = await response.json()
                  results = data.get("result", [])
                  index = 0

                  print(f"Fetched {len(results)} results from nhentai.net for query '{query}'.")

                  if results:
                    view = ImageEmbed(results)
                    await interaction.followup.send(embed=view.create_embed(), view=view)

                  else:
                      await interaction.followup.send("No results found for your query.")

                else:
                    await interaction.followup.send(f"Failed to fetch data from nhentai.net. (Status Code: {response.status}: {response.reason})")
                    
            except Exception as e:
                await interaction.followup.send(f"An error occurred while fetching data: {e}")

async def setup(bot):
    await bot.add_cog(NhentaiModule(bot))

# search_url = f"https://nhentai.net/api/galleries/search?query={query}"
# async with aiohttp.ClientSession() as session:
#     async with session.get(search_url) as response:
#         if response.status == 200:
#             data = await response.json()
#             results = data.get("result", [])
#             if results:
#                 # Create an embed for the first result
#                 first_result = results[0]
#                 title = first_result.get("title", {}).get("english", "No Title")
#                 cover_id = first_result.get("media_id")
#                 cover_url = f"https://t1.nhentai.net/galleries/{cover_id}/cover.jpg"
#                 doujinshi_id = first_result.get("id")
#                 doujinshi_url = f"https://nhentai.net/g/{doujinshi_id}/"

#                 embed = discord.Embed(title=title, url=doujinshi_url, color=discord.Color.blue())
#                 embed.set_image(url=cover_url)
#                 embed.set_footer(text=f"ID: {doujinshi_id}")

#                 await interaction.followup.send(embed=embed)
#             else:
#                 await interaction.followup.send("No results found for your query.")
#         else:
#             await interaction.followup.send("Failed to fetch data from nhentai.net.")