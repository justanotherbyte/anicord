import discord
from discord.ext import commands
import aiohttp
import asyncio
from plugins.parsers import EmbedParsers
from disputils import BotEmbedPaginator
async def close_session(http_session):
    await http_session.close()

class Anime_Manga(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()
        self.base = "https://kitsu.io/api/edge"

    @commands.command(usage = "<query>")
    async def anime(self, ctx, *, query : str):
        query = query.replace(" ", r"%20")
        url = f"{self.base}/anime?filter[text]={query}"
        async with ctx.channel.typing():
            async with self.session.get(url) as response:
                data = await response.json()
                embeds = await EmbedParsers.parseforsearch(data, self.client.colours["EMBEDCOLOUR"])
                paginator = BotEmbedPaginator(ctx, embeds)
                
        await paginator.run()
        await ctx.message.add_reaction("✅")


    @commands.command(usage = "<query>")
    async def manga(self, ctx, *, query : str):
        query = query.replace(" ", r"%20")
        url = f"{self.base}/manga?filter[text]={query}"
        async with ctx.channel.typing():
            async with self.session.get(url) as response:
                data = await response.json()
                embeds = await EmbedParsers.parseforsearch(data, self.client.colours["EMBEDCOLOUR"])
                paginator = BotEmbedPaginator(ctx, embeds)
                
        await paginator.run()
        await ctx.message.add_reaction("✅")


    
            

    
    def cog_unload(self):
        asyncio.get_event_loop().run_until_complete(close_session(self.session))


def setup(client):
    client.add_cog(Anime_Manga(client))