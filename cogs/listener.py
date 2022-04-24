from discord import Game, Status
from discord.ext import commands
from discord.ext.commands.context import Context

from __main__ import HeeKyung


class Listener(commands.Cog):
    def __init__(self, bot: HeeKyung):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CheckFailure):
            if str(ctx.command) == "회의":
                return await ctx.reply("해당 명령어는 KyungheeGames 개발자들만 사용할 수 있습니다.")
        self.bot.logger.error(error)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(f"Logged in as {self.bot.user}")
        await self.bot.change_presence(activity=Game(name="!help"), status=Status.online)


def setup(bot: HeeKyung):
    bot.add_cog(Listener(bot))
