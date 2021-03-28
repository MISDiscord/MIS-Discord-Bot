import os
import discord
from discord.ext import commands
import custom_functions
import sqlite3

"""
Leveling commands. Not yet complete.
"""

# Connect to database
try:
    dbdir = os.getcwd() + '/database.sqlite'
    conn = custom_functions.SqliteConnection(dbdir).conn
except AttributeError as err:
    print("Failed to connect to sqlite table!", err)


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="xp")
    async def level(self, ctx, user: discord.Member = None):

        if user:
            cursor = conn.cursor()
            cursor.execute(f'SELECT xp FROM message_levels WHERE user_id = {user.id}')
            result = cursor.fetchone()
            await ctx.send(f'{user.name}#{user.discriminator} has {result[0]} experience points!')
        else:
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
