import os
import discord
from discord.ext import commands
import random
import logging
import sqlite3
import datetime
from dotenv import load_dotenv
import custom_functions
import traceback
import discord.utils
import json
import re
from datetime import datetime
import numpy as np
import requests
import asyncio

# Load env file
load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Set discord intents
intents = discord.Intents.default()
intents.members = True
intents.invites = True
intents.messages = True

# Bot user (client)
bot = commands.Bot(intents=intents, command_prefix=os.getenv("BOT_PREFIX"), help_command=None)

join_and_leave_logs_channel_id = 792161507005038612
welcome_channel_id = 798686136691458088
confession_log_channel_id = 826516916196999198

# Load cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        print(f'Loaded {filename[:-3]} cog!')
        bot.load_extension(f'cogs.{filename[:-3]}')

# Connect to sqlite3 database
try:
    dbdir = os.getcwd() + '/database.sqlite'
    conn = custom_functions.SqliteConnection(dbdir).conn
except AttributeError as err:
    print("Failed to connect to sqlite table!", err)

server_invites = {}

def is_staff(ctx):
    # Restrict command.
    t_mod = discord.utils.get(ctx.guild.roles, name="Trial Moderator")
    mod = discord.utils.get(ctx.guild.roles, name="Moderator")
    sr_mod = discord.utils.get(ctx.guild.roles, name="Senior Moderator")
    if t_mod or mod or sr_mod in ctx.author.roles:
        return True
    else:
        return False


@bot.event
async def on_ready():
    for guild in bot.guilds:
        server_invites[guild.id] = await guild.invites()
    print(f'Logged in as: {bot.user.name}#{bot.user.discriminator} ({bot.user.id})\n')


cooldown_list = {}


@bot.event
async def on_message(ctx):
    # Bots can't trigger events
    if ctx.author.bot:
        return

    # Process commands if message starts with specified prefix
    await bot.process_commands(ctx)
    print(f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}): {ctx.content}")

    if ctx.channel.id == 830171012199874600:
        await ctx.delete()
        await ctx.channel.send(ctx.content)
        embed = discord.Embed(title="Feedback Log", url="", color=0xabc9FF)
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Message Content:", value=ctx.content, inline=False)
        embed.set_footer(text=f"ID: {ctx.author.id} • {datetime.now().strftime('Today at %I:%M %p')}")
        await bot.get_channel(confession_log_channel_id).send(embed=embed)

    if ctx.channel.id == 817326358107389963 and ctx.content == "$verify":
        messages = await ctx.channel.history(limit=None).flatten()
        for message in messages:
            if message.author == ctx.author:
                await message.delete()
                await asyncio.sleep(0.5)
        # [await message.delete() for message in messages if message.author == ctx.author]
        embed = discord.Embed(title="r/mentalillness", color=0x7b57d4)
        embed.add_field(name="Welcome to r/mentalillness",
                        value=f"Hey, {ctx.author.mention}!\nHead over to <#808934814689918996> to grab some roles "
                              f"and introduce yourself in <#702569287214301206>.\n"
                              f"Feel free to start a conversation in <#824532627339083786> or join a current one and"
                              f" say hi.\nIf you need any support please head over to any of our heavy channels.\n"
                              f"Any questions? Feel free to file a ticket or ask in <#826478320472293407>.",
                        inline=False)
        await bot.get_channel(828909612291457045).send(embed=embed)

    if ctx.channel.id == 826474833000661012:
        anonymous_channel_id = 795669876345274378
        #
        # json_params = { "channel_id": anonymous_channel_id }
        # headers = { "Authorization": "Bot " + os.getenv("BOT_TOKEN") }
        # url = '/'.join(os.getenv("ANONYMOUS_CONFESSIONS_WEBHOOK_URL").split('/')[:6])
        #
        # change_channel = requests.patch(url, json=json_params, headers=headers)

        send_message = requests.post(url=os.getenv("ANONYMOUS_CONFESSIONS_WEBHOOK_URL"), data={"content": ctx.content})

        def check_user(m):
            return m.author.id == ctx.author.id

        await bot.get_channel(826474833000661012).purge(limit=5, check=check_user)

        embed = discord.Embed(title="Confession Log", url=" ", color=0xabc9FF)
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Message Content:", value=ctx.content, inline=False)
        embed.set_footer(text=f"ID: {ctx.author.id} • {datetime.now().strftime('Today at %I:%M %p')}")

        await bot.get_channel(confession_log_channel_id).send(embed=embed)

    if not ctx.content.startswith(bot.command_prefix):

        try:
            last_message = cooldown_list[ctx.author.id]
        except KeyError:
            last_message = datetime.now()
            cooldown_list[ctx.author.id] = datetime.now()

        since_last_message = datetime.now() - last_message
        if since_last_message.total_seconds() // 1 > 12:
            # Every time a user talks in chat, give them a random amount of experience points ranging from 10-15
            xp = random.randint(10, 15)
            cursor = conn.cursor()
            cursor.execute(f'SELECT xp FROM message_levels WHERE user_id = {ctx.author.id}')
            result = cursor.fetchall()
            if len(result) == 0:
                print(f"({ctx.author.id}): User is not in database. Add them!")
                cursor.execute(f'INSERT INTO message_levels VALUES ({ctx.author.id}, {xp}, {0})')
                conn.commit()
            else:
                newXP = result[0][0] + xp

                level = int(np.floor((1 + np.sqrt(1 + (4 * newXP) / 25)) / 4))

                level_roles = [5, 10, 20, 30, 40, 50, 60, 70, 80]

                if level in level_roles:
                    level_role = discord.utils.find(lambda r: r.name == f"Level {level}", ctx.guild.roles)
                    if level_role and level_role not in ctx.author.roles:
                        await ctx.author.add_roles(level_role)

                print(f'{ctx.author.name} got {xp} XP points. They now have {newXP} experience.')
                cursor.execute(
                    f'UPDATE message_levels SET xp = {newXP}, level = {level} WHERE user_id = {ctx.author.id}')
                conn.commit()
            cooldown_list[ctx.author.id] = datetime.now()

    with open(f"logs/{str(ctx.channel.id)}-{ctx.channel.name}.txt", "a+", encoding="utf8") as f:
        time = datetime.now()
        user = f"{ctx.author.name}#{ctx.author.discriminator}"
        f.write(f"[{str(time)[:-7]}] ({ctx.author.id}) {user}: {ctx.system_content}\n")
        f.close()


