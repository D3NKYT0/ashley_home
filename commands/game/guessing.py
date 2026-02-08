import discord

from asyncio import TimeoutError
from random import choice, randint
from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from datetime import datetime


class GameThinker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.extra = ['Melted_Bone', 'Life_Crystal', 'Death_Blow', 'Stone_of_Soul', 'Vital_Force']

        self.soulshot = ['soushot_platinum_silver', 'soushot_platinum_mystic', 'soushot_platinum_inspiron',
                         'soushot_platinum_violet', 'soushot_platinum_hero', 'soushot_leather_silver',
                         'soushot_leather_mystic', 'soushot_leather_inspiron', 'soushot_leather_violet',
                         'soushot_leather_hero', 'soushot_cover_silver', 'soushot_cover_mystic',
                         'soushot_cover_inspiron', 'soushot_cover_violet', 'soushot_cover_hero',
                         'soushot_platinum_divine', 'soushot_leather_divine', 'soushot_cover_divine']

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='guess', aliases=['advinhe', 'adivinhe'])
    async def guess(self, ctx, resposta: str = ""):
        """Use ash guess ou ash adivinhe, e tente acertar o numero que ela pensou"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        try:
            if data['inventory']['coins']:
                pass
        except KeyError:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`VOCE NÃO TEM FICHA!`')
            return await ctx.send(embed=embed)

        ct = 25
        if data['rpg']['active']:
            date_old = data['rpg']['activated_at']
            date_now = datetime.today()
            days = abs((date_old - date_now).days)
            if days <= 10:
                ct = 5

        if data['inventory']['coins'] > ct and ctx.author.id not in self.bot.jogando:
            self.bot.jogando.append(ctx.author.id)

            number = choice(['0', '1', '2', '3', '4', '5'])

            def check(m):
                return m.author == ctx.author and m.content.isdigit()

            if resposta in ['0', '1', '2', '3', '4', '5']:
                _answer = resposta
            else:
                await ctx.send("<:game:519896830230790157>│`Acabei de pensar em um numero entre` **0** `até` "
                               "**5**, `tente advinhar qual foi o numero eu pensei:`")

                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=30.0)
                except TimeoutError:
                    self.bot.jogando.remove(ctx.author.id)
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito, o número que eu '
                                          'tinha escolhido era` **{}**.'.format(number))
                _answer = answer.content

            update['inventory']['coins'] -= ct
            await self.bot.db.update_data(data, update, 'users')
            reward = ['crystal_fragment_light', 'crystal_fragment_energy', 'crystal_fragment_dark', 'Energy']
            soulshots = [choice(self.soulshot), choice(self.soulshot), choice(self.soulshot),
                         choice(self.soulshot), choice(self.soulshot), choice(self.soulshot)]
            change = randint(15, 100)
            if change == 50:
                reward.append(choice(self.extra))

            if _answer in ["0", "1", "2", "3", "4", "5"]:
                if _answer == number:
                    answer_ = await self.bot.db.add_money(ctx, change, True)
                    await ctx.send("<:rank:519896825411665930>│`O numero que eu pensei foi` **{}** "
                                   "`e o número que vc falou foi` **{}** 🎊 **PARABENS** 🎉 `você GANHOU:`\n"
                                   "{}".format(number, _answer, answer_))

                    souls = await self.bot.db.add_rpg(ctx, soulshots, False, 5)
                    await ctx.send('<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **SOULSHOTS** ✨ '
                                   '{}'.format(souls))

                    if change < 50:
                        response = await self.bot.db.add_reward(ctx, reward)
                        await ctx.send('<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       '{}'.format(response))
                else:
                    await ctx.send("<:negate:721581573396496464>│`O numero que eu pensei foi` **{}** "
                                   "`e o número que vc falou foi` **{}**"
                                   " `Infelizmente Você PERDEU!`".format(number, _answer))
            else:
                await ctx.send("<:negate:721581573396496464>│`Você não digitou um número válido!` "
                               "**Tente Novamente!**")
            self.bot.jogando.remove(ctx.author.id)
        else:
            if ctx.author.id in self.bot.jogando:
                await ctx.send('<:alert:739251822920728708>│`VOCÊ JÁ ESTÁ JOGANDO!`')
            else:
                await ctx.send(f'<:alert:739251822920728708>│`VOCÊ PRECISA DE + DE {ct} FICHAS PARA JOGAR`\n'
                               f'**OBS:** `USE O COMANDO` **ASH SHOP** `PARA COMPRAR FICHAS!`')


async def setup(bot):
    await bot.add_cog(GameThinker(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mGAME\033[1;32m foi carregado com sucesso!\33[m')
