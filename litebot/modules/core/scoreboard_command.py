import json
import os
from discord.ext import commands

from litebot.core import Cog
from litebot.utils.misc import scoreboard_image
from litebot.utils import embeds


class ScoreboardCommand(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(os.getcwd(), "litebot", "utils", "assets", "scoreboards.json")) as f:
            self.scoreboards = json.load(f)

    @commands.command(name="scoreboard", aliases=["sb"])
    async def _scoreboard(self, ctx: commands.Context, objective_name: str, option: str = None) -> None:
        """
        This command lets you view the scoreboard for an ingame objective.
        The command will generate an image that looks similar to the sidebar in game.
        `option` can be two separate options:
        `all` will show the values for all scoreboard entities as opposed to just the whitelisted players.
        `board` will show only the values that would appear on the actual ingame sidebar.
        """
        server = self.bot.servers.get_first_instance()

        if option and option.upper() == "ALL":
            player_list = server.send_command("scoreboard players list")
        else:
            player_list = server.send_command("whitelist list")

        if objective_name in self.scoreboards:
            objective_name = self.scoreboards[objective_name]

        scores = {}
        for player in player_list.replace(",", "").split(" "):
            objective = server.send_command(f"scoreboard players get {player} {objective_name}")

            if "none" not in objective:
                player_name = objective.split()[0]
                objectve_value = int(objective.split()[2])

                scores.update({player_name: objectve_value})

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if option and option.upper() == "BOARD":
            sorted_scores = sorted_scores[:15]

        image = scoreboard_image(sorted_scores, objective_name)
        await ctx.send(file=image)

    @_scoreboard.error
    async def on_scoreboard_error(self, ctx: commands.Context, err: commands.CommandInvokeError) -> None:
        """
        Handles any errors that might occur within the scoreboard command
        :param ctx: The context that the command was invoked in
        :type ctx: commands.Context
        :param err: The error that was raised
        :type err: commands.CommandInvokeError
        """

        if isinstance(err.original, ValueError):
            await ctx.send(embed=embeds.ErrorEmbed("That scoreboard does not exist"))
        elif isinstance(err.original, UnboundLocalError):
            await ctx.send(embed=embeds.ErrorEmbed("That scoreboard has no values"))