from discord.ext import tasks, commands
import json
import random
from datetime import datetime
import discord

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
    @tasks.loop(minutes=8)
    async def printer(self):
        if random.random() > 0.1:
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
            with open('easterlogs.txt', 'a+') as f:
                f.write(f'{selection} egg spawned at {str(datetime.now())}\n')
                f.close()

            await channel.send(f"An easter egg has appeared! React to this message with {selection} to pick it up!\n")

    @printer.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    # Command for checking how many eggs a user has collected
    @commands.command(name="eggs")
    async def eggs(self, ctx, user: discord.Member = None):
        scoreboard_file = open('eggs.json', 'r')
        data = json.load(scoreboard_file)
        scoreboard_file.close()

        try:
            if user:
                await ctx.send(f"{user.name}#{user.discriminator} has collected {data[str(user.id)]} eggs so far!")
            else:
                await ctx.send(f"{ctx.author.mention}, you have collected {data[str(ctx.author.id)]} egg so far!")
        except KeyError:
            if user:
                await ctx.send(f"{user.name}#{user.discriminator} has collected 0 eggs so far!")
            else:
                await ctx.send(f"{ctx.author.mention}, you have collected 0 eggs so far!")

    @eggs.error
    async def eggs_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.MemberNotFound):
            await ctx.send("I could not find that member!")

    @commands.command(name="eggleaderboard")
    async def eggleaderboard(self, ctx):
        scoreboard_file = open('eggs.json', 'r')
        data = json.load(scoreboard_file)
        scoreboard_file.close()
        # print(data)
        sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        print(sort_data)
        leaderboard_string = "__Top 10 Users__\n\n"
        for i in sort_data[:10]:
            user = self.bot.get_user(int(i[0]))
            if i[1] == 1:
                leaderboard_string += f"{user.name}#{user.discriminator}: {i[1]} egg\n"
            else:
                leaderboard_string += f"{user.name}#{user.discriminator}: {i[1]} eggs\n"

        await ctx.send(leaderboard_string)


def setup(bot):
    bot.add_cog(Easter(bot))
