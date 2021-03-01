from dhooks import Webhook
import discord


async def send_error(ctx, error):
    hook = Webhook("https://discord.com/api/webhooks/805737880047190026/gg7V8eqwl6L8B9yWz2jNXJiJbQcejgi9hgYs52dAZ6_Mej3FEd5Yj_JxSR7YGHWkL_DX")
    embed = discord.Embed(
        title = "Global Error",
        description = f"**Guild: ** {ctx.guild.name} ({ctx.guild.id})\n**Message:** `{ctx.message.content}`\n**Author:** {ctx.author} ({ctx.author.id})",
        colour = discord.Colour.orange()
    )
    embed.add_field(name = "Error", value = f"```{error}```", inline = False)
    hook.send(embed = embed)