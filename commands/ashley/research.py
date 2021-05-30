import discord

from asyncio import sleep, TimeoutError
from discord.ext import commands
from resources.check import check_it
from resources.db import Database

_ANSWERS = dict()
_SCORE = dict()
_RESEARCH = {
    "-4": "<:negate:721581573396496464>│`Desculpe, você já fez essa pesquisa!`",
    "-3": "\n```CONTEUDO COM NO MINIMO 100 CARACTERES E NO MAXIMO 450 CARACTERES!```",
    "-2": "<:confirmed:721581574461587496>│`FORMULARIO FINALIZADO COM SUCESSO!`",
    "-1": "<:negate:721581573396496464>│`Desculpe, você demorou muito!`",
    "0": "<:send:519896817320591385>│`ESTAREI ENVIANDO PARA SEU PRIVADO O FORMULARIO!`",

    "1": "<a:blue:525032762256785409>│`O QUE TE FAZ JOGAR A ASHLEY TODO O DIA?`",
    "2": "<a:blue:525032762256785409>│`QUAL A FUNÇÃO DA ASHLEY QUE MAIS É IMPORTANTE PRA VOCÊ? POR QUE?`",
    "3": "<a:blue:525032762256785409>│`O QUE FALTA PARA QUE VOCÊ ACHE QUE DEVERIA DOAR ALGUM VALOR PARA OBTER"
         " ALGUMA VANTAGEM NA ASHLEY? ALGO COMO VIP, ITENS E ETC...`",
    "4": "<a:blue:525032762256785409>│`VOCÊ RECOMENDARIA O RPG DA ASHLEY PARA ALGUM AMIGO?`",
    "5": "<a:blue:525032762256785409>│`O QUE VOCÊ ACHA DOS EVENTOS DA ASHLEY?`",
    "6": "<a:blue:525032762256785409>│`EXISTE ALGUMA FUNÇÃO QUE VOCE ACHA PRIMORDIAL E AINDA NAO TEM NA ASHLEY?`",
    "7": "<a:blue:525032762256785409>│`VOCÊ ACHA O SISTEMA DE PVP / RAID / BOSS DA ASHLEY COMPETITIVO? POR QUE?`",
    "8": "<a:blue:525032762256785409>│`SE A ASHLEY PARASSE DE SER DESENVOLVIDA HOJE, VOCÊ SENTIRIA FALTA? POR QUE?`",
    "9": "<a:blue:525032762256785409>│`VOCÊ ACHA QUE EXISTE MUITA DIFERENÇA PARA QUEM É VIP E QUEM NAO É A PONTO DE"
         " DEIXAR A EXPERIENCIA DO RPG DESLEAL?`",
    "10": "<a:blue:525032762256785409>│`QUAL CONSELHO VOCÊ DARIA PARA O CRIADOR DA ASHLEY, "
          "OU ALGUMA RECLAMAÇÃO OU ELOGIO?`",
}


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
                          value=f"{self.st[67]} `p s` Faça uma pesquisa de satisfação sobre a ASHLEY!")
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
            return await ctx.author.send(_RESEARCH["-4"])

        def check(m):
            if m.author.id == ctx.author.id:
                if 100 <= len(m.content) <= 450:
                    return True
            return False

        await ctx.send(_RESEARCH["0"], delete_after=5.0)
        _ANSWERS[ctx.author.id] = dict()
        _SCORE[ctx.author.id] = 0

        # ----------------------------------------------------------------------------------
        await ctx.author.send(_RESEARCH["1"] + _RESEARCH["-3"])
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
            data["research"]["satisfaction"] = True
            cl = await self.bot.db.cd("users")
            query = {"$set": {"research": data['research']}}
            await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)
        else:
            extra += "\n`SEU FORMULARIO FOI REJEITADO PARA ANALIZE!`"
        await ctx.author.send(_RESEARCH["-2"] + f"\n`SEU SCORE:` **{_SCORE[ctx.author.id]}**{extra}")


def setup(bot):
    bot.add_cog(RegisterClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mREGISTERCLASS\033[1;32m foi carregado com sucesso!\33[m')
