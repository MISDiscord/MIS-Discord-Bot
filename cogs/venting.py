from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
from datetime import datetime
import requests

load_dotenv()

CONFESS_SUBMIT_CHANNEL_ID = 826474833000661012
CONFESSION_LOG_CHANNEL_ID = 826516916196999198


class Venting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="noresponse")
    async def no_response(self, ctx):
        if ctx.channel.id != CONFESS_SUBMIT_CHANNEL_ID:
            await ctx.send(f"Error! Please only use this command in <#{CONFESS_SUBMIT_CHANNEL_ID}>")
            return
        else:
            channel_id = 795669876345274378

            json_params = {"channel_id": channel_id}
            headers = {"Authorization": "Bot " + os.getenv("BOT_TOKEN")}
            url = '/'.join(os.getenv("ANONYMOUS_CONFESSIONS_WEBHOOK_URL").split("/")[:6])

            change_channel = requests.patch(url, json=json_params, headers=headers)

            send_msg = requests.post(url=os.getenv("ANONYMOUS_CONFESSIONS_WEBHOOK_URL"),
                                     data={"content": ctx.message.content[12:]})

            await ctx.message.delete()

            embed = discord.Embed(title="Confession Log", url=" ", color=0xabc9FF)
            embed.set_author(name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}",
                             icon_url=ctx.message.author.avatar_url)
            embed.add_field(name="Message Content:", value=ctx.message.content[12:], inline=False)
            embed.set_footer(text=f"ID: {ctx.message.author.id} • {datetime.now().strftime('Today at %I:%M %p')}")

            await self.bot.get_channel(CONFESSION_LOG_CHANNEL_ID).send(embed=embed)

    @commands.command(name="response")
    async def response(self, ctx):
        if ctx.channel.id != CONFESS_SUBMIT_CHANNEL_ID:
            await ctx.send(f"Error! Please only use this command in <#{CONFESS_SUBMIT_CHANNEL_ID}>")
            return
        else:
            channel_id = 702184354092417084

            json_params = {"channel_id": channel_id}
            headers = {"Authorization": "Bot " + os.getenv("BOT_TOKEN")}
            url = '/'.join(os.getenv("ANONYMOUS_CONFESSIONS_WEBHOOK_URL").split("/")[:6])

            change_channel = requests.patch(url, json=json_params, headers=headers)

            send_msg = requests.post(url=os.getenv("ANONYMOUS_CONFESSIONS_WEBHOOK_URL"),
                                     data={"content": ctx.message.content[10:]})

            await ctx.message.delete()

            embed = discord.Embed(title="Confession Log", url=" ", color=0xabc9FF)
            embed.set_author(name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}",
                             icon_url=ctx.message.author.avatar_url)
            embed.add_field(name="Message Content:", value=ctx.message.content[10:], inline=False)
            embed.set_footer(text=f"ID: {ctx.message.author.id} • {datetime.now().strftime('Today at %I:%M %p')}")

            await self.bot.get_channel(CONFESSION_LOG_CHANNEL_ID).send(embed=embed)


def setup(bot):
    bot.add_cog(Venting(bot))
