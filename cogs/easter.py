from discord.ext import tasks, commands

"""

"""


class Easter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=30)
    async def printer(self):
        channel = self.bot.get_channel(701103774235754537)
        await channel.send("An easter egg has appeared! React to this message with :egg: to pick it up!")
        print(channel.name)

    @printer.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Easter(bot))
