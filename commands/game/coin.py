import discord

from random import choice, randint
from asyncio import sleep, TimeoutError
from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from datetime import datetime


class HeadsOrTails(commands.Cog):
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
    @commands.command(name='hot', aliases=['moeda'])
    async def hot(self, ctx, resposta: str = ""):
        """use ash hot ou ash moeda, cara ou coroa, acho que não preciso explicar"""

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

            choice_ = choice(['1', '2'])

            def check(m):
                return m.author == ctx.author and m.content == '1' or m.author == ctx.author and m.content == '2'

            if resposta in ['1', '2']:
                _answer = resposta
            else:
                await ctx.send("<:game:519896830230790157>│`Vamos brincar de` **CARA** `ou` **COROA**"
                               " `Escolha uma dessas opções abaixo:` \n"
                               "**[ 1 ]** - `Para Cara`\n"
                               "**[ 2 ]** - `Para Coroa`")

                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=30.0)
                except TimeoutError:
                    self.bot.jogando.remove(ctx.author.id)
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito:` **COMANDO'
                                          ' CANCELADO**')

                _answer = answer.content

            update['inventory']['coins'] -= ct
            await self.bot.db.update_data(data, update, 'users')
            reward = ['crystal_fragment_light', 'crystal_fragment_energy', 'crystal_fragment_dark', 'Energy']
            change = randint(5, 100)
            if change == 50:
                reward.append(choice(self.extra))

            soulshots = [choice(self.soulshot), choice(self.soulshot), choice(self.soulshot)]

            if choice_ == '1':
                msg_r = await ctx.send("Cara!")
                await msg_r.add_reaction('🙂')
                await sleep(1)
                if _answer == choice_:
                    answer_ = await self.bot.db.add_money(ctx, change, True)
                    await ctx.send('<:rank:519896825411665930>│`VOCÊ ACERTOU!` 🎊 **PARABENS** 🎉 '
                                   '`você GANHOU:`\n {}'.format(answer_))

                    souls = await self.bot.db.add_rpg(ctx, soulshots, False, 5)
                    await ctx.send('<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **SOULSHOTS** ✨ '
                                   '{}'.format(souls))

                    if change < 50:
                        response = await self.bot.db.add_reward(ctx, reward)
                        await ctx.send('<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       '{}'.format(response))
                else:
                    await ctx.send('<:negate:721581573396496464>│`INFELIZMENTE VOCE PERDEU!`')
            if choice_ == '2':
                msg_r = await ctx.send("Coroa!")
                await msg_r.add_reaction('👑')
                await sleep(1)
                if _answer == choice_:
                    answer_ = await self.bot.db.add_money(ctx, change, True)
                    await ctx.send('<:rank:519896825411665930>│`VOCÊ ACERTOU!` 🎊 **PARABENS** 🎉 '
                                   '`você GANHOU:`\n {}'.format(answer_))
                    if change < 50:
                        response = await self.bot.db.add_reward(ctx, reward)
                        await ctx.send('<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       '{}'.format(response))
                else:
                    await ctx.send('<:negate:721581573396496464>│`INFELIZMENTE VOCE PERDEU!`')
            self.bot.jogando.remove(ctx.author.id)
        else:
            if ctx.author.id in self.bot.jogando:
                await ctx.send('<:alert:739251822920728708>│`VOCÊ JÁ ESTÁ JOGANDO!`')
            else:
                await ctx.send(f'<:alert:739251822920728708>│`VOCÊ PRECISA DE + DE {ct} FICHAS PARA JOGAR`\n'
                               f'**OBS:** `USE O COMANDO` **ASH SHOP** `PARA COMPRAR FICHAS!`')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='caraoucoroa', aliases=['match'])
    async def caraoucoroa(self, ctx, member: discord.Member = None):
        if member is not None:
            if member.id == ctx.author.id:
                return await ctx.send("<:alert:739251822920728708>│`Você não pode jogar consigo mesmo!`")

            data_member = await self.bot.db.get_data("user_id", member.id, "users")
            if data_member is None:
                return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                      '`esse usuário não está cadastrado!`', delete_after=5.0)

            def check_challenge(m):
                return m.author.id == member.id and m.content.upper() in ['SIM', 'NÃO', 'S', 'N', 'NAO', 'CLARO']

            await ctx.send(f'<:game:519896830230790157>│{member.mention}, `VOCÊ RECEBEU UM DESAFIO PARA JOGAR '
                           f'COM` {ctx.author.mention} `DIGITE` **SIM** `OU` **NÃO** '
                           f'`PARA ACEITAR OU REGEITAR!`')
            try:
                answer = await self.bot.wait_for('message', check=check_challenge, timeout=30.0)
            except TimeoutError:
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, ele(a) demorou muito pra responder:` '
                                      '**COMANDO CANCELADO**')

            if answer.content.upper() not in ['SIM', 'S', 'CLARO']:
                return await ctx.send(f'<:negate:721581573396496464>│{ctx.author.mention} `VOCE FOI REJEITADO...`')

            _p1 = ctx.author.id

            def check_p1(m):
                return m.author.id == _p1 and m.content == '1' or m.author.id == _p1 and m.content == '2'

            await ctx.send(f"<:game:519896830230790157>│{ctx.author.mention} `Você começa, escolha ` "
                           "**CARA** `ou` **COROA** `com uma dessas opções abaixo:` \n"
                           "**[ 1 ]** - `Para Cara`\n**[ 2 ]** - `Para Coroa`")

            try:
                answer_p1 = await self.bot.wait_for('message', check=check_p1, timeout=30.0)
            except TimeoutError:
                return await ctx.author.send('<:negate:721581573396496464>│`Desculpe, você demorou muito!`')

            _ans = ("CARA", "COROA") if answer_p1.content == '1' else ("COROA", "CARA")
            await ctx.send(f"<:game:519896830230790157>│{member.mention}, {ctx.author.mention} `Escolheu` "
                           f"**{_ans[0]}**, `logo você fica com` **{_ans[1]}**")

            choice_ = choice(['1', '2'])

            if choice_ == '1':
                msg_r = await ctx.send("Cara!")
                await msg_r.add_reaction('🙂')
                await sleep(1)

                if _ans[0] == "CARA":
                    await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 {ctx.author.mention}'
                                   f'`VOCÊ ACERTOU!`')
                    await ctx.send(f'<:negate:721581573396496464>│{member.mention} `INFELIZMENTE VOCE PERDEU!`')
                else:
                    await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 {member.mention}'
                                   f'`VOCÊ ACERTOU!`')
                    await ctx.send(f'<:negate:721581573396496464>│{ctx.author.mention} `INFELIZMENTE VOCE PERDEU!`')

            else:
                msg_r = await ctx.send("Coroa!")
                await msg_r.add_reaction('👑')
                await sleep(1)

                if _ans[0] == "COROA":
                    await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 {ctx.author.mention}'
                                   f'`VOCÊ ACERTOU!`')
                    await ctx.send(f'<:negate:721581573396496464>│{member.mention} `INFELIZMENTE VOCE PERDEU!`')
                else:
                    await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 {member.mention}'
                                   f'`VOCÊ ACERTOU!`')
                    await ctx.send(f'<:negate:721581573396496464>│{ctx.author.mention} `INFELIZMENTE VOCE PERDEU!`')

            return await ctx.send('<:alert:739251822920728708>│`JOGO FINALIZADO!`')
        else:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa marcar alguem pra jogar!`")


def setup(bot):
    bot.add_cog(HeadsOrTails(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mCARA_OU_COROA\033[1;32m foi carregado com sucesso!\33[m')
