import discord

from random import choice, randint
from asyncio import TimeoutError
from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from datetime import datetime

player_ = ""


class JoKenPo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.extra = ['Melted_Bone', 'Life_Crystal', 'Death_Blow', 'Stone_of_Soul', 'Vital_Force']

        self.soulshot = ['soushot_platinum_silver', 'soushot_platinum_mystic', 'soushot_platinum_inspiron',
                         'soushot_platinum_violet', 'soushot_platinum_hero', 'soushot_leather_silver',
                         'soushot_leather_mystic', 'soushot_leather_inspiron', 'soushot_leather_violet',
                         'soushot_leather_hero', 'soushot_cover_silver', 'soushot_cover_mystic',
                         'soushot_cover_inspiron', 'soushot_cover_violet', 'soushot_cover_hero']

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='jkp', aliases=['jokenpo'])
    async def jkp(self, ctx, resposta: str = ""):
        """Use ash jkp ou ash jokenpo
        Escolha pedra papel ou tesoura e torça pela sua sorte"""
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

            global player_
            jkp = choice(["Pedra", "Papel", "Tesoura"])

            def check(m):
                return m.author == ctx.author and m.content == '1' or m.author == ctx.author and m.content == '2' \
                       or m.author == ctx.author and m.content == '3'

            if resposta in ['1', '2', '3']:
                _answer = resposta
            else:
                await ctx.send("<:game:519896830230790157>│`Vamos brincar de` **JO-KEN-PO!** `Eu ja escolhi, "
                               "agora é sua vez! Escolha uma dessas opções abaixo:` \n"
                               "**[ 1 ]** - `Para Pedra`\n"
                               "**[ 2 ]** - `Para Papel`\n"
                               "**[ 3 ]** - `Para Tesoura`")

                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=30.0)
                except TimeoutError:
                    self.bot.jogando.remove(ctx.author.id)
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito, eu tinha '
                                          'escolhido:` **{}**.'.format(jkp))
                _answer = answer.content

            update['inventory']['coins'] -= ct
            await self.bot.db.update_data(data, update, 'users')
            reward = ['crystal_fragment_light', 'crystal_fragment_energy', 'crystal_fragment_dark', 'Energy']
            soulshots = [choice(self.soulshot), choice(self.soulshot), choice(self.soulshot), choice(self.soulshot)]
            change = randint(10, 100)
            if change == 50:
                reward.append(choice(self.extra))

            if _answer == "1":
                player_ = "Pedra"
            elif _answer == "2":
                player_ = "Papel"
            elif _answer == "3":
                player_ = "Tesoura"

            if _answer == "1":  # jogador escolheu "Pedra"

                if jkp == "Pedra":
                    await ctx.send("<:game:519896830230790157>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `empata com` "
                                   "**{}** `EMPATAMOS.`".format(ctx.author, player_, jkp, player_, jkp))
                elif jkp == "Tesoura":
                    answer_ = await self.bot.db.add_money(ctx, change, True)
                    await ctx.send("<:rank:519896825411665930>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `ganha de` "
                                   "**{}** 🎊 **PARABENS** 🎉 `você GANHOU:`\n"
                                   "{}".format(ctx.author, player_, jkp, player_, jkp, answer_))

                    souls = await self.bot.db.add_rpg(ctx, soulshots, False, 5)
                    await ctx.send('<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **SOULSHOTS** ✨ '
                                   '{}'.format(souls))

                    if change < 50:
                        response = await self.bot.db.add_reward(ctx, reward)
                        await ctx.send('<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       '{}'.format(response))
                elif jkp == "Papel":
                    await ctx.send("<:negate:721581573396496464>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `perde para` "
                                   "**{}** `VOCÊ PERDEU!!`".format(ctx.author, player_, jkp, player_, jkp))

            elif _answer == "2":  # jogador escolheu "Papel"

                if jkp == "Pedra":
                    answer_ = await self.bot.db.add_money(ctx, change, True)
                    await ctx.send("<:rank:519896825411665930>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `ganha de` "
                                   "**{}** 🎊 **PARABENS** 🎉 `você GANHOU:`\n"
                                   "{}".format(ctx.author, player_, jkp, player_, jkp, answer_))

                    souls = await self.bot.db.add_rpg(ctx, soulshots, False, 5)
                    await ctx.send('<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **SOULSHOTS** ✨ '
                                   '{}'.format(souls))

                    if change < 50:
                        response = await self.bot.db.add_reward(ctx, reward)
                        await ctx.send('<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       '{}'.format(response))
                elif jkp == "Papel":
                    await ctx.send("<:game:519896830230790157>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `empata com` "
                                   "**{}** `EMPATAMOS.`".format(ctx.author, player_, jkp, player_, jkp))
                elif jkp == "Tesoura":
                    await ctx.send("<:negate:721581573396496464>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `perde para` "
                                   "**{}** `VOCÊ PERDEU!!`".format(ctx.author, player_, jkp, player_, jkp))

            elif _answer == "3":  # jogador escolheu "Tesoura"

                if jkp == "Pedra":
                    await ctx.send("<:negate:721581573396496464>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `perde para` "
                                   "**{}** `VOCÊ PERDEU!!`".format(ctx.author, player_, jkp, player_, jkp))
                elif jkp == "Papel":
                    answer_ = await self.bot.db.add_money(ctx, change, True)
                    await ctx.send("<:rank:519896825411665930>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `ganha de` "
                                   "**{}** 🎊 **PARABENS** 🎉 `você GANHOU:`\n"
                                   "{}".format(ctx.author, player_, jkp, player_, jkp, answer_))

                    souls = await self.bot.db.add_rpg(ctx, soulshots, False, 5)
                    await ctx.send('<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **SOULSHOTS** ✨ '
                                   '{}'.format(souls))

                    if change < 50:
                        response = await self.bot.db.add_reward(ctx, reward)
                        await ctx.send('<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       '{}'.format(response))
                elif jkp == "Tesoura":
                    await ctx.send("<:game:519896830230790157>│`{}, você escolheu` **{}** `e eu "
                                   "escolhi` **{}, {}** `empata com` "
                                   "**{}** `EMPATAMOS.`".format(ctx.author, player_, jkp, player_, jkp))

            self.bot.jogando.remove(ctx.author.id)
        else:
            if ctx.author.id in self.bot.jogando:
                await ctx.send('<:alert:739251822920728708>│`VOCÊ JÁ ESTÁ JOGANDO!`')
            else:
                await ctx.send(f'<:alert:739251822920728708>│`VOCÊ PRECISA DE + DE {ct} FICHAS PARA JOGAR`\n'
                               f'**OBS:** `USE O COMANDO` **ASH SHOP** `PARA COMPRAR FICHAS!`')


def setup(bot):
    bot.add_cog(JoKenPo(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mJOKENPO\033[1;32m foi carregado com sucesso!\33[m')
