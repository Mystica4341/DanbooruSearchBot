import discord

class EmbedPaginator(discord.ui.View):
    def __init__(self, show_read_button=False):
        super().__init__(timeout=180)  # Hết hạn sau 3 phút
        self.current_page = 0
        self.total_pages = 1

        if not show_read_button:
            self.remove_item(self.read_button)  # Remove the read button if not needed

    def update_buttons(self):
        # Vô hiệu hóa nút "Prev" nếu đang ở trang đầu
        self.prev_button.disabled = (self.current_page == 0)
        
        # Vô hiệu hóa nút "Next" nếu đang ở trang cuối hoặc không có dữ liệu
        self.next_button.disabled = (self.current_page >= self.total_pages - 1) or (self.total_pages == 0)

    # Nút Prev
    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.primary, custom_id="prev_btn")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Read 📖", style=discord.ButtonStyle.danger, custom_id="read_btn")
    async def read_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # This method should be overridden in subclasses to provide specific functionality
        await self.on_read(interaction)

    # Nút Next
    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary, custom_id="next_btn")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    def create_embed(self):
        raise NotImplementedError("This method should be implemented in subclasses or instances where needed.")

    async def on_read(self, interaction: discord.Interaction):
        pass