import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice, randint
from resources.giftmanage import register_gift, open_gift, open_chest
from resources.img_edit import gift as gt
from resources.utility import convert_item_name


class OpenClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.i = self.bot.items
        self.chest_choice = {"Baú de Casamento - Rosa": "marry_pink", "Baú de Casamento - Laranja": "marry_orange",
                             "Baú de Casamento - Verde": "marry_green", "Baú de Casamento - Azul": "marry_blue"}

        self.discover_items = {

            "marry_blue": [("fragment_of_crystal_wind", 3),
                           ("fragment_of_crystal_water", 3),
                           ("fragment_of_crystal_fire", 3)],

            "marry_green": [("fragment_of_crystal_wind", 9),
                            ("fragment_of_crystal_water", 9),
                            ("fragment_of_crystal_fire", 9)],

            "marry_orange": [("fragment_of_crystal_wind", 18),
                             ("fragment_of_crystal_water", 18),
                             ("fragment_of_crystal_fire", 18)],

            "marry_pink": [("fragment_of_crystal_wind", 36),
                           ("fragment_of_crystal_water", 36),
                           ("fragment_of_crystal_fire", 36),
                           ("blessed_fragment_of_crystal_wind", 7),
                           ("blessed_fragment_of_crystal_water", 7),
                           ("blessed_fragment_of_crystal_fire", 7)],
        }

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='open', aliases=['abrir'])
    async def open(self, ctx):
        """Abra um presente para liberar seu giftcard."""
        if ctx.guild.id in self.bot.box:
            try:
                BOX = choice(self.bot.box[ctx.guild.id]['boxes'])
            except IndexError:
                return await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem presentes disponiveis!`\n"
                                      f"`TODOS OS PRESENTES FORAM UTILIZADOS, AGUARDE UM NOVO PRESENTE DROPAR E FIQUE "
                                      f"ATENTO!`")
            I_BOX = self.bot.box[ctx.guild.id]['boxes'].index(BOX)
            del (self.bot.box[ctx.guild.id]['boxes'][I_BOX])
            self.bot.box[ctx.guild.id]['quant'] -= 1
            time = randint(90, 600)
            gift = await register_gift(self.bot, time)

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")

            if not data['rpg']['vip']:
                await ctx.send(f"> 🎊 **PARABENS** 🎉 `VOCÊ GANHOU UM GIFT`\n"
                               f"`USE O COMANDO:` **ASH GIFT** `PARA RECEBER SEU PRÊMIO!!`")
                gt(gift, f"{time} SEGUNDOS")
                if discord.File('giftcard.png') is None:
                    return await ctx.send("<:negate:721581573396496464>│`ERRO!`")
                await ctx.send(file=discord.File('giftcard.png'))
            else:
                if not data['security']['status']:
                    return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS "
                                          "RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

                reward = await open_gift(self.bot, gift.upper())
                await ctx.send("🎊 **PARABENS** 🎉 `VC USOU SEU GIFT COM SUCESSO!!`")
                answer_ = await self.bot.db.add_money(ctx, reward['money'], True)
                await ctx.send(f'<:rank:519896825411665930>│`você GANHOU:`\n {answer_}')

                data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update = data
                update['inventory']['coins'] += reward["coins"]
                await self.bot.db.update_data(data, update, 'users')
                await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                               f'<:coin:546019942936608778> **{reward["coins"]}** `fichas!`')

                data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update = data
                response = '`Caiu pra você:` \n'
                for item in reward['items']:
                    amount = randint(10, 25)
                    try:
                        update['inventory'][item] += amount
                    except KeyError:
                        update['inventory'][item] = amount
                    response += f"{self.bot.items[item][0]} `{amount}` `{self.bot.items[item][1]}`\n"
                response += '```dê uma olhada no seu inventario com o comando: "ash i"```'
                await self.bot.db.update_data(data, update, 'users')
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if reward['rare'] is not None:
                    response = await self.bot.db.add_reward(ctx, reward['rare'], True)
                    await ctx.send(f'<a:caralho:525105064873033764>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS RAROS** ✨ '
                                   f'{response}')

        else:
            await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem presentes disponiveis...`\n"
                           f"**OBS:** se eu for reiniciada, todos os presentes disponiveis sao resetados. Isso é feito"
                           f" por medidas de segurança da minha infraestrutura!")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='gift', aliases=['g'])
    async def gift(self, ctx, *, gift=None):
        """Esse comando libera premios do giftcard que voce abriu no comando 'ash open'"""
        if gift is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa digitar um numero de GIFT!`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if not data_user['security']['status']:
            return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO "
                                  "DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

        reward = await open_gift(self.bot, gift.upper())
        if reward is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa digitar um numero de GIFT VALIDO!`")

        if not reward['validity']:
            return await ctx.send("<:negate:721581573396496464>│`ESSE GIFT ESTÁ COM O TEMPO EXPIRADO!`")

        await ctx.send("🎊 **PARABENS** 🎉 `VC USOU SEU GIFT COM SUCESSO!!`")
        answer_ = await self.bot.db.add_money(ctx, reward['money'], True)
        await ctx.send(f'<:rank:519896825411665930>│`você GANHOU:`\n {answer_}')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        update['inventory']['coins'] += reward["coins"]
        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                       f'<:coin:546019942936608778> **{reward["coins"]}** `fichas!`')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        response = '`Caiu pra você:` \n'
        for item in reward['items']:
            amount = randint(10, 25)
            try:
                update['inventory'][item] += amount
            except KeyError:
                update['inventory'][item] = amount
            response += f"{self.bot.items[item][0]} `{amount}` `{self.bot.items[item][1]}`\n"
        response += '```dê uma olhada no seu inventario com o comando: "ash i"```'
        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

        if reward['rare'] is not None:
            response = await self.bot.db.add_reward(ctx, reward['rare'], True)
            await ctx.send(f'<a:caralho:525105064873033764>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS RAROS** ✨ {response}')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='event', aliases=['evento'])
    async def event(self, ctx):
        """Abra um presente para liberar seu giftcard."""
        if not self.bot.event_special:
            return await ctx.send(f"<:negate:721581573396496464>│`ATUALMENTE NAO TEM NENHUM EVENTO ESPECIAL!`")

        if ctx.author.id in self.bot.chests_users:
            try:
                CHEST = choice(self.bot.chests_users[ctx.author.id]['chests'])
            except IndexError:
                return await ctx.send(f"<:negate:721581573396496464>│`Você nao tem mais baus disponiveis...`\n"
                                      f"`TODOS OS BAUS FORAM UTILIZADOS, DROPE UM NOVO BÁU UTILIZANDO O MAXIMO DE "
                                      f"COMANDOS DIFERENTES POSSIVEIS!`")

            I_CHEST = self.bot.chests_users[ctx.author.id]['chests'].index(CHEST)
            del (self.bot.chests_users[ctx.author.id]['chests'][I_CHEST])
            self.bot.chests_users[ctx.author.id]['quant'] -= 1
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            if not data['security']['status']:
                return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS "
                                      "RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

            reward = open_chest(self.bot.chests_l[str(CHEST)])
            await ctx.send("🎊 **PARABENS** 🎉 `VC ABRIU O SEU BAU COM SUCESSO!!`")
            answer_ = await self.bot.db.add_money(ctx, reward['money'], True)
            await ctx.send(f'<:rank:519896825411665930>│`você GANHOU:`\n {answer_}')

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory']['coins'] += reward["coins"]
            except KeyError:
                update['inventory']['coins'] = reward["coins"]
            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                           f'<:coin:546019942936608778> **{reward["coins"]}** `fichas!`')

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory']['Energy'] += reward["Energy"]
            except KeyError:
                update['inventory']['Energy'] = reward["Energy"]
            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                           f'<:energy:546019943603503114> **{reward["Energy"]}** `energias!`')

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            response = '`Caiu pra você:` \n'
            for item in reward['items']:
                amount = randint(1, 3)
                try:
                    update['inventory'][item] += amount
                except KeyError:
                    update['inventory'][item] = amount
                response += f"{self.bot.items[item][0]} `{amount}` `{self.bot.items[item][1]}`\n"
            response += '```dê uma olhada no seu inventario com o comando: "ash i"```'

            if self.bot.event_now not in update['event'].keys():
                update['event'][self.bot.event_now] = False

            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

            if reward['relic'][0] is not None:
                response = await self.bot.db.add_reward(ctx, reward['relic'], True)
                await ctx.send(f'<a:caralho:525105064873033764>│`VOCÊ TAMBEM GANHOU` ✨ **O ITEM SECRETO** ✨ '
                               f'{response}')

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            relics = ["WrathofNatureCapsule", "UltimateSpiritCapsule", "SuddenDeathCapsule", "InnerPeacesCapsule",
                      "EternalWinterCapsule", "EssenceofAsuraCapsule", "DivineCalderaCapsule", "DemoniacEssenceCapsule"]
            cr = 0
            for relic in relics:
                if relic in data['inventory'].keys():
                    cr += 1
            if cr == 8 and not update['event'][self.bot.event_now]:
                update['event'][self.bot.event_now] = True
                channel = self.bot.get_channel(543589223467450398)
                if channel is not None:
                    await channel.send(f'<a:caralho:525105064873033764>│{ctx.author} ✨ **GANHOU O EVENTO** ✨')
                    self.bot.event_special = False
                await self.bot.db.update_data(data, update, 'users')

        else:
            await ctx.send(f"<:negate:721581573396496464>│`Você nao tem mais baus disponiveis...`\n"
                           f"**OBS:** se eu for reiniciada, todos os baus disponiveis sao resetados. Isso é feito"
                           f" por medidas de segurança da minha infraestrutura!")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='chest', aliases=['bau', 'baú'])
    async def chest(self, ctx):
        """Abra um presente para liberar seu giftcard."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if not data['user']['married']:
            return await ctx.send(f"<:negate:721581573396496464>│`ATUALMENTE VOCÊ NÃO É CASADO!`")

        if ctx.author.id in self.bot.chests_marry:
            try:
                CHEST = choice(self.bot.chests_marry[ctx.author.id]['chests'])
            except IndexError:
                return await ctx.send(f"<:negate:721581573396496464>│`Você nao tem mais baus disponiveis...`\n"
                                      f"`TODOS OS BAUS FORAM UTILIZADOS, DROPE UM NOVO BÁU UTILIZANDO O MAXIMO DE "
                                      f"COMANDOS DIFERENTES POSSIVEIS!`")

            I_CHEST = self.bot.chests_marry[ctx.author.id]['chests'].index(CHEST)
            del (self.bot.chests_marry[ctx.author.id]['chests'][I_CHEST])
            self.bot.chests_marry[ctx.author.id]['quant'] -= 1
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            if not data['security']['status']:
                return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS "
                                      "RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

            key = self.bot.chests_lm[str(CHEST)]
            item = self.chest_choice[key]

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory'][item] += 1
            except KeyError:
                update['inventory'][item] = 1
            await self.bot.db.update_data(data, update, 'users')

            await ctx.send(f"🎊 **PARABENS** 🎉 `VC ABRIU O SEU BAU COM SUCESSO!!`\n"
                           f"`E GANHOU:` {self.i[item][0]} **{1}** `{self.i[item][1].upper()}`\n"
                           f"```Aproveite e olhe o seu inventário!```")

        else:
            await ctx.send(f"<:negate:721581573396496464>│`Você nao tem mais baus disponiveis...`\n"
                           f"**OBS:** se eu for reiniciada, todos os baus disponiveis sao resetados. Isso é feito"
                           f" por medidas de segurança da minha infraestrutura!")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='discover', aliases=['descobrir'])
    async def discover(self, ctx, amount: int = 1, *, item=None):
        """Abra um presente para liberar seu giftcard."""
        if item is None:
            return await ctx.send("<:alert:739251822920728708>│`Você esqueceu de falar o nome do item para descobrir!`")

        if amount < 1:
            return await ctx.send("<:alert:739251822920728708>│`A quantidade nao pode ser menor do que 0!`")

        item_key = convert_item_name(item, self.bot.items)

        if item_key is None:
            return await ctx.send("<:alert:739251822920728708>│`Item Inválido!`")

        if item_key not in ["marry_pink", "marry_orange", "marry_green", "marry_blue"]:
            return await ctx.send("<:alert:739251822920728708>│`Você não pode descobrir esse tipo de item.`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if data_user['config']['playing']:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if data_user['config']['battle']:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        item_name = self.bot.items[item_key][1]

        if item_key not in data_user['inventory']:
            return await ctx.send(f"<:alert:739251822920728708>│`Você não tem {item_name.upper()} no seu "
                                  f"inventario!`")

        if data_user['inventory'][item_key] < amount:
            return await ctx.send(f"<:alert:739251822920728708>│`Você não tem` **{amount}** `de {item_name.upper()} no"
                                  f" seu inventario!`")

        update_user['inventory'][item_key] -= amount
        if update_user['inventory'][item_key] < 1:
            del update_user['inventory'][item_key]

        msg, items = "", dict()
        for _ in range(amount):
            item_discovered = choice(self.discover_items[item_key])
            quant = randint(1, item_discovered[1])

            try:
                items[item_discovered[0]] += quant
            except KeyError:
                items[item_discovered[0]] = quant

            try:
                update_user['inventory'][item_discovered[0]] += quant
            except KeyError:
                update_user['inventory'][item_discovered[0]] = quant

            if item_key == "marry_pink":
                item_discovered_2 = choice(self.discover_items[item_key])
                amount_2 = randint(1, item_discovered_2[1])

                try:
                    items[item_discovered_2[0]] += amount_2
                except KeyError:
                    items[item_discovered_2[0]] = amount_2

                try:
                    update_user['inventory'][item_discovered_2[0]] += amount_2
                except KeyError:
                    update_user['inventory'][item_discovered_2[0]] = amount_2

        for it in items.keys():
            msg += f"\n{self.i[it][0]} **{items[it]}** `{self.i[it][1].upper()}`\n"

        await self.bot.db.update_data(data_user, update_user, 'users')
        await ctx.send(f'<:confirmed:721581574461587496>│`PARABENS, VC DESCOBRIU` {msg} `COM SUCESSO!`')
        await self.bot.data.add_sts(ctx.author, "discover", amount)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='key', aliases=['chave'])
    async def key(self, ctx, amount: int = 1):
        """Abra um presente para liberar seu giftcard."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if amount < 1:
            return await ctx.send("<:negate:721581573396496464>│`A QUANTIDADE NAO PODE SER MENOR QUE 1!`")

        if not data['security']['status']:
            return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS "
                                  "RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

        if "boss_key" in data['inventory'].keys():
            if data['inventory']['boss_key'] < amount:
                return await ctx.send(f"<:negate:721581573396496464>│`Você nao tem` {self.i['boss_key'][0]} `{amount}`"
                                      f"**{self.i['boss_key'][1]}** `disponiveis no seu inventario!`")
        else:
            return await ctx.send(f"<:negate:721581573396496464>│`Você nao tem` {self.i['boss_key'][0]} "
                                  f"**{self.i['boss_key'][1]}** `no seu inventario!`")

        update['inventory']['boss_key'] -= amount
        if update['inventory']['boss_key'] <= 0:
            del update['inventory']['boss_key']
        await self.bot.db.update_data(data, update, 'users')

        bchest = choice(["Baú de Evento - Incomum", "Baú de Evento - Raro",
                         "Baú de Evento - Super Raro", "Baú de Evento - Ultra Raro"])

        reward = open_chest(bchest, False, amount)
        await ctx.send("🎊 **PARABENS** 🎉 `VC ABRIU O SEU BAU DO BOSS COM SUCESSO!!`")
        answer_ = await self.bot.db.add_money(ctx, reward['money'], True)
        await ctx.send(f'<:rank:519896825411665930>│`você GANHOU:`\n {answer_}')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        try:
            update['inventory']['coins'] += reward["coins"]
        except KeyError:
            update['inventory']['coins'] = reward["coins"]
        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                       f'<:coin:546019942936608778> **{reward["coins"]}** `fichas!`')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        try:
            update['inventory']['Energy'] += reward["Energy"]
        except KeyError:
            update['inventory']['Energy'] = reward["Energy"]
        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f'<:rank:519896825411665930>│🎊 **PARABENS** 🎉 : `Você acabou de ganhar` '
                       f'<:energy:546019943603503114> **{reward["Energy"]}** `energias!`')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        response = '`Caiu pra você:` \n'
        _items = dict()
        for item in reward['items']:
            amount = randint(1, 2)
            try:
                update['inventory'][item] += amount
            except KeyError:
                update['inventory'][item] = amount
            try:
                _items[item] += amount
            except KeyError:
                _items[item] = amount

        for _it in _items.keys():
            response += f"{self.bot.items[_it][0]} `{_items[_it]}` `{self.bot.items[_it][1]}`\n"

        response += '```dê uma olhada no seu inventario com o comando: "ash i"```'

        if self.bot.event_now not in update['event'].keys():
            update['event'][self.bot.event_now] = False

        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

        if len(reward['relic']) > 0:
            response = await self.bot.db.add_reward(ctx, reward['relic'], True)
            await ctx.send(f'<a:caralho:525105064873033764>│`VOCÊ TAMBEM GANHOU` ✨ **O ITEM SECRETO** ✨ '
                           f'{response}')


def setup(bot):
    bot.add_cog(OpenClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mOPEN\033[1;32m foi carregado com sucesso!\33[m')
