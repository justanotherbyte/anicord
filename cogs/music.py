import discord
from discord.ext import commands, tasks
import lavalink
import subprocess
import sys
import datetime
from plugins import errormsgs
from plugins import sysmsgs


def lavalink_init():
    subprocess.Popen(["java", "-jar", "Lavalink.jar"] + sys.argv[1:])



    
def seconds_to_minutes(seconds: int) -> str:
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds) 


class music(commands.Cog):
    def __init__(self, client):
        #subprocess.call(["java", "-jar", "Lavalink.jar"])
        lavalink_init()
        self.client = client
        self.prefix = self.client.command_prefix
        self.client.music = lavalink.Client(self.client.user.id)
        self.client.music.add_node("localhost", 8080, self.client.lavalink_token, "eu", "music-node")   #self.client.music.add_node("localhost", 7000, "testing", "na", "music-node")
        self.client.add_listener(self.client.music.voice_update_handler, "on_socket_response")
        self.client.music.add_event_hook(self.track_hook)
        self.rcmanager.start()


    @tasks.loop()
    async def rcmanager(self):
        for client in self.client.voice_clients:
            if len(client.members) == 0:
                client.cleanup()
                await client.disconnect()
        
    
    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id : int, channel_id : str):
        ws = self.client._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    @commands.command(usage = "")
    async def join(self, ctx):
        print("join command worked!")
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            await sysmsgs.sys(ctx, f"Connected to **{member.voice.channel.name}**")

    
    @commands.command(usage = "[link or query]")
    async def search(self, ctx, *, query):
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        


        player = self.client.music.player_manager.get(ctx.guild.id)
        query = f"ytsearch:{query}"
        results = await player.node.get_tracks(query)
        tracks = results["tracks"][0:10]
        i = 0
        query_result = ""
        for track in tracks:
            i = i + 1
            query_result = query_result + f"`{i}` [{track['info']['title']}]({track['info']['uri']})\n\n"
        embed = discord.Embed(
            title = "Search & Play!",
            colour = self.client.colours["EMBEDCOLOUR"]
        )
        embed.description = query_result
        embed.set_footer(text = "Type a number to make a choice! Type [cancel] to cancel the command!", icon_url = self.client.user.avatar_url)
        msg = await ctx.send(embed = embed)
        def check(m):
            return m.author.id == ctx.author.id

        response = await self.client.wait_for("message", check = check, timeout = 30.0)
        if response.content.lower() == "cancel":
            await msg.delete()
            await errormsgs.pass_error(ctx, "Cancelled Command!")
            return

        track = tracks[int(response.content) - 1]
        player.add(requester = ctx.author.id, track = track)
        await msg.delete()
        if not player.is_playing:
            await player.play()
            p_embed = discord.Embed(
                title = track["info"]["title"],
                url = track["info"]["uri"],
                colour = self.client.colours["EMBEDCOLOUR"]
            )
            p_embed.set_author(name = "Playing/Added to Queue",  icon_url = ctx.author.avatar_url)
            p_embed.add_field(name = "Channel", value = track["info"]["author"], inline = True)
            #duration = datetime.timedelta(seconds = track["info"]["length"])
            p_embed.add_field(name = "Duration", value = str(seconds_to_minutes(int(track["info"]["length"])/1000)).replace(".0", ""), inline = True)
            await ctx.send(embed = p_embed)

    @commands.command(usage = "[link or query]", aliases = ["p"])
    async def play(self, ctx, *, query : str):
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        elif member.voice is None and player.is_connected is not None:
            await errormsgs.pass_error(ctx, f"You have to be in the same voice channel as {self.client.user.name} to use this command!")
            return
        

        
        query = f"ytsearch:{query}"
        player = self.client.music.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await errormsgs.pass_error(ctx, f"I'm already playing something. Please use the `{self.client.command_prefix[0]}add` command to add something to the queue!")
            return

        results = await player.node.get_tracks(query)
        track = results["tracks"][0]
        player.add(requester = member.id, track = track)
        if not player.is_playing:
            await player.play()
            #await ctx.send(track)
            p_embed = discord.Embed(
                title = track["info"]["title"],
                url = track["info"]["uri"],
                colour = self.client.colours["EMBEDCOLOUR"]
            )
            p_embed.set_author(name = "Playing/Added to Queue",  icon_url = ctx.author.avatar_url)
            p_embed.add_field(name = "Channel", value = track["info"]["author"], inline = True)
            #duration = datetime.timedelta(seconds = track["info"]["length"])
            p_embed.add_field(name = "Duration", value = str(seconds_to_minutes(track["info"]["length"]/1000)), inline = True)
            await ctx.send(embed = p_embed)


    



    

    @commands.command(usage = "")
    async def stop(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I'm not playing anything!")
        player.repeat = False
        await player.stop()
        await sysmsgs.sys(ctx, "Stopped Music!")


    @commands.command(usage = "")
    async def loop(self, ctx):
        guild_id = int(ctx.guild.id)
        player = self.client.music.player_manager.get(guild_id)
        
        #await ctx.send(str(queue))
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I'm not playing anything!")
            return
        
        if player.repeat == True:
            player.repeat = False
            await sysmsgs.sys(ctx, "Disabled Player Loop!")
        elif player.repeat == False:
            player.repeat = True
            await sysmsgs.sys(ctx, "Looping the **queue**")
            
    
    @commands.command(usage = "[volume level]")
    @commands.has_permissions(manage_guild = True)
    async def volume(self, ctx, vol_level : int):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I'm not playing anything!")
            return
        
        await player.set_volume(vol_level)
        await sysmsgs.sys(ctx, f"Set Volume to `{vol_level}`")

    
    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await errormsgs.pass_error(ctx, "You need to have `manage_guild` permissions to run this command!")


    @commands.command(usage = "")
    async def skip(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I'm not playing anything!")
            return
        
        await player.skip()
        was_looping = False
        if player.repeat == True:
            was_looping = True
            player.repeat == False
        await sysmsgs.sys(ctx, "Skipped Track!")
        if was_looping == True:
            player.repeat = True


    @commands.command(usage = "")
    async def pause(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I am not playing anything!")
            return
        if player.paused == True:
            await player.set_pause(False)
            await sysmsgs.sys(ctx, "**Resumed** Music!")
        elif player.paused == False:
            await player.set_pause(True)
            await sysmsgs.sys(ctx, "**Paused** Music!")


    @commands.command(usage = "[link or query]")
    async def add(self, ctx, *, query : str):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        query = f"ytsearch:{query}"
        results = await player.node.get_tracks(query)
        tracks = results["tracks"][0:10]
        i = 0
        query_result = ""
        for track in tracks:
            i = i + 1
            query_result = query_result + f"`{i}` [{track['info']['title']}]({track['info']['uri']})\n\n"
        embed = discord.Embed(
            title = "Search & Queue!",
            colour = self.client.colours["EMBEDCOLOUR"]
        )
        embed.description = query_result
        embed.set_footer(text = "Type a number to make a choice! Type [cancel] to cancel the command!", icon_url = self.client.user.avatar_url)
        msg = await ctx.send(embed = embed)
        def check(m):
            return m.author.id == ctx.author.id

        response = await self.client.wait_for("message", check = check, timeout = 30.0)
        if response.content.lower() == "cancel":
            await msg.delete()
            await ctx.send("Cancelled Command!")
            return

        track = tracks[int(response.content) - 1]
        player.add(ctx.author.id, track)
        await ctx.send(f"Added `{track['info']['title']}` to queue")


    @commands.command(usage = "[link or query]")
    async def queue(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send(f"I am not playing anything! Use the `{self.client.command_prefix}play` command!")
            return
        queue = player.queue
        queue_list = "No Queue"
        counter = 0
        for i in queue:
            if queue_list != "":
                queue_list = ""
            counter = counter + 1
            song_title = i["title"]
            if queue.index(i) == 0:
                queue_list = f"`{counter}.` **{song_title}**"
            else:
                queue_list = queue_list + "\n" + f"`{counter}.` **{song_title}**"

        embed = discord.Embed(
            title = "Song Queue for {}".format(ctx.guild.name),
            colour = self.client.colours["EMBEDCOLOUR"],
            description = queue_list
        )

        await ctx.send(embed = embed)


    @commands.command()
    async def nodestats(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        stats = player.node.stats
        uptime = stats.uptime
        players = stats.players
        memory_free = round(stats.memory_free / 1024)
        memory_used = round(stats.memory_used / 1024)
        memory_allocated = round(stats.memory_allocated / 1024)
        cores = stats.cpu_cores
        embed = discord.Embed(
            title = "Node Info",
            description = f"The Node Info for {ctx.guild.name}\nMemory is in MB",
            colour = self.client.colours["EMBEDCOLOUR"]
        )
        embed.add_field(name = "Uptime", value = uptime, inline = True)
        embed.add_field(name = "Players", value = players, inline = True)
        embed.add_field(name = "Memory Used", value = f"{memory_used} MB", inline = True)
        embed.add_field(name = "Memory Free", value = f"{memory_free} MB", inline = True)
        embed.add_field(name = "Memory Allocated", value = f"{memory_allocated} MB", inline = True)
        embed.add_field(name = "CPU Cores", value = cores, inline = True)
        await ctx.send(embed = embed)


    @commands.command(usage = "[link or query]", aliases = ["sc"])
    async def soundcloud(self, ctx, *, query : str):
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))

        query = f"scsearch:{query}"
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if player.is_playing:
            await errormsgs.pass_error(ctx, f"I'm already playing something. Please use the `{self.client.command_prefix}add` command to add something to the queue!")
            return

        results = await player.node.get_tracks(query)
        track = results["tracks"][0]
        player.add(requester = member.id, track = track)
        if not player.is_playing:
            await player.play()
            p_embed = discord.Embed(
                title = track["info"]["title"],
                url = track["info"]["uri"],
                colour = discord.Colour.orange()
            )
            p_embed.set_author(name = "Playing/Added to Queue",  icon_url = ctx.author.avatar_url)
            p_embed.add_field(name = "Channel", value = track["info"]["author"], inline = True)
            #duration = datetime.timedelta(seconds = track["info"]["length"])
            p_embed.add_field(name = "Duration", value = str(seconds_to_minutes(track["info"]["length"]/1000)), inline = True)
            await ctx.send(embed = p_embed)

#51, 153, 255

    @commands.command(usage = "[link or query]")
    async def vimeo(self, ctx, *, query : str):
        if not "vimeo.com" in query.lower():
            await errormsgs.pass_error(ctx, "That's not a valid vimeo link!")
            return

        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        #query = f"scsearch:{query}"
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if player.is_playing:
            await errormsgs.pass_error(ctx, f"I'm already playing something. Please use the `{self.client.command_prefix}add` command to add something to the queue!")
            return

        results = await player.node.get_tracks(query)
        track = results["tracks"][0]
        player.add(requester = member.id, track = track)
        if not player.is_playing:
            await player.play()

            p_embed = discord.Embed(
                title = track["info"]["title"],
                url = track["info"]["uri"],
                colour = discord.Colour.from_rgb(153, 204, 255)
            )
            p_embed.set_author(name = "Playing/Added to Queue",  icon_url = ctx.author.avatar_url)
            p_embed.add_field(name = "Channel", value = track["info"]["author"], inline = True)
            #duration = datetime.timedelta(seconds = track["info"]["length"])
            p_embed.add_field(name = "Duration", value = str(seconds_to_minutes(track["info"]["length"]/1000)), inline = True)
            await ctx.send(embed = p_embed)


    @commands.command(usage = "[link or query]")
    async def twitch(self, ctx, *, query : str):
        if not "twitch.tv" in query.lower():
            await errormsgs.pass_error(ctx, "That's not a valid twitch link!")
            return

        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        #query = f"scsearch:{query}"
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if player.is_playing:
            await errormsgs.pass_error(ctx, f"I'm already playing something. Please use the `{self.client.command_prefix}add` command to add something to the queue!")
            return

        results = await player.node.get_tracks(query)
        track = results["tracks"][0]
        player.add(requester = member.id, track = track)
        if not player.is_playing:
            await player.play()

            p_embed = discord.Embed(
                title = track["info"]["title"],
                url = track["info"]["uri"],
                colour = discord.Colour.purple()
            )
            p_embed.set_author(name = "Playing/Added to Queue",  icon_url = ctx.author.avatar_url)
            p_embed.add_field(name = "Channel", value = track["info"]["author"], inline = True)
            #duration = datetime.timedelta(seconds = track["info"]["length"])
            p_embed.add_field(name = "Duration", value = str(seconds_to_minutes(track["info"]["length"]/1000)), inline = True)
            await ctx.send(embed = p_embed)



    @commands.command(usage = "[link or query]")
    async def bandcamp(self, ctx, *, query : str):
        if not "bandcamp.com" in query.lower():
            await errormsgs.pass_error(ctx, "That's not a valid bandcamp link!")
            return
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        #query = f"scsearch:{query}"
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if player.is_playing:
            await errormsgs.pass_error(ctx, f"I'm already playing something. Please use the `{self.client.command_prefix}add` command to add something to the queue!")
            return

        results = await player.node.get_tracks(query)
        track = results["tracks"][0]
        player.add(requester = member.id, track = track)
        if not player.is_playing:
            await player.play()

            p_embed = discord.Embed(
                title = track["info"]["title"],
                url = track["info"]["uri"],
                colour = discord.Colour.magenta()
            )
            p_embed.set_author(name = "Playing/Added to Queue",  icon_url = ctx.author.avatar_url)
            p_embed.add_field(name = "Channel", value = track["info"]["author"], inline = True)
            #duration = datetime.timedelta(seconds = track["info"]["length"])
            p_embed.add_field(name = "Duration", value = str(seconds_to_minutes(track["info"]["length"]/1000)), inline = True)
            await ctx.send(embed = p_embed)


    



    

    
    @commands.command()
    async def playlist(self, ctx, *, name : str):
        playlist = await get_playlist(ctx.author.id, name)
        if playlist == None:
            await errormsgs.pass_error(ctx, "I couldn't find a playlist with that name!")
            return
        member = ctx.author
        if member is not None and member.voice is not None:
            vc = member.voice.channel
            player = self.client.music.player_manager.create(ctx.guild.id, endpoint = str(ctx.guild.region))
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        i = 0
        pl_len = len(playlist)
        for song in playlist:
            try:
                query = f"ytsearch:{song}"
                results = await player.node.get_tracks(query)
                track = results["tracks"][0]
                player.add(ctx.author.id, track)
                i += 1
            except:
                continue

        await sysmsgs.sys(ctx, f"Queued `{i}/{pl_len}` songs!")
        if not player.is_playing:
            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            await player.play()
            await sysmsgs.sys(ctx, f"Started Playlist Queue!")
            songs = ""
            i = 0
            for _ in playlist:
                i += 1
                songs = songs + "\n" + f"`{i}` {_}"

            embed = discord.Embed(
                title = "Playlist Viewer",
                description = songs,
                colour = self.client.colours["EMBEDCOLOUR"]
            )
            await ctx.send(embed = embed)


    
    @commands.command()
    async def shuffle(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I'm not playing any music!")
            return
        
        if player.shuffle == True:
            await sysmsgs.sys(ctx, "Shuffled the queue!")
        else:
            player.shuffle = True
            await sysmsgs.sys(ctx, "Shuffled the queue!")


    @commands.command()
    async def current(self, ctx):
        player = self.client.music.player_manager.get(ctx.guild.id)
        
        if not player.is_playing:
            await errormsgs.pass_error(ctx, "I'm not playing anything right now!")
            return
        current_track = player.current
        await sysmsgs.sys(ctx, f"Current Track: `{current_track.title}`")


    
    



    
    

def setup(client):
    client.add_cog(music(client))