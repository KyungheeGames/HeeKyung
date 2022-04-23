import aiohttp
from discord.ext import commands
from discord import Message, Member, Embed, File
from discord.ext.commands.context import Context

from __main__ import HeeKyung

import os
import json
import pytz
from datetime import datetime
from asyncio import TimeoutError
from aiohttp import ClientSession


def isGameDeveloper():
    with open("./database/managers.json", "r", encoding="utf8") as f:
        managers = json.load(f)
    return commands.check(lambda ctx: managers.get(str(ctx.author.id)))


class Core(commands.Cog):
    def __init__(self, bot: HeeKyung):
        self.bot = bot
        self.meetings = {"meetingWhether": False, "channel": int(), "messages": []}

    @commands.group(name="회의")
    @isGameDeveloper()
    async def meeting(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @meeting.command(name="시작")
    @commands.guild_only()
    async def meetingStart(self, ctx: Context):
        if self.meetings["meetingWhether"]:
            return await ctx.reply("회의가 이미 진행중입니다.")
        self.meetings["meetingWhether"] = True
        self.meetings["channel"] = int(ctx.channel.id)
        return await ctx.reply("회의가 시작되었습니다.")

    @meeting.command(name="종료")
    @commands.guild_only()
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
        self.meetings["messages"] = []
        return await ctx.reply("회의가 종료되었습니다.")

    @commands.command(name="회의록")
    @isGameDeveloper()
    async def exportMeeting(self, ctx: Context):
        meetings = sorted(os.listdir("./database/meetings"), reverse=True)
        if len(meetings) == 0:
            return await ctx.reply("회의록이 없습니다.")
        meetingLetters = []
        for meeting in meetings:
            with open(f"./database/meetings/{meeting}", "r", encoding="utf8") as f:
                meetingLetters.append(len(f.read()))
        numberEmojis = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
        ]
        embed = Embed(
            title="회의록 목록",
            description="\n".join(
                [
                    f"{numberEmojis[meetings.index(_)]} - {_[0:4]}.{_[4:6]}.{_[6:8]} {_[8:10]}:{_[10:12]} ( {meetingLetters[meetings.index(_)]}자 )"
                    for _ in meetings[:5]
                ]
            ),
        ).set_footer(text="아래 버튼을 눌러 회의록을 다운로드하세요. (60초)")
        msg: Message = await ctx.reply(embed=embed)
        for emoji in numberEmojis[: len(meetings)]:
            await msg.add_reaction(emoji)
        try:
            react = await self.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: user == ctx.author
                and str(reaction.emoji) in numberEmojis,
                timeout=60,
            )
        except TimeoutError:
            return await msg.clear_reactions()
        await msg.delete()
        await ctx.send(
            file=File(
                f"./database/meetings/{meetings[numberEmojis.index(str(react[0].emoji))]}",
                filename=meetings[numberEmojis.index(str(react[0].emoji))],
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if message.content == "!회의 시작":
            return
        if self.meetings["meetingWhether"]:
            if message.channel.id == self.meetings["channel"]:
                with open("./database/managers.json", "r", encoding="utf8") as f:
                    managers = json.load(f)
                self.meetings["messages"].append(
                    f"{message.author.name if managers.get(str(message.author.id)) is None else managers[str(message.author.id)]}"
                    f" - {datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%m-%d %H:%M')} - {message.content}"
                )

    @commands.group(name="관리자")
    async def admin(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @admin.command(name="추가")
    async def adminAdd(self, ctx: Context, user: Member, *, name: str):
        with open("./database/managers.json", "r", encoding="utf8") as f:
            managers = json.load(f)
        if managers.get(str(user.id)) is None:
            managers[str(user.id)] = name
            with open("./database/managers.json", "w", encoding="utf8") as f:
                json.dump(managers, f, ensure_ascii=False, indent=4)
            return await ctx.reply(f"{user} 님의 관리자명이 `{name}` 으로 변경되었습니다.")
        return await ctx.reply(f"{user}({managers[str(user.id)]}) 님은 이미 관리자입니다.")

    @admin.command(name="삭제")
    async def adminDelete(self, ctx: Context, user: Member):
        with open("./database/managers.json", "r", encoding="utf8") as f:
            managers = json.load(f)
        if managers.get(str(user.id)) is not None:
            del managers[str(user.id)]
            with open("./database/managers.json", "w", encoding="utf8") as f:
                json.dump(managers, f, ensure_ascii=False, indent=4)
            return await ctx.reply(f"{user} 님의 관리자명이 삭제되었습니다.")
        return await ctx.reply(f"{user} 님은 관리자가 아닙니다.")

    @admin.command(name="변경")
    async def adminChange(self, ctx: Context, user: Member, *, name: str):
        with open("./database/managers.json", "r", encoding="utf8") as f:
            managers = json.load(f)
        if managers.get(str(user.id)) is not None:
            managers[str(user.id)] = name
            with open("./database/managers.json", "w", encoding="utf8") as f:
                json.dump(managers, f, ensure_ascii=False, indent=4)
            return await ctx.reply(f"{user} 님의 관리자명이 `{name}` 으로 변경되었습니다.")
        return await ctx.reply(f"{user} 님은 관리자가 아닙니다.")

    @admin.command(name="목록")
    async def adminList(self, ctx: Context):
        with open("./database/managers.json", "r", encoding="utf8") as f:
            managers = json.load(f)
        if len(managers) == 0:
            return await ctx.reply("관리자가 없습니다.")
        return await ctx.reply(
            embed=Embed(
                title="관리자 목록",
                description="\n".join(
                    [
                        f"{ctx.guild.get_member(int(_)).mention} : {managers[_]}"
                        for _ in managers
                    ]
                ),
            )
        )

    @commands.command(name="대본")
    async def script(self, ctx: Context, _id: int):
        async with ClientSession() as session:
            async with session.get(f"http://localhost:8000/api/script/{_id}") as resp:
                response = await resp.json()
        koreanScripts = "\n".join(response['korean'])
        englishScripts = "\n".join(response['english'])
        msg: Message = await ctx.reply(embed=Embed(title=response['name'], description=f'**한국어**\n```{koreanScripts}```\n**영어**\n```{englishScripts}```'))
        await msg.add_reaction("📝")
        try:
            await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and str(reaction.emoji) == "📝", timeout=60)
        except TimeoutError:
            await msg.clear_reactions()
        else:
            await msg.clear_reactions()
            msg1: Message = await ctx.send("대본 txt 파일을 보내주세요!")
            try:
                res: Message = await self.bot.wait_for("message", check=lambda message: ctx.author == message.author and message.channel == ctx.channel, timeout=60)
            except TimeoutError:
                await msg1.delete()
            else:
                if len(res.attachments) == 0:
                    return await ctx.send("보내주신 메시지엔 파일이 없는거 같아요 ㅠ")
                async with aiohttp.ClientSession() as session:
                    async with session.post(res.attachments[0].url) as resp:
                        response = await resp.read()
                fileRead = response.decode("utf8")
                if len(fileRead.splitlines()) % 2 != 0:
                    return await ctx.send("한국어, 영어 버전의 대본을 보내주셔야하는데 정확하지 않은거 같아요 ㅠ")
                twoLines = fileRead.splitlines()[_ * 2:_ * 2 + 2]
                for _ in range(len(fileRead.splitlines()) // 2):
                    twoLines.append()
                koreanScripts = [x[0] for x in twoLines]
                englishScripts = [y[1] for y in twoLines]
                response['korean'] = koreanScripts
                response['english'] = englishScripts
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"http://localhost:8000/api/script/{_id}", json=response) as resp:
                        await resp.read()
                


def setup(bot: HeeKyung):
    bot.add_cog(Core(bot))
