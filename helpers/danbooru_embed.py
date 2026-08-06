import discord
import math
import os
from helpers.button_paginator import EmbedPaginator

CLOUDFLARE_URL_WORKER = os.getenv('CLOUDFLARE_URL_WORKER')  # Lấy URL Cloudflare Worker từ biến môi trường

class ImageEmbed(EmbedPaginator):
    def __init__(self, posts, tags):
        super().__init__()
        self.posts = posts
        self.tags = tags

        # Total pages is the length of the posts list
        self.total_pages = len(self.posts) 
        self.update_buttons()
        
    # Override the create_embed method to display the current post
    def create_embed(self):
      try:
        post = self.posts[self.current_page]
        image_url = post.get('file_url')
        post_id = post.get('id')
        author = post.get('tag_string_artist', 'Unknown Artist')
        character = post.get('tag_string_character', 'Unknown Character')

        embed = discord.Embed(
            title=f"Kết quả cho: {self.tags}", 
            color=discord.Color.blue()
        )

        embed.set_image(url=image_url)
        embed.add_field(name="Artist", value=author, inline=True)
        embed.add_field(name="Character", value=character, inline=True)
        embed.description = f"[Xem bài gốc trên Danbooru](https://danbooru.donmai.us/posts/{post_id})"

        # Footer (ex: 1/10)
        embed.set_footer(text=f"Trang {self.current_page + 1}/{self.total_pages}")
        return embed
      
      except Exception as e:
          return discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())

class TextEmbed(EmbedPaginator):
    def __init__(self, tags_list, query):
        super().__init__()
        self.tags_list = tags_list    # Danh sách các tag (có thể là list các dict hoặc string)
        self.query = query            # Từ khóa người dùng đã tìm
        self.items_per_page = 10      # Số lượng tag hiển thị trên mỗi trang
        
        # Total pages is the ceiling of the length of tags_list divided by items_per_page
        self.total_pages = math.ceil(len(self.tags_list) / self.items_per_page)
        self.update_buttons()

    # Override the create_embed method to display the current page of tags
    def create_embed(self):
        try:
            # Calculate the start and end indices for slicing the tags list
            start_idx = self.current_page * self.items_per_page
            end_idx = start_idx + self.items_per_page
            current_tags = self.tags_list[start_idx:end_idx]
            
            # Create a description string for the current page of tags
            description = ""
            for index, tag in enumerate(current_tags, start=start_idx + 1):
                # Xử lý nếu tag là dict (từ API) hoặc chỉ là string đơn thuần
                if isinstance(tag, dict):
                    tag_name = tag.get('name', 'Unknown')
                    post_count = tag.get('post_count', 0)
                    description += f"`{index}.` **{tag_name}** - ({post_count} posts)\n"
                else:
                    # Nếu list truyền vào chỉ là chuỗi text
                    description += f"`{index}.` **{tag}**\n"
            
            embed = discord.Embed(
                title=f"🔎 Tìm thấy {len(self.tags_list)} tags cho: '{self.query}'", 
                description=description,
                color=discord.Color.green()
            )
            
            # Footer (ex: 1/10)
            embed.set_footer(text=f"Trang {self.current_page + 1}/{self.total_pages}")
            return embed
            
        except Exception as e:
                  return discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())

class VideoEmbed(EmbedPaginator):
    def __init__(self, posts, tags):
        super().__init__()
        self.posts = posts
        self.tags = tags

        # Total pages is the length of the posts list
        self.total_pages = len(self.posts) 
        self.update_buttons()
        
    # Override the create_embed method to display the current post
    async def create_embed(self):
        try:
            post = self.posts[self.current_page]
            video_url = post.get('file_url')
            post_id = post.get('id')
            author = post.get('tag_string_artist', 'Unknown Artist')
            character = post.get('tag_string_character', 'Unknown Character')

            embed = discord.Embed(
                title=f"Kết quả videos cho: {self.tags}", 
                color=discord.Color.blue()
            )

            embed.add_field(name="Artist", value=author, inline=True)
            embed.add_field(name="Character", value=character, inline=True)
            embed.description = f"[Xem bài gốc trên Danbooru](https://danbooru.donmai.us/posts/{post_id})"

            # Footer (ex: 1/10)
            embed.set_footer(text=f"Trang {self.current_page + 1}/{self.total_pages}")

            return {'content': f"[\u200B]({video_url})", 'embed': embed}
        
        except Exception as e:
            return {'content': None, 'embed': discord.Embed(title="Error", description=f"An error occurred while creating the embed: {e}", color=discord.Color.red())
}
