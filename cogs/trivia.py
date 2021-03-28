import os
import discord
from discord.ext import commands
import sqlite3
import operator
import custom_functions
from discord.utils import get

"""
Handling points and leaderboard for users/events
"""

try:
    dbdir = os.getcwd() + '/database.sqlite'
    conn = custom_functions.SqliteConnection(dbdir).conn
except AttributeError as err:
    print("Failed to connect to sqlite table!", err)


async def has_permission(ctx):
    # Restrict command.
    role = discord.utils.get(ctx.guild.roles, name="Moderator")
    if role in ctx.author.roles:
        return True
    else:
        return False


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="points")
    # Permission check
    @commands.check(has_permission)
    async def points(self, ctx, user: discord.Member):
        cursor = conn.cursor()
        cursor.execute("SELECT points FROM trivia_points WHERE User = ?", (int(user.id),))
        points = cursor.fetchone()[0]

        await ctx.send(f'User {user.name}#{user.discriminator} currently has {points} points!')

    @points.error
    async def points_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("I could not find that member. Please try again.")

    @commands.command(name="ap")
    @commands.check(has_permission)
    async def add_points(self, ctx, user: discord.Member, amount):

        # Input validation.
        if not amount.isdigit():
            await ctx.send("Please input a numeric value for the number of points to add!")
            return

        # Lambda function to get the team role a user has.
        role = discord.utils.find(lambda r: r.name.endswith('Team') and (r.name.split(" ")[0] in ["Red", "Blue", "Pink", "Purple"]), user.roles)
        if role is None or role.name not in ["Red Team", "Blue Team", "Pink Team", "Purple Team"]:
            await ctx.send(f'{user.mention} has not joined a team yet. They must be part of a team to receive points!')
            return
        else:
            role_name = role.name[:-5]

        try:
            # Initialize cursor object.
            cursor = conn.cursor()

            # Get current points of selected user.
            cursor.execute("SELECT points FROM trivia_points WHERE User = ?", (int(user.id),))
            # This is a tuple object.
            current_points = cursor.fetchone()

            if current_points is None:
                # If the user is not found in the database, give them an entry.
                cursor.execute("INSERT INTO trivia_points (User, Points, Team) VALUES (?, ?, ?)",
                               (int(user.id), int(amount), role_name))

                await ctx.send(f'Adding {amount} points to {user.mention}. They now have {amount} points.')
                # Commit changes.
                conn.commit()
            else:
                # New points = current points + amount to add (math).
                new_points = int(current_points[0]) + int(amount)

                # Update the user's entry with the new amount of points.
                cursor.execute("UPDATE trivia_points SET points = ? WHERE User = ?", (new_points, user.id,))

                # Commit changes.
                conn.commit()

                # Send reply.
                await ctx.send(f'Adding {amount} points to {user.mention}. They now have {new_points} points.')
                await ctx.message.delete()
            # Close cursor.
            cursor.close()
        except sqlite3.Error as err:
            print(err)

    @add_points.error
    async def add_points_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.BadArgument):
            # If there is an error of bad argument, send an error message back.
            await ctx.send("I could not find that member. Please try again!")

    @commands.command(name="rpts")
    @commands.check(has_permission)
    async def remove_points(self, ctx, user: discord.Member, amount):
        if not amount.isdigit():
            await ctx.send("Please input a numeric value for the number of points to remove!")
            return
        try:
            cursor = conn.cursor()

            # Get current points of selected user.
            cursor.execute("SELECT points FROM trivia_points WHERE User = ?", (int(user.id),))
            # This is a tuple object.
            current_points = cursor.fetchone()

            if current_points is None:
                # If user isn't in the database, send an error message.
                await ctx.send(f'{user.mention} is not in the database! No points to remove.')
                # Commit changes.
                conn.commit()
            else:
                # Math (subtraction).
                new_points = int(current_points[0]) - int(amount)

                if new_points < 0:
                    await ctx.send(
                        f'Cannot remove {amount} points. {user.mention} only has {current_points[0]} points!')
                    return

                # Update table with new points.
                cursor.execute("UPDATE trivia_points SET points = ? WHERE User = ?", (new_points, user.id,))

                # Commit.
                conn.commit()

                # Send reply
                await ctx.send(f'Removing {amount} points from {user.mention}. They now have {new_points} points.')

            # Close cursor for now.
            cursor.close()
        except sqlite3.Error as err:
            print(err)

        await ctx.message.delete()

    @remove_points.error
    async def remove_points_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.BadArgument):
            # If there is an error of bad argument, send an error message back.
            await ctx.send("I could not find that member. Please try again!")

    # Show user leaderboard
    @commands.command(name="leaderboard")
    @commands.check(has_permission)
    async def leaderboard(self, ctx, *args):
        if args == ():
            await ctx.send("Please specify a valid command!")
            return

        print(args[0])

        if args[0] != "teams" and args[0] != "users" and args[0] != "final":
            await ctx.send("Please use a valid command!")
            return

        # Team points array
        team_pts = []
        cursor = conn.cursor()

        # For each team add their points to the array
        cursor.execute("SELECT SUM(Points) FROM trivia_points WHERE Team = ?", ("Blue",))
        team_pts.append(("Blue", cursor.fetchone()[0] or 0))

        cursor.execute("SELECT SUM(Points) FROM trivia_points WHERE Team = ?", ("Red",))
        team_pts.append(("Red", cursor.fetchone()[0] or 0))

        cursor.execute("SELECT SUM(Points) FROM trivia_points WHERE Team = ?", ("Pink",))
        team_pts.append(("Pink", cursor.fetchone()[0] or 0))

        cursor.execute("SELECT SUM(Points) FROM trivia_points WHERE Team = ?", ("Purple",))
        team_pts.append(("Purple", cursor.fetchone()[0] or 0))

        # Create top users list
        cursor.execute("SELECT User, Points, Team FROM trivia_points ORDER BY Points DESC LIMIT 15")
        top_users = list(cursor.fetchall())

        for item in range(len(top_users)):
            top_users[item] = list(top_users[item])

        print(top_users)
        # Reformat top users to be identified by team emoji
        for top_user in top_users:
            if top_user[2] == "Blue":
                top_user[2] = ":small_blue_diamond:"
            if top_user[2] == "Red":
                top_user[2] = ":small_red_triangle:"
            if top_user[2] == "Pink":
                top_user[2] = ":cherry_blossom:"
            if top_user[2] == "Purple":
                top_user[2] = ":woman_mage:"

        cursor.close()

        leaderboard_string = ""

        print(team_pts)
        team_pts.sort(key=operator.itemgetter(1), reverse=True)

        # Create leaderboard based on whether teams, users, or final is requested
        if args != () and args[0] == "teams":
            leaderboard_string += "__Team Points__"
            for i in team_pts:
                leaderboard_string += f'\n**{i[0]} Team**: {i[1]} Points'
                if i == team_pts[0]:
                    leaderboard_string += " :trophy:"

        if args != () and args[0] == "users":

            leaderboard_string += "\n\n\n __Top 15 Users__\n"

            for k in top_users:
                print(int(k[0]))
                member_object = self.bot.get_user(int(k[0]))
                print(member_object)
                if len(top_users) >= 1 and k == top_users[0]:
                    leaderboard_string += " :first_place:      "
                if len(top_users) >= 2 and k == top_users[1]:
                    leaderboard_string += " :second_place:      "
                if len(top_users) >= 3 and k == top_users[2]:
                    leaderboard_string += " :third_place:      "
                leaderboard_string += f'{k[2]} **{member_object.name + "#" + member_object.discriminator}**:' \
                                      f' {k[1]} Points\n'

        if args != () and args[0] == "final":

            leaderboard_string += "__Team Points__"
            for i in team_pts:
                leaderboard_string += f'\n**{i[0]} Team**: {i[1]} Points'
                if i == team_pts[0]:
                    leaderboard_string += " :trophy:"

            leaderboard_string += "\n\n\n __Top 15 Users__\n"

            for j in top_users:
                if len(top_users) >= 1 and j == top_users[0]:
                    leaderboard_string += " :first_place:      "
                if len(top_users) >= 2 and j == top_users[1]:
                    leaderboard_string += " :second_place:      "
                if len(top_users) >= 3 and j == top_users[2]:
                    leaderboard_string += " :third_place:      "
                leaderboard_string += f'{j[2]} **<@{j[0]}>**: {j[1]} Points\n'

        print(leaderboard_string)

        # Send the leaderboard
        await ctx.send(leaderboard_string)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Trivia(bot))
