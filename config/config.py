import discord

colours = {
    "EMBEDCOLOUR" : discord.Colour.blurple()
}




async def load_config(bot):
    bot.colours = colours
    