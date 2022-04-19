from discord.ext import commands
from discord import Message, Embed, Color
from discord.ext.commands.context import Context

from __main__ import HeeKyung


class ILove103(commands.Cog):
    def __init__(self, bot: HeeKyung):
        self.bot = bot
        self.queue = {
            "blue": [],
            "red": [],
            "sessionCreator": str(),
        }

    @commands.group(name="내전")
    async def scream(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @scream.command(name="시작")
    @commands.guild_only()
    async def screamStart(self, ctx: Context):
        emojis = ["🔵", "🔴", "💥", "⛔"]
        msg: Message = await ctx.send(
            embed=Embed(
                title="내전 준비",
                description=f"{emojis[0]} 블루팀\n\n\n{emojis[1]} 레드팀\n\n{emojis[3]} 시작\n\n{emojis[3]} 팀 나가기",
            ).set_footer(text="300초 안에 팀을 선택해주세요.\n💥 이모지는 세션 생성자만 사용할 수 있습니다.")
        )
        blueTeam = []
        redTeam = []
        for _ in emojis:
            await msg.add_reaction(_)
        while True:
            try:
                r, u = await self.bot.wait_for(
                    "reaction_add",
                    timeout=300,
                    check=lambda reaction, user: str(reaction.emoji) in emojis,
                )
            except TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(
                    embed=Embed(
                        title="내전 종료",
                        description="시간 초과로 내전이 종료되었습니다.",
                    )
                )
            else:
                if u == self.bot.user:
                    continue
                if r.emoji == emojis[0]:
                    if u.id in blueTeam:
                        continue
                    if u.id in redTeam:
                        redTeam.remove(u.id)
                    blueTeam.append(u.id)
                    blue = "\n".join(
                        list(map(lambda x: self.bot.get_user(x).mention, blueTeam))
                    )
                    red = "\n".join(
                        list(map(lambda x: self.bot.get_user(x).mention, redTeam))
                    )
                    await msg.edit(
                        embed=Embed(
                            title="내전 준비",
                            description=f"{emojis[0]} 블루팀\n{blue}\n\n{emojis[1]} 레드팀\n{red}",
                        ).set_footer(text="300초 안에 팀을 선택해주세요.")
                    )
                elif r.emoji == emojis[1]:
                    if u.id in redTeam:
                        continue
                    if u.id in blueTeam:
                        blueTeam.remove(u.id)
                    redTeam.append(u.id)
                    blue = "\n".join(
                        list(map(lambda x: self.bot.get_user(x).mention, blueTeam))
                    )
                    red = "\n".join(
                        list(map(lambda x: self.bot.get_user(x).mention, redTeam))
                    )
                    await msg.edit(
                        embed=Embed(
                            title="내전 준비",
                            description=f"{emojis[0]} 블루팀\n{blue}\n\n{emojis[1]} 레드팀\n{red}",
                        ).set_footer(text="300초 안에 팀을 선택해주세요.")
                    )
                elif r.emoji == emojis[2]:
                    if ctx.author != u:
                        continue
                    await msg.clear_reactions()
                    return await msg.edit(
                        embed=Embed(
                            title="내전 종료",
                            description=f"{u.mention} 님에 의해 내전이 종료되었습니다.",
                        )
                    )
                elif r.emoji == emojis[3]:
                    try:
                        blueTeam.remove(u.id)
                    except ValueError:
                        pass
                    try:
                        redTeam.remove(u.id)
                    except ValueError:
                        pass
                    blue = "\n".join(
                        list(map(lambda x: self.bot.get_user(x).mention, blueTeam))
                    )
                    red = "\n".join(
                        list(map(lambda x: self.bot.get_user(x).mention, redTeam))
                    )
                    await msg.edit(
                        embed=Embed(
                            title="내전 준비",
                            description=f"{emojis[0]} 블루팀\n{blue}\n\n{emojis[1]} 레드팀\n{red}",
                        ).set_footer(text="300초 안에 팀을 선택해주세요.")
                    )
                if len(blueTeam) == 5 and len(redTeam) == 5:
                    break
        blue = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, blueTeam)))
        red = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, redTeam)))
        await msg.clear_reactions()
        await msg.edit(
            embed=Embed(
                title="내전 시작",
                description=f"{emojis[0]} 블루팀\n{blue}\n\n{emojis[1]} 레드팀\n{red}",
            ).set_footer(text=f"세션 생성자 : {ctx.author}")
        )
        self.queue.clear()
        self.queue["blue"] = blueTeam
        self.queue["red"] = redTeam
        self.queue["sessionCreator"] = str(ctx.author.id)

    @scream.command(name="종료")
    async def screamEnd(self, ctx: Context):
        teams = ["🔵", "🔴"]
        if len(self.queue) == 0:
            return await ctx.send("내전이 시작되지 않았습니다.")
        msg: Message = await ctx.send(
            embed=Embed(
                title="내전 결과",
                description=f"{teams[0]} 블루팀이 이겼나요?\n\n{teams[1]} 레드팀이 이겼나요?",
            ).set_footer(
                text=f"세션 종료자({self.bot.get_user(int(self.queue['sessionCreator']))})만 사용할 수 있습니다."
            )
        )
        for _ in teams:
            await msg.add_reaction(_)
        try:
            r, u = await self.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: str(reaction.emoji) in teams
                and user == ctx.author,
            )
        except TimeoutError:
            return await msg.edit(
                embed=Embed(
                    title="내전 종료",
                    description="시간 초과",
                    color=Color.red(),
                )
            )
        else:
            if r.emoji == teams[0]:
                await msg.edit(
                    embed=Embed(
                        title="내전 결과",
                        description=f"{teams[0]} 블루팀이 이겼습니다!",
                        color=Color.blue(),
                    )
                )
            elif r.emoji == teams[1]:
                await msg.edit(
                    embed=Embed(
                        title="내전 결과",
                        description=f"{teams[1]} 레드팀이 이겼습니다!",
                        color=Color.red(),
                    )
                )


def setup(bot: HeeKyung):
    bot.add_cog(ILove103(bot))
