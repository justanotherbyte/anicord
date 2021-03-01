import discord
from discord.ext import commands


async def pass_error(ctx, error_msg : str):
    embed = discord.Embed(
        colour = discord.Colour.red(),
        description = error_msg
    )
    await ctx.send(embed = embed)


async def pass_cooldown(ctx, msg : str):
    embed = discord.Embed(
        title = "Command On Cooldown!",
        description = msg,
        colour = discord.Colour.light_grey()
    )
    embed.add_field(name = ":clock1: Why the Cooldown?", value = f"Well, to make sure server connections aren't overloaded and the bot doesn't become slow, we've added some basic cooldowns on some of the most network heavy commands! Please do understand that we're only doing this to keep {ctx.me.name} running smoothly!")
    await ctx.send(embed = embed)