import discord
import math
import os
from helpers.button_paginator import EmbedPaginator

class ImageEmbed(EmbedPaginator):
    def __init__(self, results):
        super().__init__()
        self.results = results

        # Total pages is the length of the posts list
        self.total_pages = len(self.results) 
        self.update_buttons()
        
    # Override the create_embed method to display the current post
    def create_embed(self):
      try:

        index_result = self.results[self.current_page]
        title = index_result.get("english_title", "No Title")
        cover_id = index_result.get("thumbnail")
        cover_url = f"https://t1.nhentai.net/{cover_id}"
        doujinshi_id = index_result.get("id")
        doujinshi_url = f"https://nhentai.net/g/{doujinshi_id}"

        embed = discord.Embed(
            title=title,
            url=doujinshi_url,
            color=discord.Color.dark_green()
        )

        embed.set_image(url=cover_url)

        # Footer (ex: 1/10)
        embed.set_footer(text=f"ID: {doujinshi_id} \nTrang {self.current_page + 1}/{self.total_pages}")
        return embed
      
      except Exception as e:
          return discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())
        
class DetailImageEmbed(EmbedPaginator):
    def __init__(self, results):
        super().__init__()
        self.results = results

        # Total pages is the length of the posts list
        self.total_pages = len(self.results) 
        self.update_buttons()
        
    # Override the create_embed method to display the current post
    def create_embed(self):
      try:

        index_result = self.results[self.current_page]
        title = index_result.get("title", {}).get("english", "No Title")
        cover_id = index_result.get("thumbnail").get("path")
        cover_url = f"https://t1.nhentai.net/{cover_id}"
        doujinshi_id = index_result.get("id")
        doujinshi_url = f"https://nhentai.net/g/{doujinshi_id}"

        embed = discord.Embed(
            title=title,
            url=doujinshi_url,
            color=discord.Color.dark_green()
        )

        embed.set_image(url=cover_url)

        # Footer (ex: 1/10)
        embed.set_footer(text=f"ID: {doujinshi_id} \nTrang {self.current_page + 1}/{self.total_pages}")
        return embed
      
      except Exception as e:
          return discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())