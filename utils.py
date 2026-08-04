import discord

async def send_error(interaction: discord.Interaction, error_message: str):
    """
    Hàm gửi thông báo lỗi dùng chung cho mọi command.
    Tự động kiểm tra xem interaction đã được defer hay chưa để dùng phương thức gửi phù hợp.
    """
    embed = discord.Embed(
        title="⚠️ Error Occurred",
        description=error_message,
        color=discord.Color.red()
    )
    embed.set_footer(text="Please check your request.")
    try:
        # Nếu đã dùng await interaction.response.defer() trước đó
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        # Nếu chưa defer()
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"Error occurred while sending error message: {e}")