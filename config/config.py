import discord

colours = {
    "EMBEDCOLOUR" : discord.Colour.blurple()
}

emojis = {
    "REDPASTELHEART" : "<:red_pastel_heart:815887671204511764>",
    "WHITECHECKMARK" : "✅"
}



async def load_config(bot):
    bot.colours = colours
    