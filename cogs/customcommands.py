from discord.ext import commands
import discord

"""
Lily's (the American) custom single-response commands
"""


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="breathe")
    async def breathe(self, ctx):
        await ctx.message.delete()
        ctx.send("https://imgur.com/wPqVzGz")

    @commands.command(name="grounding")
    async def grounding(self, ctx):
        await ctx.message.delete()
        ctx.send("https://imgur.com/TB659EQ")

    @commands.command(name="relax")
    async def relax(self, ctx):
        await ctx.message.delete()
        ctx.send("https://imgur.com/rdpfi4N")

    @commands.command(name="hugs")
    async def hugs(self, ctx, *args):

        # If command is DM'ed to bot, try to find a specified user to send a hug to.
        if str(ctx.channel).startswith("Direct Message"):

            try:
                member = await self.bot.fetch_user(int(args[0]))
            except Exception as e:
                print(e)
                await ctx.send("Error! Cannot find that user.")
                return

            print(f'{ctx.message.author.name}#{ctx.message.author.discriminator} ({ctx.message.author.id}) sent a '
                  f'hug to {member.name}#{member.discriminator} ({member.id})')

            # Send confirmation + hugs to targeted user.
            await ctx.message.author.send(f'Sent a hug to {member.mention}!')
            await member.send(f'{ctx.message.author.mention} sent you a virtual hug!')
            await member.send("https://giphy.com/gifs/3M4NpbLCTxBqU")
        else:

            # If not executed in a DM, just reply with a hug gif.
            await ctx.message.delete()
            ctx.send("https://imgur.com/FF2klRE")


def setup(bot):
    bot.add_cog(CustomCommands(bot))
