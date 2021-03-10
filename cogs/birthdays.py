from discord.ext import commands
import discord
import datetime
import openpyxl

"""
Commands for keeping track of user's birthdays.
"""

SPREADSHEET_PATH = "birthdays.xlsx"


# Converts a month name to corresponding number
def month_to_number(month):
    try:
        datetime_object = datetime.datetime.strptime(month, "%B").month
        return str(datetime_object)
    except ValueError:
        return None


# Checks if provided day actually exists
def validate_birthday(month, day):
    months = {"January": 31, "February": 29, "March": 31, "April": 30, "May": 31, "June": 30, "July": 31, "August": 31,
              "September": 30, "October": 31, "November": 30, "December": 31}
    if months[month] >= int(day) >= 1:
        return True
    else:
        return None


class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setbirthday")
    async def set_birthday(self, ctx, month, day):

        # Make sure user is in a DM
        if str(ctx.channel).startswith("Direct Message"):

            # Validate birthday entry
            if validate_birthday(month.lower().capitalize(), day):
                pass
            else:
                await ctx.send("Invalid date! Please set your birthday with the full month name,"
                               " along with the day you were born.\nExample: `/setbirthday May 1`")
                return

            if month_to_number(month) is not None and len(day) <= 2 and int(day) <= 31:

                # Format of excel entry
                entry = [str(ctx.author.id), month_to_number(month), str(day),
                         f"{ctx.author.name}#{ctx.author.discriminator}"]
                print(entry)

                # Open spreadsheet
                wb = openpyxl.load_workbook(SPREADSHEET_PATH)
                ws = wb.active

                for row in ws.iter_rows(values_only=True):
                    # If the user already has an entry, prevent from adding another. Message me directly if they need
                    # it changed
                    if row[0] == str(ctx.author.id):
                        user_birth_month = datetime.datetime.strptime(str(row[1]), "%m").strftime("%B")
                        await ctx.send(
                            f"You have already set your birthday as {user_birth_month.lower().capitalize()} {row[2]}!"
                            f" If you believe there has been a mistake, "
                            f"please contact <@222479899808628736> for assistance in changing it.")
                        return

                # Append, save, and close the file
                ws.append(entry)
                wb.save(SPREADSHEET_PATH)
                wb.close()

                # Confirmation message
                await ctx.send(f"Your birthday has been set to {month.capitalize()} {day}!")
            else:
                await ctx.send("Invalid format! Please set your birthday with the full month name,"
                               " along with the day you were born.\nExample: `/setbirthday May 1`")
                return

    # Send error message if something went wrong
    @set_birthday.error
    async def set_birthday_error(self, ctx, err):
        await ctx.send("Error! Please set your birthday with the full month name,"
                       " along with the day you were born.\nExample: `/setbirthday May 1`")


def setup(bot):
    bot.add_cog(Birthdays(bot))
