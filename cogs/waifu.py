import discord
from discord.ext import commands
import asyncio
import aiohttp
import random
from datetime import datetime

async def close_session(http_session):
    await http_session.close()

class Waifu(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()

    @commands.group(invoke_without_command = True)
    async def waifu(self, ctx):
        url = "https://waifu.pics/api/sfw/waifu"
        async with self.session.get(url) as response:
            data = await response.json()
            url = data.get("url")
            embed = discord.Embed(
                colour = self.client.colours["EMBEDCOLOUR"],
                timestamp = datetime.utcnow()
            )
            embed.set_author(name = str(ctx.author), icon_url = ctx.author.avatar_url)
            embed.set_image(url = url)
            await ctx.send(embed = embed)

    @waifu.command()
    async def nsfw(self, ctx, *, category = None):
        if not ctx.channel.nsfw and not ctx.author.id == 775102060944293901:
            await ctx.send("**No! Why don't you slide into an NSFW channel instead. I'll be glad to play with you there! Hehe!**")
            return
        categories = ["waifu", "neko", "trap", "blowjob"]
        if category is None or category not in categories:
            category = random.choice(categories)
            url = f"https://waifu.pics/api/nsfw/{category}"
            async with self.session.get(url) as response:
                data = await response.json()
                url = data.get("url")
                embed = discord.Embed(
                    colour = self.client.colours["EMBEDCOLOUR"],
                    timestamp = datetime.utcnow()
                )
                embed.set_author(name = str(ctx.author), icon_url = ctx.author.avatar_url)
                embed.set_image(url = url)
                await ctx.send(embed = embed)

        
        




    def cog_unload(self):
        asyncio.get_event_loop().run_until_complete(close_session(self.session))



def setup(client):
    client.add_cog(Waifu(client))