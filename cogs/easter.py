from discord.ext import tasks, commands
import json
import random
"""
Easter event cog
"""


class Easter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    # Loop every 15 minutes
    @tasks.loop(minutes=15)
    async def printer(self):
        if random.random() > 0.3:

            emojis = [
                        "<:Eggito:821374260831453184>",
                        "<:EggBurto:821380416581009438>",
                        "<:McEgg:821380416669351936>",
                        "<:Eggie:821380416987725864>"
                    ]

            channel_ids = [
                            701102362516914189,
                            805391478267969556,
                            702178236704227480,
                            714573685431730207,
                            702908817515479141,
                            816981072855695370
                        ]

            # Choose a random emoji and channel to format the message
            selection = random.choice(emojis)
            channel = self.bot.get_channel(random.choice(channel_ids))
            await channel.send(f"An easter egg has appeared! React to this message with {selection} to pick it up!")

    @printer.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    # Command for checking how many eggs a user has collected
    @commands.command(name="eggs")
    async def eggs(self, ctx):
        scoreboard_file = open('eggs.json', 'r')
        data = json.load(scoreboard_file)
        scoreboard_file.close()
        print(data["222479899808628736"])
        await ctx.send(f"{ctx.author.mention}, you have collected {data[str(ctx.author.id)]} eggs so far!")


def setup(bot):
    bot.add_cog(Easter(bot))
