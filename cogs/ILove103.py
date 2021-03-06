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

    @commands.group(name="λ΄μ ")
    async def scream(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @scream.command(name="μμ")
    @commands.guild_only()
    async def screamStart(self, ctx: Context):
        emojis = ["π΅", "π΄", "π₯", "β"]
        msg: Message = await ctx.send(
            embed=Embed(
                title="λ΄μ  μ€λΉ",
                description=f"{emojis[0]} λΈλ£¨ν\n\n\n{emojis[1]} λ λν\n\n{emojis[3]} μμ\n\n{emojis[3]} ν λκ°κΈ°",
            ).set_footer(text="300μ΄ μμ νμ μ νν΄μ£ΌμΈμ.\nπ₯ μ΄λͺ¨μ§λ μΈμ μμ±μλ§ μ¬μ©ν  μ μμ΅λλ€.")
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
                        title="λ΄μ  μ’λ£",
                        description="μκ° μ΄κ³Όλ‘ λ΄μ μ΄ μ’λ£λμμ΅λλ€.",
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
                            title="λ΄μ  μ€λΉ",
                            description=f"{emojis[0]} λΈλ£¨ν\n{blue}\n\n{emojis[1]} λ λν\n{red}",
                        ).set_footer(text="300μ΄ μμ νμ μ νν΄μ£ΌμΈμ.")
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
                            title="λ΄μ  μ€λΉ",
                            description=f"{emojis[0]} λΈλ£¨ν\n{blue}\n\n{emojis[1]} λ λν\n{red}",
                        ).set_footer(text="300μ΄ μμ νμ μ νν΄μ£ΌμΈμ.")
                    )
                elif r.emoji == emojis[2]:
                    if ctx.author != u:
                        continue
                    await msg.clear_reactions()
                    return await msg.edit(
                        embed=Embed(
                            title="λ΄μ  μ’λ£",
                            description=f"{u.mention} λμ μν΄ λ΄μ μ΄ μ’λ£λμμ΅λλ€.",
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
                            title="λ΄μ  μ€λΉ",
                            description=f"{emojis[0]} λΈλ£¨ν\n{blue}\n\n{emojis[1]} λ λν\n{red}",
                        ).set_footer(text="300μ΄ μμ νμ μ νν΄μ£ΌμΈμ.")
                    )
                if len(blueTeam) == 5 and len(redTeam) == 5:
                    break
        blue = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, blueTeam)))
        red = "\n".join(list(map(lambda x: self.bot.get_user(x).mention, redTeam)))
        await msg.clear_reactions()
        await msg.edit(
            embed=Embed(
                title="λ΄μ  μμ",
                description=f"{emojis[0]} λΈλ£¨ν\n{blue}\n\n{emojis[1]} λ λν\n{red}",
            ).set_footer(text=f"μΈμ μμ±μ : {ctx.author}")
        )
        self.queue.clear()
        self.queue["blue"] = blueTeam
        self.queue["red"] = redTeam
        self.queue["sessionCreator"] = str(ctx.author.id)

    @scream.command(name="μ’λ£")
    async def screamEnd(self, ctx: Context):
        teams = ["π΅", "π΄"]
        if len(self.queue) == 0:
            return await ctx.send("λ΄μ μ΄ μμλμ§ μμμ΅λλ€.")
        msg: Message = await ctx.send(
            embed=Embed(
                title="λ΄μ  κ²°κ³Ό",
                description=f"{teams[0]} λΈλ£¨νμ΄ μ΄κ²Όλμ?\n\n{teams[1]} λ λνμ΄ μ΄κ²Όλμ?",
            ).set_footer(
                text=f"μΈμ μ’λ£μ({self.bot.get_user(int(self.queue['sessionCreator']))})λ§ μ¬μ©ν  μ μμ΅λλ€."
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
                    title="λ΄μ  μ’λ£",
                    description="μκ° μ΄κ³Ό",
                    color=Color.red(),
                )
            )
        else:
            if r.emoji == teams[0]:
                await msg.edit(
                    embed=Embed(
                        title="λ΄μ  κ²°κ³Ό",
                        description=f"{teams[0]} λΈλ£¨νμ΄ μ΄κ²Όμ΅λλ€!",
                        color=Color.blue(),
                    )
                )
            elif r.emoji == teams[1]:
                await msg.edit(
                    embed=Embed(
                        title="λ΄μ  κ²°κ³Ό",
                        description=f"{teams[1]} λ λνμ΄ μ΄κ²Όμ΅λλ€!",
                        color=Color.red(),
                    )
                )


def setup(bot: HeeKyung):
    bot.add_cog(ILove103(bot))
