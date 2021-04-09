import os
import discord
from discord.ext import commands
import custom_functions
import sqlite3
from datetime import datetime
import asyncio

"""
Leveling commands. Not yet complete.
"""

# Connect to database
try:
    dbdir = os.getcwd() + '/database.sqlite'
    conn = custom_functions.SqliteConnection(dbdir).conn
except AttributeError as error:
    print("Failed to connect to sqlite table!", error)


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="xp")
    async def xp(self, ctx, user: discord.Member = None):

        if user:
            cursor = conn.cursor()
            cursor.execute(f'SELECT xp FROM message_levels WHERE user_id = {user.id}')
            result = cursor.fetchone()
            await ctx.send(f'{user.name}#{user.discriminator} has {result[0]} experience points!')
            cursor.close()
        else:
            # Execute query to get xp from specified user.
            cursor = conn.cursor()
            cursor.execute(f'SELECT xp FROM message_levels WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()

            # Send the amount of experience the user has.
            await ctx.send(f'You have {result[0]} experience points!')
            cursor.close()

    # Handle errors if input is invalid
    @xp.error
    async def xp_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("I could not find that member. Please try again.")

    @commands.command(name="level")
    async def level(self, ctx, user: discord.Member = None):
        if user:
            cursor = conn.cursor()
            cursor.execute(f'SELECT level FROM message_levels WHERE user_id = {user.id}')
            result = cursor.fetchone()
            level = result[0]
            await ctx.send(f'{user.name}#{user.discriminator} is level {level}!')

            if level >= 5:
                # Assign roles
                level_roles = [5, 10, 20, 30, 40, 50, 60, 70, 80]
                index = int((level - level % 10) / 10)
                role = discord.utils.find(lambda r: r.name == f"Level {level_roles[index]}", ctx.guild.roles)

                if role and role not in user.roles:
                    await user.add_roles(role)

        else:
            # Execute query to get user's level.
            cursor = conn.cursor()
            cursor.execute(f'SELECT level FROM message_levels WHERE user_id = {ctx.author.id}')
            result = cursor.fetchone()
            level = int(result[0])

            # Reply with level number
            await ctx.send(f'You are level {level}!')

            if level >= 5:
                # Assign roles
                level_roles = [5, 10, 20, 30, 40, 50, 60, 70, 80]
                index = int((level - level % 10) / 10)

                role = discord.utils.find(lambda r: r.name == f"Level {level_roles[index]}", ctx.guild.roles)

                if role and role not in ctx.author.roles:
                    await ctx.author.add_roles(role)
        cursor.close()

    @level.error
    async def level_error(self, ctx, err):
        print(err)
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("I could not find that member. Please try again.")


def setup(bot):
    bot.add_cog(Leveling(bot))
