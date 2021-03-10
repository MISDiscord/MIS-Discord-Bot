from discord.ext import commands
import numpy as np

"""
Rock paper scissors command. Quite inefficient and quickly put together; rewrite later.
"""


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rps")
    async def rps(self, ctx, *args):
        choices = ["rock", "paper", "scissors"]

        # Make sure the user chose a valid option.
        try:
            print(args[0])
            if args[0] not in choices:
                await ctx.send('Please choose either rock, paper, or scissors.')
        except IndexError:
            await ctx.send("Please choose either rock, paper, or scissors.")

        # Computer chooses a random option
        rand_int = np.random.randint(2)
        computer_choice = choices[rand_int]

        # Game logic (needs to be rewritten later)

        if args[0] == computer_choice:
            await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\nDraw.')
            return

        if args[0] == "rock":
            if computer_choice == "paper":
                await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\n:x: You lose!')
            else:
                await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\n:white_check_mark: You win!')

        if args[0] == "paper":
            if computer_choice == "scissors":
                await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\n:x: You lose!')
            else:
                await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\n:white_check_mark: You win!')

        if args[0] == "scissors":
            if computer_choice == "rock":
                await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\n:x: You lose!')
            else:
                await ctx.send(f'You chose {args[0]}. Computer chose {computer_choice}.\n:white_check_mark: You win!')


def setup(bot):
    bot.add_cog(Game(bot))
