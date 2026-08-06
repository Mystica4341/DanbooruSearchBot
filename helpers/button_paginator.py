import discord

class EmbedPaginator(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # Hết hạn sau 3 phút
        self.current_page = 0
        self.total_pages = 1

    def update_buttons(self):
        # Vô hiệu hóa nút "Prev" nếu đang ở trang đầu
        self.prev_button.disabled = (self.current_page == 0)
        
        # Vô hiệu hóa nút "Next" nếu đang ở trang cuối hoặc không có dữ liệu
        self.next_button.disabled = (self.current_page >= self.total_pages - 1) or (self.total_pages == 0)

    # Nút Prev
    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.primary, custom_id="prev_btn")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    # Nút Next
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary, custom_id="next_btn")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    def create_embed(self):
        raise NotImplementedError("This method should be implemented in subclasses or instances where needed.")