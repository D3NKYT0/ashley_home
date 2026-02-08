import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.utility import parse_duration as pd
from random import randint, choice
from datetime import datetime

m = 0
money = 0
epoch = datetime.utcfromtimestamp(0)
TOT_REC = 10


class DailyClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color

        self.extra = ['unsealed_stone', 'Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal',
                      'melted_artifact', 'marry_orange', 'marry_green', 'marry_blue']

        self.soulshot = ['soushot_platinum_silver', 'soushot_platinum_mystic', 'soushot_platinum_inspiron',
                         'soushot_platinum_violet', 'soushot_platinum_hero', 'soushot_leather_silver',
                         'soushot_leather_mystic', 'soushot_leather_inspiron', 'soushot_leather_violet',
                         'soushot_leather_hero', 'soushot_cover_silver', 'soushot_cover_mystic',
                         'soushot_cover_inspiron', 'soushot_cover_violet', 'soushot_cover_hero']

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='daily', aliases=['diario', 'd'])
    async def daily(self, ctx):
        """Comando usado pra retornar uma lista de todos os subcomandos de daily
        Use ash daily"""
        if ctx.invoked_subcommand is None:
            self.status()
            daily = discord.Embed(color=self.color)
            daily.add_field(name="Daily Commands:",
                            value=f"{self.st[66]} `daily coin` Receba suas fichas diarias.\n"
                                  f"{self.st[66]} `daily energy` Receba suas energias diarias.\n"
                                  f"{self.st[66]} `daily work` Trabalhe duro e receba seu salario.\n"
                                  f"{self.st[66]} `daily vip` Recompença diaria para VIPs.")
            daily.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            daily.set_thumbnail(url=self.bot.user.display_avatar)
            daily.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=daily)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=86400))
    @daily.group(name='coin', aliases=['ficha'])
    async def _coin(self, ctx):
        """Comando usado pra ganhar coins de jogo da Ashley
        Use ash daily coin"""
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if not data_user['security']['status']:
            return await ctx.send("<:alert:739251822920728708>│`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO "
                                  "DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**")

        cc, ct = 350, 1100
        patent = update_user['user']['patent']
        if data_user['rpg']['active']:
            date_old = data_user['rpg']['activated_at']
            date_now = datetime.today()
            days = abs((date_old - date_now).days)
            if days <= 10:
                cc, ct = 1100, 2400

        coin = randint(cc, ct)
        tot = coin + (patent * 25)
        try:
            update_user['inventory']['coins'] += tot
        except KeyError:
            update_user['inventory']['coins'] = tot
        await self.bot.db.update_data(data_user, update_user, 'users')
        await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                       f'<:coin:546019942936608778> **{coin}** `fichas!` + **{patent * 25}** '
                       f'`pela sua patente. Olhe seu inventario usando o comando:` **ash i**')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=86400, vip=True))
    @daily.group(name='vip', aliases=['v'])
    async def _vip(self, ctx):
        """Comando usado pra ganhar itens de jogo da Ashley
        Use ash daily vip"""
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if not data_user['security']['status']:
            return await ctx.send("<:alert:739251822920728708>│`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO "
                                  "DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**")

        reward = ['onyx', 'diamond', 'marry_pink']
        if randint(1, 100) >= 50:
            reward.append(choice(self.extra))
        if randint(1, 100) >= 50:
            reward.append(choice(self.extra))
        if randint(1, 100) >= 50:
            reward.append(choice(self.extra))

        soulshots = ["summon_box_secret", choice(self.soulshot), choice(self.soulshot), choice(self.soulshot)]
        if randint(1, 100) >= 50:
            soulshots.append(choice(self.soulshot))
        if randint(1, 100) >= 50:
            soulshots.append(choice(self.soulshot))

        souls = await self.bot.db.add_rpg(ctx, soulshots, False, 5)
        msg = f"<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **SOULSHOTS** ✨ {souls}"
        response = await self.bot.db.add_reward(ctx, reward)
        msg += f"\n<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}"
        await ctx.send(msg)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=86400))
    @daily.group(name='energy', aliases=['energia'])
    async def _energy(self, ctx):
        """Comando usado pra ganhar coins de jogo da Ashley
        Use ash daily energy"""
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if not data_user['security']['status']:
            return await ctx.send("<:alert:739251822920728708>│`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO "
                                  "DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**")

        patent = update_user['user']['patent']
        energy = randint(250, 500)
        tot = energy + (patent * 25)
        try:
            update_user['inventory']['Energy'] += tot
        except KeyError:
            update_user['inventory']['Energy'] = tot
        await self.bot.db.update_data(data_user, update_user, 'users')
        await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                       f'<:energy:546019943603503114> **{energy}** `Energias!` + **{patent * 25}** '
                       f'`pela sua patente. Olhe seu inventario usando o comando:` **ash i**')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=86400))
    @daily.group(name='work', aliases=['trabalho', 'trabalhar'])
    async def _work(self, ctx):
        """Comando usado pra ganhar o dinheiro da Ashley diariamente
        Use ash daily work"""
        if self.bot.guilds_commands[ctx.guild.id] > 50:
            if self.bot.commands_user[ctx.author.id] > 20:
                global money, m
                data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                if not data_user['security']['status']:
                    return await ctx.send("<:alert:739251822920728708>│`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO"
                                          " DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**")

                if data_user['user']['ranking'] == "Bronze":
                    money = 70 * 5
                    m = 5
                elif data_user['user']['ranking'] == "Silver":
                    money = 70 * 10
                    m = 10
                elif data_user['user']['ranking'] == "Gold":
                    money = 70 * 15
                    m = 15

                msg = await self.bot.db.add_money(ctx, money)
                await ctx.send(f'<:confirmed:721581574461587496>│`Você trabalhou duro e acabou de ganhar:`\n{msg}')
                commands_work = data_user['security']['commands_today']
                msg = await self.bot.db.add_money(ctx, commands_work * m)
                await ctx.send(f'<:confirmed:721581574461587496>│`Você tambem ganhou:`\n{msg}\n'
                               f'`de ETHERNYAS a mais por usar {data_user["security"]["commands_today"]} comandos.`')
            else:
                try:
                    data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                    update_ = data_
                    del data_['cooldown'][str(ctx.command)]
                    await self.bot.db.update_data(data_, update_, 'users')
                except KeyError:
                    pass
                await ctx.send('<:alert:739251822920728708>│`VOCÊ AINDA NÃO USOU + DE 20 COMANDOS DA '
                               'ASHLEY DESDE A ULTIMA VEZ EM QUE ELA FICOU ONLINE!`')
        else:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            await ctx.send('<:alert:739251822920728708>│`O SERVIDOR ATUAL AINDA NÃO USOU + DE 50 COMANDOS DA '
                           'ASHLEY DESDE A ULTIMA VEZ EM QUE ELA FICOU ONLINE!`')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='rec', aliases=['recomendação', 'rep', 'reputação'])
    async def rec(self, ctx, member: discord.Member = None):
        """Comando usado pra dar um rec da Ashley pra algum usuario
        Use ash rec <usuario desejado>"""
        if member is None:
            return await ctx.send('<:alert:739251822920728708>│`Você precisa mencionar alguem!`')

        data_user = await self.bot.db.get_data("user_id", member.id, "users")
        update_user = data_user
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        chance = randint(1, 100)
        reward = False

        if member.id == ctx.author.id:
            return await ctx.send('<:alert:739251822920728708>│`Você não pode dar REC em si mesmo!`')
        if data_user is None:
            return await ctx.send('<:alert:739251822920728708>│`Você precisa mencionar alguem cadastrado no meu '
                                  'banco de dados!`')
        if not data_user['security']['status']:
            return await ctx.send("<:alert:739251822920728708>│`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO "
                                  "DEMAIS` **ESSE TIPO DE USUARIO NAO PODE RECEBER RECOMENDAÇÃO...**")

        try:
            time_diff = (datetime.utcnow() - epoch).total_seconds() - update['cooldown']['rec']['date']
            if time_diff < 86400:
                if update['cooldown']['rec']['cont'] >= TOT_REC:
                    time_ = pd(int(86400 - time_diff))
                    return await ctx.send(f"<:alert:739251822920728708>│`Você ultrapassou suas recomendações diarias,"
                                          f" então deve esperar` **{time_}** `para usar esse comando novamente!`")
                if member.id in update['cooldown']['rec']['list']:
                    return await ctx.send(f"<:alert:739251822920728708>│`Você já deu REC nesse membro hoje!`")

                update['cooldown']['rec']['cont'] += 1
                update['cooldown']['rec']['list'].append(member.id)

            else:
                update['cooldown']['rec'] = {"cont": 1, "date": (datetime.utcnow() - epoch).total_seconds(),
                                             "list": [member.id]}
        except KeyError:
            update['cooldown']['rec'] = {"cont": 1, "date": (datetime.utcnow() - epoch).total_seconds(),
                                         "list": [member.id]}

        # o rec é dado aqui (acima é apenas testes, e abaixo as premiações.)
        update_user['user']['rec'] += 1

        embed = discord.Embed(color=self.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        embed.set_image(url="https://i.pinimg.com/originals/1f/48/c4/1f48c47b7803eca495d237be1d0cfaba.gif")

        if (update_user['user']['rec'] % 2) == 0:
            if chance <= 25:
                if update_user['user']['stars'] < 25:
                    update_user['user']['stars'] += 1
                    await ctx.send(embed=embed)
                    await ctx.send(f'<:rank:519896825411665930>│{member.mention} `GANHOU 1 ESTRELA!` '
                                   f'🎊 **PARABENS** 🎉 **APROVEITE E OLHE SEU RANK PARA VER SUA ESTRELINHA NOVA COM '
                                   f'O COMANDO:** `ASH RANK`')
                    if chance < 6:
                        if update['user']['stars'] < 25:
                            update['user']['stars'] += 1
                            await ctx.send(embed=embed)
                            await ctx.send(f'<:rank:519896825411665930>│{ctx.author.mention} `TAMBEM GANHOU 1 '
                                           f'ESTRELA!` 🎊 **PARABENS** 🎉 **APROVEITE E OLHE SEU RANK PARA VER SUA '
                                           f'ESTRELINHA NOVA COM O COMANDO:** `ASH RANK`')
                        else:
                            reward = True
                else:
                    if update['user']['stars'] < 25:
                        update['user']['stars'] += 1
                        await ctx.send(embed=embed)
                        await ctx.send(f'<:rank:519896825411665930>│{ctx.author.mention} `GANHOU 1 ESTRELA, PORQUE` '
                                       f'{member.mention} `JA TEM TODAS AS 25 ESTRELAS DISPONIVEIS`'
                                       f'🎊 **PARABENS** 🎉 **APROVEITE E OLHE SEU RANK PARA VER SUA ESTRELINHA NOVA '
                                       f'COM O COMANDO:** `ASH RANK`')

        await ctx.send(f'<:confirmed:721581574461587496>│{member.mention} `ACABOU DE RECEBER +1 REC DE ` '
                       f'{ctx.author.mention}`, QUE DEU SEUS ` **{update["cooldown"]["rec"]["cont"]}**`/{TOT_REC} '
                       f'RECS DISPONIVEIS`')

        await self.bot.db.update_data(data, update, 'users')
        await self.bot.db.update_data(data_user, update_user, 'users')

        if reward:
            response = await self.bot.db.add_reward(ctx, ['?-Bollash'])
            await ctx.send(f'<a:fofo:524950742487007233>│{ctx.author.mention} `COMO VOCE NAO PODE MAIS GANHAR '
                           f'ESTRELAS POR JA TER TODAS AS 25 ESTRELAS DISPONIVEIS VOCE GANHOU` '
                           f'✨ **ITENS PARA PET** ✨ {response}')

        elif update_user['user']['stars'] >= 25 and update['user']['stars'] >= 25:
            response = await self.bot.db.add_reward(ctx, ['?-Bollash'])
            await ctx.send(f'<a:fofo:524950742487007233>│{ctx.author.mention} `COMO NEM VOCE NEM` '
                           f'{member.mention} `PODEM MAIS GANHAR ESTRELAS POR JA TEREM TODAS AS 25`'
                           f' `VOCE GANHOU` ✨ **ITENS PARA PET** ✨ {response}')

        response = await self.bot.db.add_reward(ctx, ['Energy', 'Energy', 'Energy', 'Energy', 'Energy'])
        await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ENERGIA 5x** ✨ {response}')


async def setup(bot):
    await bot.add_cog(DailyClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mDAILYCLASS\033[1;32m foi carregado com sucesso!\33[m')
