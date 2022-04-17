from discord import Message
from discord.ext import commands
from discord.ext.commands.context import Context

from __main__ import HeeKyung

import json
import pytz
from datetime import datetime

with open("./database/managers.json", "r", encoding="utf8") as f:
    managers = json.load(f)


class Core(commands.Cog):
    def __init__(self, bot: HeeKyung):
        self.bot = bot
        self.meetings = {"meetingWhether": False, "channel": int(), "messages": []}

    @commands.group(name="회의")
    async def meeting(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @meeting.command(name="시작")
    async def meetingStart(self, ctx: Context):
        if self.meetings["meetingWhether"]:
            return await ctx.reply("회의가 이미 진행중입니다.")
        self.meetings["meetingWhether"] = True
        self.meetings["channel"] = int(ctx.channel.id)
        return await ctx.reply("회의가 시작되었습니다.")

    @meeting.command(name="종료")
    async def meetingEnd(self, ctx: Context):
        if not self.meetings["meetingWhether"]:
            return await ctx.reply("회의가 진행중이 아닙니다.")
        self.meetings["meetingWhether"] = False
        self.meetings["channel"] = int()
        with open(
            f'./database/meetings/{datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime("%Y%m%d%H%M")}.txt',
            "w",
            encoding="utf8",
        ) as meeting:
            meeting.write("\n".join(self.meetings["messages"]))
        return await ctx.reply("회의가 종료되었습니다.")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if message.content == "!회의 시작":
            return
        if self.meetings["meetingWhether"]:
            if message.channel.id == self.meetings["channel"]:
                self.meetings["messages"].append(
                    f"{message.author.name if managers.get(str(message.author.id)) is None else managers[str(message.author.id)]}"
                    f" - {datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%m-%d %H:%M')} - {message.content}"
                )


def setup(bot: HeeKyung):
    bot.add_cog(Core(bot))