@bot.event
async def on_member_join(member):

    # Find invites before and after join to see which one was used
    invites_before_join = server_invites[int(member.guild.id)]
    invites_after_join = await member.guild.invites()

    foundInvite = False
    for invite in invites_before_join:

        # Find which invite has an extra use and use its data to format the embed
        if invite.uses < custom_functions.find_invite_uses_by_code(invites_after_join, invite.code):
            foundInvite = True
            embed = discord.Embed(color=0xabe9ff)
            embed.set_author(name=f'{member.name}#{member.discriminator}',
                             url=f'{member.avatar_url}',
                             icon_url=f'{member.avatar_url}')
            embed.add_field(name='Welcome to Mental Health of Reddit',
                            value=f'{member.mention} has joined using {invite.inviter.mention}\'s invite!\n'
                                  f'Code: **{invite.code}** (**{invite.uses}** uses)',
                            inline=False)
            embed.add_field(name=':bust_in_silhouette: Inviter', value=f'{invite.inviter.mention}', inline=True)
            embed.add_field(name=':white_check_mark: Invites', value=f'{invite.uses + 1}', inline=True)
            time = divmod((datetime.now() - bot.get_user(member.id).created_at).total_seconds(), 1)[0]
            embed.set_footer(text=f'Account Age: {custom_functions.seconds_to_age(int(time))}')
            await bot.get_channel(join_and_leave_logs_channel_id).send(embed=embed)

            # Update server invites
            server_invites[member.guild.id] = invites_after_join

    if not foundInvite:
        embed = discord.Embed(color=0xabe9ff)
        embed.set_author(name=f'{member.name}#{member.discriminator}',
                         url=f'{member.avatar_url}',
                         icon_url=f'{member.avatar_url}')
        embed.add_field(name='Welcome to Mental Health of Reddit',
                        value=f'{member.mention} has joined using server discovery!',
                        inline=False)
        time = divmod((datetime.now() - bot.get_user(member.id).created_at).total_seconds(), 1)[0]
        embed.set_footer(text=f'Account Age: {custom_functions.seconds_to_age(int(time))}')
        await bot.get_channel(join_and_leave_logs_channel_id).send(embed=embed)


# Print out errors
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"{str(event)}:\n{args[0]}\n{traceback.format_exc()}\n\n\n")


# Send a message to the join/leave logs when a user leaves the server
@bot.event
async def on_member_remove(member):
    server_invites[member.guild.id] = await member.guild.invites()

    embed = discord.Embed(title="Member Left", color=0xd4130d)
    embed.set_author(name=f'{member.name}#{member.discriminator}',
                     url=f'{member.avatar_url}',
                     icon_url=f'{member.avatar_url}')
    embed.add_field(name='Member', value=f'{member.mention}', inline=True)
    embed.add_field(name='Member Since', value=f'{member.joined_at.strftime("%B %d, %Y")}', inline=True)

    await bot.get_channel(join_and_leave_logs_channel_id).send(embed=embed)


# Run the bot with token specified in .env
bot.run(os.getenv("BOT_TOKEN"))
