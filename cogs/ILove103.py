from discord.ext import commands
from discord import Message, Embed
from discord.ext.commands.context import Context

from __main__ import HeeKyung


class ILove103(commands.Cog):
    def __init__(self, bot: HeeKyung):
        self.bot = bot

    @commands.group(name="내전")
    async def scream(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @scream.command(name="시작")
    @commands.guild_only()
    async def screamStart(self, ctx: Context):
        teams = ["🔵", "🔴", "💥"]
        msg: Message = await ctx.send(
            embed=Embed(
                title="내전 시작", description=f"{teams[0]} 블루팀\n\n\n{teams[1]} 레드팀"
            ).set_footer(text="300초 안에 팀을 선택해주세요.\n💥 이모지는 세션 생성자만 사용할 수 있습니다.")
        )
        blueTeam = []
        redTeam = []
        for _ in teams:
            await msg.add_reaction(_)
        while True:
            try:
                r, u = await self.bot.wait_for(
                    "reaction_add",
                    timeout=300,
                    check=lambda reaction, user: str(reaction.emoji) in teams,
                )
            except TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(
                    embed=Embed(
                        title="내전 시작",
                        description="시간 초과로 내전이 종료되었습니다.",
                    )
                )
            else:
                if u == self.bot.user:
                    continue
                if r.emoji == teams[0]:
                    if u.id in blueTeam:
                        continue
                    if u.id in redTeam:
                        redTeam.remove(u.id)
                    blueTeam.append(u.id)
                    blue = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, blueTeam)))
                    red = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, redTeam)))
                    await msg.edit(
                        embed=Embed(
                            title="내전 시작",
                            description=f"{teams[0]} 블루팀\n{blue}\n\n{teams[1]} 레드팀\n{red}",
                        ).set_footer(text="300초 안에 팀을 선택해주세요.")
                    )
                elif r.emoji == teams[1]:
                    if u.id in redTeam:
                        continue
                    if u.id in blueTeam:
                        blueTeam.remove(u.id)
                    redTeam.append(u.id)
                    blue = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, blueTeam)))
                    red = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, redTeam)))
                    await msg.edit(
                        embed=Embed(
                            title="내전 시작",
                            description=f"{teams[0]} 블루팀\n{blue}\n\n{teams[1]} 레드팀\n{red}",
                        ).set_footer(text="300초 안에 팀을 선택해주세요.")
                    )
                elif r.emoji == teams[2]:
                    if ctx.author != u:
                        continue
                    await msg.clear_reactions()
                    return await msg.edit(
                        embed=Embed(
                            title="내전 종료",
                            description=f"{u.mention} 님에 의해 내전이 종료되었습니다.",
                        )
                    )
                if len(blueTeam) == 5 and len(redTeam) == 5:
                    break
        await ctx.send("총 10명 참가로 자동으로 시작하겠습니다.")


def setup(bot: HeeKyung):
    bot.add_cog(ILove103(bot))
