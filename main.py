import discord
from discord.ext import commands
from dotenv import load_dotenv
from config.config import load_config
import os

def get_token():
    try:
        load_dotenv()
    except:
        pass

    return os.getenv("TOKEN")


INITIAL_EXTENSIONS = [
    "cogs.animeandmanga"
]

class Anicord(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned_or("anime ", "a!"),
            case_insensitive = True,
            owner_id = 691406006277898302
        )
        for cog in INITIAL_EXTENSIONS:
            self.load_extension(cog)
            print(f"Loaded {cog}")

    
    async def on_ready(self):
        print('Logged in as:')
        print('Username: ' + self.user.name)
        print('ID: ' + str(self.user.id))
        print('------')
        await load_config(self)

    async def on_message(self, message):
        content = message.content.lower()
        setattr(message, "content", content)
        await self.process_commands(message)

    def run(self, token):
        super().run(token)






if __name__ == "__main__":
    bot = Anicord()
    bot.run(get_token())