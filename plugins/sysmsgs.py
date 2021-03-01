import discord

async def sys(ctx, msg : str):
    embed = discord.Embed(
        colour = discord.Colour.green(),
        description = msg
    )

    await ctx.send(embed = embed)