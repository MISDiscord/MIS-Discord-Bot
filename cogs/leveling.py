import os
import discord
from discord.ext import commands
import sqlite3

"""
Leveling commands. Not yet complete.
"""

# Connect to database
try:
    dbdir = os.getcwd() + '/database.sqlite'
    print(dbdir)
    conn = sqlite3.connect(dbdir)
    print("Connected!")
except sqlite3.Error as error:
    print("Failed to connect to sqlite table", error)


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="xp")
    async def level(self, ctx):

        # Execute query to get xp from specified user.
        cursor = conn.cursor()
        cursor.execute(f'SELECT xp FROM message_levels WHERE user_id = {ctx.author.id}')
        result = cursor.fetchone()

        # Send the amount of experience the user has.
        await ctx.send(f'You have {result[0]} experience points!')
        cursor.close()

    # Handle errors if input is invalid
    @level.error
    async def level_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("I could not find that member. Please try again.")


def setup(bot):
    bot.add_cog(Leveling(bot))
