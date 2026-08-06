async def isNSFW(interaction):
    if not interaction.channel.is_nsfw():
        await interaction.followup.send("NSFW content is not allowed in this channel.")
        return False
    return True