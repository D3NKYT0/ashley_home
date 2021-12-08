import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.lotash import Lottery, create
from resources.utility import create_id
from datetime import datetime as dt


class LotteryClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def format_num(num):
        a = '{:,.0f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    @staticmethod
    def verify_time(date_old):
        s, t, f = date_old.strftime('%Y/%m/%d %H:%M:%S'), dt.today().strftime('%Y/%m/%d %H:%M:%S'), '%Y/%m/%d %H:%M:%S'
        dif = (dt.strptime(t, f) - dt.strptime(s, f)).total_seconds()
        return True if dif < 86400 else False

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='lottery', aliases=['loteria', 'loto'])
    async def lottery(self, ctx, amount: int = None):
        """loteria da ashley"""
        if amount is None:
            return await ctx.send('<:negate:721581573396496464>│`VOCÊ PRECISA DIZER UMA QUANTIDADE DE BILHETES!`')

        if amount < 1:
            return await ctx.send('<:negate:721581573396496464>│`VOCÊ PRECISA DIZER UMA QUANTIDADE MAIOR QUE 0!`')

        if amount > 20:
            return await ctx.send('<:negate:721581573396496464>│`VOCÊ PRECISA DIZER UMA QUANTIDADE ENTRE 1 A 20!`')

        cl, msg = await self.bot.db.cd("users"), "**SEUS BILHETES**\n"
        data_user = await cl.find_one({"user_id": ctx.author.id}, {"_id": 0, "user_id": 1, "treasure.money": 1})

        if data_user["treasure"]["money"] < amount * 1000:
            return await ctx.send(f'<:negate:721581573396496464>│`VOCÊ NÃO TEM {amount * 1000} ETHERNYAS!`')

        await self.bot.db.take_money(ctx, amount * 1000)
        bets = create(Lottery("megasena"), amount, 6)

        for bet in bets:
            _bet_now = ' '.join('%02d' % n for n in bet)
            msg += f"<:confirmed:721581574461587496>│`{_bet_now}`\n"
            _bet = {"_id": create_id(), "bet": bet, "user_id": ctx.author.id, "date": dt.today(), "active": True}
            await self.bot.db.push_data(_bet, "lottery")

        query = {"$inc": {"accumulated": amount * 1000}}
        await (await self.bot.db.cd("miscellaneous")).update_one({"_id": "lottery"}, query)
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

        await ctx.send(f'<:coins:519896825365528596>│`PARABENS, VC COMPROU {amount} BILHETES E GASTOU '
                       f'R$ {self.format_num(amount * 1000)},00 DE ETHERNYAS COM SUCESSO!`')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='accumulated', aliases=['acumulado', 'ac'])
    async def accumulated(self, ctx):
        """Verifica o total aculumado atual das loterias da ashley"""
        cl = await (await self.bot.db.cd("miscellaneous")).find_one({"_id": "lottery"})
        msg = f'<:coins:519896825365528596>│`Atualmente o total acumulado é de:` ' \
              f'**{self.format_num(cl["accumulated"])}**'
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='tickets', aliases=['bilhetes', 'tk'])
    async def tickets(self, ctx):
        """Comando de compra de bilhetes para a loteria da ASHLEY"""
        _await = await ctx.send("<a:loading:520418506567843860>│ `AGUARDE, ESTOU PROCESSANDO SEU PEDIDO!`\n"
                                "**mesmo que demore, aguarde o fim do processamento...**")
        raw, actives, tot = (await self.bot.db.cd("lottery")).find({"user_id": ctx.author.id}), list(), list()
        async for d in raw:
            if self.verify_time(d["date"]) and d["active"]:
                actives.append(d)
            tot.append(d)

        msg = f'<:coins:519896825365528596>│`Atualmente você tem:` **{len(actives)}** `bilhetes ativos e `' \
              f'**{len(tot)}** `bilhetes comprados no total!`'
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await _await.delete()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LotteryClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mLOTTERY\033[1;32m foi carregado com sucesso!\33[m')
