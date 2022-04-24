from discord.ext import commands
from discord import Message, Member, Embed, File
from discord.ext.commands.context import Context

from __main__ import HeeKyung

import os
import json
import pytz
from typing import List
from datetime import datetime
from pydub import AudioSegment
from asyncio import TimeoutError
from EZPaginator import Paginator


def isGameDeveloper():
    with open("./database/managers.json", "r", encoding="utf8") as f:
        managers = json.load(f)
    return commands.check(lambda ctx: managers.get(str(ctx.author.id)))


class Core(commands.Cog):
    def __init__(self, bot: HeeKyung):
        self.bot = bot
        self.meetings = {"meetingWhether": False, "channel": int(), "messages": []}

    @commands.command(name="도움말", aliases=["도움", "help"])
    async def help(self, ctx: Context):
        embeds: List[Embed] = list(map(lambda x: x.set_footer(icon_url=ctx.author.avatar_url), [
            Embed(
                title="희경 도움말",
                description="**Page 1.** ILove103\n**Page 2.** KyungheeGames 개발자 도움말"
            ),
            Embed(
                title="ILove103 도움말",
                description="1학년 3반을 위한 커맨드입니다."
            ).add_field(
                name="!내전 시작",
                value="롤 5 vs 5 내전을 시작합니다.",
                inline=False,
            ).add_field(
                name="!내전 종료",
                value="롤 5 vs 5 내전을 종료합니다.",
                inline=False,
            ),
            Embed(
                title="KyungheeGames 개발자 도움말",
                description="게임 개발자만 사용할 수 있습니다."
            ).add_field(
                name="!회의 시작",
                value="회의를 시작합니다."
            ).add_field(
                name="!회의 종료",
                value="회의를 종료합니다."
            ).add_field(
                name="!회의록",
                value="이전 회의록을 불러옵니다."
            ).add_field(
                name="!관리자 추가 @멘션",
                value="관리자를 추가합니다."
            ).add_field(
                name="!관리자 삭제 @멘션",
                value="관리자 권한을 박탈합니다."
            ).add_field(
                name="!관리자 변경 @멘션 이름",
                value="관리자의 이름을 변경합니다."
            ).add_field(
                name="!관리자 목록",
                value="관리자 목록을 불러옵니다."
            ).add_field(
                name="!오디오변환",
                value="파일을 같이 보내주시면 mp3 파일을 ogg 파일로 변환해드려요!"
            )
        ]))
        msg: Message = await ctx.send(embed=embeds[0])
        await Paginator(bot=self.bot, message=msg, embeds=embeds, use_extend=True).start()

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
    @isGameDeveloper()
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

    @commands.command(name="오디오변환")
    @isGameDeveloper()
    async def audioConvert(self, ctx: Context):
        if len(ctx.message.attachments) == 0:
            return await ctx.reply("첨부된 파일이 없습니다.")
        if ctx.message.attachments[0].filename.split(".")[-1] not in ["mp3", "wav"]:
            return await ctx.reply("오디오 파일이 아닙니다.")
        with open(
            f"./database/audioDatas/input/{ctx.message.attachments[0].filename}", "wb"
        ) as fp:
            await ctx.message.attachments[0].save(fp)
        songFile = AudioSegment.from_mp3(
            f"./database/audioDatas/input/{ctx.message.attachments[0].filename}"
        )
        songFile.export(
            f'./database/audioDatas/output/{ctx.message.attachments[0].filename.split(".")[0]}.ogg',
            format="ogg",
        )
        await ctx.reply(
            f"{ctx.message.attachments[0].filename} 파일이 오디오로 변환되었습니다.",
            file=File(
                f'./database/audioDatas/output/{ctx.message.attachments[0].filename.split(".")[0]}.ogg'
            ),
        )
        os.remove(f"./database/audioDatas/input/{ctx.message.attachments[0].filename}")
        os.remove(
            f'./database/audioDatas/output/{ctx.message.attachments[0].filename.split(".")[0]}.ogg'
        )


def setup(bot: HeeKyung):
    bot.add_cog(Core(bot))
