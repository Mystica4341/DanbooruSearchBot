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
        self.total_pages = len(self.results[0].get("pages", [])) + 1  # +1 for the cover page
        self.update_buttons()
        
    # Override the create_embed method to display the current post
    def create_embed(self):
      try:

        index_result = self.results[0]

        title = index_result.get("title", {}).get("english", "No Title")
        doujinshi_id = index_result.get("id")
        doujinshi_url = f"https://nhentai.net/g/{doujinshi_id}"

        if (self.current_page == 0):
            cover_data = index_result.get("thumbnail").get("path")
            image_url = f"https://t1.nhentai.net/{cover_data}"
        else:
            pages_list = index_result.get("pages", [])

            # Cover duplicate with the first page, so we need to adjust the index for pages_list
            # page_index = self.current_page - 1  # Adjust for to seperate cover page with 1st page (which not neccessary if you want to include the cover page as the first page)

            page_index = self.current_page

            if page_index < len(pages_list):

                page_data = pages_list[page_index]
                image_url = f"https://i.nhentai.net/{page_data.get('path')}"

            else:
                image_url = None

        embed = discord.Embed(
            title=title,
            url=doujinshi_url,
            color=discord.Color.dark_green()
        )

        embed.set_image(url=image_url)

        # Footer (ex: 1/10)
        embed.set_footer(text=f"ID: {doujinshi_id} \nTrang {self.current_page + 1}/{self.total_pages}")
        return embed
      
      except Exception as e:
          return discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())