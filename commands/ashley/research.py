import discord
import json

from asyncio import sleep, TimeoutError
from discord.ext import commands
from resources.check import check_it
from resources.db import Database

with open("data/research.json") as research:
    research = json.loads(research.read())

_ANSWERS, _SCORE, _RESEARCH = dict(), dict(), research["satisfaction"]
_ANSWERS_2, _SCORE_2, _RESEARCH_2 = dict(), dict(), research["feedback"]


class RegisterClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @staticmethod
    def verify_answer(text):
        l_text, words = [word for word in text.split() if 1 < len(word) < 21], list()
        score = len(l_text) * 50
        for p in l_text:
            if p not in words:
                if l_text.count(p) >= 5:
                    score -= l_text.count(p) * 50
                words.append(p)
        return 0 if score < 0 else score

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='research', aliases=['pesquisa', "p"])
    async def research(self, ctx):
        """Sistema de Pesquisa da Ashley"""
        if ctx.invoked_subcommand is None:
            self.status()
            top = discord.Embed(color=self.color)
            top.add_field(name="Research Commands:",
                          value=f"{self.st[67]} `p s` Faça uma pesquisa de satisfação sobre a ASHLEY!\n"
                                f"{self.st[67]} `p f` Faça uma pesquisa de feedback sobre a ASHLEY!")
            top.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            top.set_thumbnail(url=self.bot.user.avatar_url)
            top.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=top)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @research.command(name='satisfaction', aliases=['s'])
    async def _satisfaction(self, ctx):
        """Sistema de Pesquisa da Ashley"""
        query = {"_id": 0, "user_id": 1, "research": 1}
        data = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        if "satisfaction" in data["research"].keys():
            try:
                return await ctx.author.send(_RESEARCH["-4"])
            except discord.errors.Forbidden:
                return await ctx.send(_RESEARCH["-4"])

        def check(m):
            if m.author.id == ctx.author.id:
                if 100 <= len(m.content) <= 450:
                    return True
            return False

        await ctx.send(_RESEARCH["0"], delete_after=5.0)
        _ANSWERS[ctx.author.id] = dict()
        _SCORE[ctx.author.id] = 0

        # ----------------------------------------------------------------------------------
        try:
            await ctx.author.send(_RESEARCH["1"] + _RESEARCH["-3"])
        except discord.errors.Forbidden:
            return await ctx.send("<:negate:721581573396496464>│`Desculpe, a pesquisa precisa ser feita no privado!`")
        try:
            _ANSWERS[ctx.author.id]["1"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["2"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["2"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["3"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["3"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["4"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["4"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["5"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["5"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["6"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["6"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["7"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["7"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["8"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["8"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["9"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["9"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["10"] + _RESEARCH["-3"])
        try:
            _ANSWERS[ctx.author.id]["10"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH["-1"])

        for k in _ANSWERS[ctx.author.id].keys():
            _SCORE[ctx.author.id] += self.verify_answer(_ANSWERS[ctx.author.id][k].content)

        desc = f"`Pesquisa de:` **{ctx.author}**\n`ID:` **{ctx.author.id}**\n`Score:` **{_SCORE[ctx.author.id]}**"
        embed = discord.Embed(colour=self.color, description=desc)
        for k in _ANSWERS[ctx.author.id].keys():
            embed.add_field(name=_RESEARCH[k], value=f"**{_ANSWERS[ctx.author.id][k].content}**", inline=False)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        canal = self.bot.get_channel(839593358895743016)
        extra = ""
        if _SCORE[ctx.author.id] > 5000:
            await canal.send(embed=embed)
            cl = await self.bot.db.cd("users")
            query = {"$set": {"research.satisfaction": True}, "$inc": {"inventory.blessed_enchant_skill": 1}}
            await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)
            extra += "\n`VOCÊ GANHOU` **1 BLESSED ENCHANT SKILL** `OLHE O SEU INVENTARIO!`"
        else:
            extra += "\n`SEU FORMULARIO FOI REJEITADO PARA ANALIZE!`"
        await ctx.author.send(_RESEARCH["-2"] + f"\n`SEU SCORE:` **{_SCORE[ctx.author.id]}**{extra}")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @research.command(name='feedback', aliases=['f'])
    async def _feedback(self, ctx):
        query = {"_id": 0, "user_id": 1, "research": 1}
        data = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        if "feedback" in data["research"].keys():
            try:
                return await ctx.author.send(_RESEARCH_2["-4"])
            except discord.errors.Forbidden:
                return await ctx.send(_RESEARCH_2["-4"])

        def check(m):
            if m.author.id == ctx.author.id:
                if 100 <= len(m.content) <= 450:
                    return True
            return False

        await ctx.send(_RESEARCH_2["0"], delete_after=5.0)
        _ANSWERS_2[ctx.author.id] = dict()
        _SCORE_2[ctx.author.id] = 0

        # ----------------------------------------------------------------------------------
        try:
            await ctx.author.send(_RESEARCH_2["1"] + _RESEARCH_2["-3"])
        except discord.errors.Forbidden:
            return await ctx.send("<:negate:721581573396496464>│`Desculpe, a pesquisa precisa ser feita no privado!`")
        try:
            _ANSWERS_2[ctx.author.id]["1"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["2"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["2"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["3"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["3"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["4"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["4"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["5"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["5"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["6"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["6"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["7"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["7"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["8"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["8"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["9"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["9"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH_2["10"] + _RESEARCH_2["-3"])
        try:
            _ANSWERS_2[ctx.author.id]["10"] = await self.bot.wait_for('message', check=check, timeout=120.0)
        except TimeoutError:
            return await ctx.author.send(_RESEARCH_2["-1"])

        for k in _ANSWERS_2[ctx.author.id].keys():
            _SCORE_2[ctx.author.id] += self.verify_answer(_ANSWERS_2[ctx.author.id][k].content)

        desc = f"`Pesquisa de:` **{ctx.author}**\n`ID:` **{ctx.author.id}**\n`Score:` **{_SCORE_2[ctx.author.id]}**"
        embed = discord.Embed(colour=self.color, description=desc)
        for k in _ANSWERS_2[ctx.author.id].keys():
            embed.add_field(name=_RESEARCH_2[k], value=f"**{_ANSWERS_2[ctx.author.id][k].content}**", inline=False)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        canal = self.bot.get_channel(839593358895743016)
        extra = ""
        if _SCORE_2[ctx.author.id] > 5000:
            await canal.send(embed=embed)
            cl = await self.bot.db.cd("users")
            query = {"$set": {"research.feedback": True}, "$inc": {"inventory.blessed_enchant_skill": 1}}
            await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)
            extra += "\n`VOCÊ GANHOU` **1 BLESSED ENCHANT SKILL** `OLHE O SEU INVENTARIO!`"
        else:
            extra += "\n`SEU FORMULARIO FOI REJEITADO PARA ANALIZE!`"
        await ctx.author.send(_RESEARCH_2["-2"] + f"\n`SEU SCORE:` **{_SCORE_2[ctx.author.id]}**{extra}")


def setup(bot):
    bot.add_cog(RegisterClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mREGISTERCLASS\033[1;32m foi carregado com sucesso!\33[m')
