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

# Load env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Set discord intents
intents = discord.Intents.default()
intents.members = True
intents.invites = True
intents.messages = True

# Bot user (client)
bot = commands.Bot(intents=intents, command_prefix=os.getenv("BOT_PREFIX"), help_command=None)

join_and_leave_logs_channel_id = 792161507005038612
welcome_channel_id = 798686136691458088

# Load cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        print(f'Loaded {filename[:-3]} cog!')
        bot.load_extension(f'cogs.{filename[:-3]}')

# Connect to sqlite3 database
try:
    dbdir = os.getcwd() + '/database.sqlite'
    print(dbdir)
    conn = sqlite3.connect(dbdir)  # Connect to database
    print("Connected!")
except sqlite3.Error as error:
    print("Failed to connect to sqlite table", error)

server_invites = {}


@bot.event
async def on_ready():
    for guild in bot.guilds:
        server_invites[guild.id] = await guild.invites()
    print(f'Logged in as: {bot.user.name}#{bot.user.discriminator} ({bot.user.id})\n')


@bot.event
async def on_message(ctx):
    # Bots can't trigger events
    if ctx.author.bot:
        return

    # Process commands if message starts with specified prefix
    await bot.process_commands(ctx)
    print(ctx.content)

    if ctx.channel.id == 817326358107389963:
        if ctx.content.lower() == "elephant":
            member_role_id = 802838038094151692
            role = discord.utils.get(ctx.guild.roles, id=member_role_id)
            await ctx.author.add_roles(role)
            await ctx.channel.purge(limit=1)

    if not ctx.content.startswith(bot.command_prefix):

        # Every time a user talks in chat, give them a random amount of experience points ranging from 1-10
        xp = random.randint(1, 10)
        cursor = conn.cursor()
        cursor.execute(f'SELECT xp FROM message_levels WHERE user_id = {ctx.author.id}')
        result = cursor.fetchall()
        if len(result) == 0:
            print("User is not in database. Add them!")
            cursor.execute(f'INSERT INTO message_levels VALUES ({ctx.author.id}, {xp})')
            conn.commit()
        else:
            newXP = result[0][0] + xp
            print(f'{ctx.author.name} got {xp} XP points. They now have {newXP} experience.')
            cursor.execute(f'UPDATE message_levels SET xp = {newXP} WHERE user_id = {ctx.author.id}')
            conn.commit()


@bot.event
async def on_member_join(member):

    welcome_verification_message = f"Welcome {member.mention} to Mental health of Reddit! " \
                                   f"Please find the safe word located in <#701102417512628286> and type it in this" \
                                   f" channel to gain access to the rest of the server."

    verify_channel_id = 817326358107389963

    await bot.get_channel(verify_channel_id).send(welcome_verification_message)

    # Find invites before and after join to see which one was used
    invites_before_join = server_invites[int(member.guild.id)]
    invites_after_join = await member.guild.invites()

    for invite in invites_before_join:

        # Find which invite has an extra use and use its data to format the embed
        if invite.uses < custom_functions.find_invite_by_code(invites_after_join, invite.code).uses:
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
            time = divmod((datetime.datetime.now() - bot.get_user(member.id).created_at).total_seconds(), 1)[0]
            embed.set_footer(text=f'Account Age: {custom_functions.seconds_to_age(int(time))}')
            await bot.get_channel(join_and_leave_logs_channel_id).send(embed=embed)

            # Update server invites
            server_invites[member.guild.id] = invites_after_join


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


@bot.event
async def on_reaction_add(reaction, user):
    print(reaction, user)
    emojis = [
                "<:Eggito:821374260831453184>",
                "<:EggBurto:821380416581009438>",
                "<:McEgg:821380416669351936>",
                "<:Eggie:821380416987725864>"
            ]

    # Regex search for emoji in string
    search = re.search('(<:\w*:\d*>)', reaction.message.content)

    if reaction.message.author.bot and search is not None and str(reaction.emoji) == str(search.group(0)):
        # Open file, get data, then close connection
        scoreboard_file = open('eggs.json', 'r')
        data = json.load(scoreboard_file)
        scoreboard_file.close()

        # Update data
        if str(user.id) in data:
            data[str(user.id)] += 1
        else:
            data[str(user.id)] = 1

        # Save data and close connection
        f = open('eggs.json', 'w')
        json.dump(data, f)
        f.close()

        # Delete message
        await reaction.message.delete()


# Run the bot with token specified in .env
bot.run(os.getenv("BOT_TOKEN"))
