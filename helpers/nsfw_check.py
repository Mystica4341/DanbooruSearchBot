# General checking for NSFW content in channels
# If need specific checking for commands, need to implement in the command itself in their respective modules
async def isNSFW(interaction):
    if not interaction.channel.is_nsfw():
        await interaction.followup.send("NSFW content is not allowed in this channel.")
        return False
    return True