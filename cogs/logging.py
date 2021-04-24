from discord.ext import commands
import discord
from io import StringIO
from datetime import datetime


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channellogs", aliases=["logs"])
    @commands.has_permissions(manage_messages=True)
    async def channellogs(self, ctx, count: int, *selected_channel: discord.TextChannel):
        start = datetime.now()
        if count > 1000:
            await ctx.send("Error! Please do not log more than 1,000 messages!")
            return

        if selected_channel:
            channel = selected_channel[0]
        else:
            channel = ctx.channel
        try:
            with open(f"logs/{channel.id}-{channel.name}.txt", "r", encoding="utf8") as f:
                lines = f.readlines()[-1 * count:]
                f.close()
        except FileNotFoundError:
            await ctx.send("There do not seem to be any logs for that channel!")
            return

        with StringIO() as file_binary:
            for line in lines:
                file_binary.write(line)
            file_binary.seek(0)
            await ctx.send(f"Returned last {count} messages from {channel.mention} in "
                           f"{str(datetime.now() - start)[6:]} seconds.")
            await ctx.send(file=discord.File(fp=file_binary,
                                             filename=f"{str(datetime.now())[:-7]}-{channel.name}-message-logs.txt"))
            file_binary.close()

    @channellogs.error
    async def messagelog_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please provide a number of messages to retrieve the logs for!")
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("Input could not be understood! "
                           "Please be sure to provide an integer value for the number of messages to retrieve logs "
                           "for, as well as the specified channel.")

    @commands.command(name="messagelog")
    @commands.has_permissions(manage_messages=True)
    async def messagelog(self, ctx, count: int, *channel: discord.TextChannel):
        await ctx.message.delete()

        if count > 1000:
            await ctx.send("Error! Please do not log more than 1,000 messages.")
            return

        with StringIO() as file_binary:
            async for message in ctx.channel.history(limit=count):
                time = message.created_at
                user = f"{message.author.name}#{message.author.discriminator}"
                file_binary.write(f"[{time}] ({message.author.id}) {user}: {message.system_content}\n")
            file_binary.seek(0)
            if channel:
                await channel[0].send(file=discord.File(fp=file_binary, filename=f"{str(datetime.now())[:-7]}-log.txt"))
            else:
                await ctx.send(file=discord.File(fp=file_binary, filename=f"{str(datetime.now())[:-7]}-log.txt"))
            file_binary.close()

    @messagelog.error
    async def messagelog_error(self, ctx, err):
        print(err)
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please provide a number of messages to log!")
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("Input could not be understood! "
                           "Please be sure to provide an integer value for the number of messages to log.")


def setup(bot):
    bot.add_cog(Logging(bot))