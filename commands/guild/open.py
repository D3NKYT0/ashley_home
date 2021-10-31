import discord
import copy

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice, randint
from resources.giftmanage import register_gift, open_gift, open_chest
from resources.img_edit import gift as gt
from resources.utility import convert_item_name, include
from resources.moon import get_moon

from asyncio import sleep
from resources.fight import Ext
from resources.img_edit import calc_xp
extension = Ext()


class OpenClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.i = self.bot.items
        self.st = []

        self.rewards_moon = self.bot.config['attribute']['moon']

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

        self.list_stickers = list()
        for k, v in self.bot.stickers.items():
            self.list_stickers += [k] * v[1]

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='moon', aliases=['lua'])
    async def moon(self, ctx):
        """Abra um presente para liberar seu giftcard."""
        if ctx.invoked_subcommand is None:
            if ctx.guild.id in self.bot.moon_bag:
                if self.bot.moon_bag[ctx.guild.id] < 1:
                    return await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem moon bag disponiveis!`"
                                          f"\n`TODAS AS MOON BAG FORAM PEGAS, AGUARDE UMA NOVA MOON BAG DROPAR E FIQUE"
                                          f" ATENTO!`")

                self.bot.moon_bag[ctx.guild.id] -= 1
                cl = await self.bot.db.cd("users")
                query = {"$inc": {f"inventory.moon_bag": 1}}
                await cl.update_one({"user_id": ctx.author.id}, query)
                await ctx.send(f"<a:fofo:524950742487007233>│✨ **VOCE PEGOU** ✨ "
                               f"{self.bot.items['moon_bag'][0]} `1` `{self.bot.items['moon_bag'][1]}`\n")

            else:
                await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem moon bag disponiveis...`\n"
                               f"**OBS:** se eu for reiniciada, todas as moon bag disponiveis sao resetadas. "
                               f"Isso é feito por medidas de segurança da minha infraestrutura!")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @moon.command(name='phase', aliases=['fase', 'p', 'f'])
    async def _phase(self, ctx):
        data = get_moon()
        msg = f"<:confirmed:721581574461587496>│`Moon Phase:` **{data[0]}** -  `Moon Position:` **{data[1]}**"
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @moon.command(name='open', aliases=['abrir', 'o', 'a'])
    async def _open(self, ctx, amount=None):
        if amount is None:
            return await ctx.send('<:alert:739251822920728708>│`Insira a quantidade de MOON BAGS que deseja usar!`\n'
                                  '**NOTA:** `Quanto mais voce usar, mais chance de ganhar!`')

        try:
            amount_test = int(amount)
        except ValueError:
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você precisa dizer um numero.` '
                                  '**COMANDO CANCELADO**')

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if "moon_bag" not in update_user['inventory'].keys():
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não tem MOON BAG no seu inventario.` '
                                  '**COMANDO CANCELADO**')

        if update_user['inventory']["moon_bag"] < amount_test:
            return await ctx.send(f'<:negate:721581573396496464>│`Desculpe, você não tem {amount_test} MOON BAG no '
                                  f'seu inventario.` **COMANDO CANCELADO**')

        update_user['inventory']["moon_bag"] -= amount_test
        if update_user['inventory']["moon_bag"] < 1:
            del update_user['inventory']["moon_bag"]
        await self.bot.db.update_data(data_user, update_user, 'users')

        # ESCOLHENDO O PREMIO:
        list_items, data = [], get_moon()
        for i_, amount in self.rewards_moon[data[0]].items():
            list_items += [i_] * amount
        reward = choice(list_items)

        numbers, bonus = [int(n) for n in str(data[1]).replace(".", "")], 0
        for n in numbers:
            bonus += n

        if self.bot.event_special:
            bonus += 15

        if randint(1, 100) + amount_test + bonus > 95:  # 5% + bonus + amount

            msg = f"{self.bot.items[reward][0]} `{1}` `{self.bot.items[reward][1]}`"
            embed = discord.Embed(title='🎊 **PARABENS** 🎉 VOCÊ DROPOU', color=self.bot.color, description=msg)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

            msg = await ctx.send("<a:loading:520418506567843860>│`SALVANDO SEU PREMIO...`")
            await sleep(3)
            await msg.delete()

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory'][reward] += 1
            except KeyError:
                update['inventory'][reward] = 1
            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f"<:confirmed:721581574461587496>│`PREMIO SALVO COM SUCESSO!`", delete_after=5.0)

        else:
            await ctx.send(f"> `VOCE NAO ACHOU NADA DENTRO DA(S)` **{amount_test}** `MOON BAG(S)`", delete_after=30.0)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @moon.command(name='check', aliases=['c'])
    async def _check(self, ctx):
        data = get_moon()

        numbers, bonus = [int(n) for n in str(data[1]).replace(".", "")], 0
        for n in numbers:
            bonus += n

        msg = f"\n".join([f"{self.i[k][0]} `1` `{self.i[k][1]}`" for k, v in self.rewards_moon[data[0]].items()])
        msg += f"\n\n`CONSIGA OS ITENS COM O COMANDO:` **ASH MOON OPEN**\n" \
               f"`BONUS ATUAL:`  **{5 + bonus}% + 1%** `para cada MOON BAG usada.`"
        if self.bot.event_special:
            msg += f"\n`BONUS ESPECIAL:` **15%** ({self.bot.event_now})"
        title = f"MOON BAG DE: {data[0].upper()}"
        embed = discord.Embed(title=title, color=self.bot.color, description=msg)
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url="{}".format(ctx.author.avatar_url))
        embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=3600))
    @commands.command(name='pick', aliases=['pegar'])
    async def pick(self, ctx):
        """Abra um presente para liberar seu giftcard."""
        if ctx.guild.id in self.bot.sticker:
            if self.bot.sticker[ctx.guild.id] < 1:
                return await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem figurinhas disponiveis!`\n"
                                      f"`TODAS AS FIGURINHAS FORAM PEGAS, AGUARDE UMA NOVA FIGURINHA DROPAR E FIQUE "
                                      f"ATENTO!`")

            data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            self.bot.sticker[ctx.guild.id] -= 1
            _STICKER = choice(self.list_stickers)
            _NAME = self.bot.stickers[_STICKER][0]
            _RARITY = self.bot.stickers[_STICKER][1]
            _TYPE = self.bot.stickers[_STICKER][2]
            _OBS = "" if _RARITY >= 10 else "\n<a:confet:853247252998389763> `E AINDA FOI UMA FIGURINHA PREMIADA!`" \
                                            "\n<a:stars:853247252389429278> `>> VOCE GANHOU 5 BLESSED ETHERNYAS <<` " \
                                            "<a:stars:853247252389429278>"
            _TITLE = f"🎊 **PARABENS** 🎉 \n**VOCÊ GANHOU A FIGURINHA:**\n**{_NAME.upper()}**{_OBS}" \
                     f"\n```\nAproveite e olhe seus albuns\n com o comando: ash sticker```"

            if _STICKER in data_user["stickers"].keys():
                await ctx.send(f">>> <a:blue:525032762256785409> `VOCE TIROU UMA FIGURINHA REPETIDA!` "
                               f"**{_NAME.upper()}**")
            else:
                file = discord.File(f"images/stickers/{_TYPE}/{_STICKER}.jpg", filename="reward.png")
                embed = discord.Embed(description=_TITLE, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://reward.png")
                await ctx.send(file=file, embed=embed)

            cl = await self.bot.db.cd("users")
            query = {"$inc": {f"stickers.{_STICKER}": 1, "user.stickers": 1}}
            if _RARITY < 10 and _STICKER not in data_user["stickers"].keys():
                query["$inc"]["true_money.blessed"] = 5
            await cl.update_one({"user_id": ctx.author.id}, query)

        else:
            await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem figurinhas disponiveis...`\n"
                           f"**OBS:** se eu for reiniciada, todas as figurinhas disponiveis sao resetadas. "
                           f"Isso é feito por medidas de segurança da minha infraestrutura!")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='open', aliases=['abrir'])
    async def open(self, ctx):
        """Abra um presente para liberar seu giftcard."""
        if ctx.guild.id in self.bot.box:
            try:
                _BOX = choice(self.bot.box[ctx.guild.id]['boxes'])
            except IndexError:
                return await ctx.send(f"<:negate:721581573396496464>│`Esse Servidor não tem presentes disponiveis!`\n"
                                      f"`TODOS OS PRESENTES FORAM UTILIZADOS, AGUARDE UM NOVO PRESENTE DROPAR E FIQUE "
                                      f"ATENTO!`")
            _I_BOX = self.bot.box[ctx.guild.id]['boxes'].index(_BOX)
            del (self.bot.box[ctx.guild.id]['boxes'][_I_BOX])
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
                _CHEST = choice(self.bot.chests_users[ctx.author.id]['chests'])
            except IndexError:
                return await ctx.send(f"<:negate:721581573396496464>│`Você nao tem mais baus disponiveis...`\n"
                                      f"`TODOS OS BAUS FORAM UTILIZADOS, DROPE UM NOVO BÁU UTILIZANDO O MAXIMO DE "
                                      f"COMANDOS DIFERENTES POSSIVEIS!`")

            _I_CHEST = self.bot.chests_users[ctx.author.id]['chests'].index(_CHEST)
            del (self.bot.chests_users[ctx.author.id]['chests'][_I_CHEST])
            self.bot.chests_users[ctx.author.id]['quant'] -= 1
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            if not data['security']['status']:
                return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS "
                                      "RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

            reward = open_chest(self.bot.chests_l[str(_CHEST)])
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
                _event = await (await self.bot.db.cd("events")).find_one({"_id": self.bot.event_now})
                _event_update = _event
                _event_update["status"] = False
                await self.bot.db.update_data(_event, _event_update, 'events')

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
                _CHEST = choice(self.bot.chests_marry[ctx.author.id]['chests'])
            except IndexError:
                return await ctx.send(f"<:negate:721581573396496464>│`Você nao tem mais baus disponiveis...`\n"
                                      f"`TODOS OS BAUS FORAM UTILIZADOS, DROPE UM NOVO BÁU UTILIZANDO O MAXIMO DE "
                                      f"COMANDOS DIFERENTES POSSIVEIS!`")

            _I_CHEST = self.bot.chests_marry[ctx.author.id]['chests'].index(_CHEST)
            del (self.bot.chests_marry[ctx.author.id]['chests'][_I_CHEST])
            self.bot.chests_marry[ctx.author.id]['quant'] -= 1
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            if not data['security']['status']:
                return await ctx.send("<:negate:721581573396496464>│'`USUARIO DE MACRO / OU USANDO COMANDOS "
                                      "RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'")

            key = self.bot.chests_lm[str(_CHEST)]
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

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if ctx.author.id in self.bot.batalhando:
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
            for _ in range(3):
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

            # item especial
            try:
                items["frozen_letter"] += 1
            except KeyError:
                items["frozen_letter"] = 1

            try:
                update_user['inventory']["frozen_letter"] += 1
            except KeyError:
                update_user['inventory']["frozen_letter"] = 1

            if item_key == "marry_pink":
                for _ in range(3):
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

                # item especial
                try:
                    items["frozen_letter"] += 1
                except KeyError:
                    items["frozen_letter"] = 1

                try:
                    update_user['inventory']["frozen_letter"] += 1
                except KeyError:
                    update_user['inventory']["frozen_letter"] = 1

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

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='read', aliases=["ler"])
    async def read(self, ctx):
        if ctx.invoked_subcommand is None:
            self.status()
            embed = discord.Embed(color=self.bot.color)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="Read Commands:",
                            value=f"{self.st[121]} `letter` Faça a leitura da carta: Frozen Letrer.\n"
                                  f"{self.st[121]} `assemble` Faça a leitura do grimorio: Guide of Spells.\n"
                                  f"{self.st[121]} `aungen` Faça a leitura do grimorio: Aungen’s Book.\n"
                                  f"{self.st[121]} `soul` Faça a leitura do grimorio: Book of Soul.\n"
                                  f"{self.st[121]} `nw` Faça a leitura do grimorio: Neverwinter Book.\n"
                                  f"{self.st[121]} `waffen` Faça a leitura do grimorio: Waffen's Book.\n")
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @read.command(name='letter', aliases=['l'])
    async def _letter(self, ctx, amount: int = 1):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.lendo:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ LENDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "frozen_letter" not in data["inventory"].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if amount > data["inventory"]["frozen_letter"]:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM {amount} FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.lendo.append(ctx.author.id)
        db_player = extension.set_player(ctx.author, copy.deepcopy(data))
        data_xp = calc_xp(db_player['xp'], db_player['level'])
        ini, end = amount + (db_player["intelligence"] // 15), (5 * amount) + (db_player["intelligence"] // 15)
        perc = randint(ini, end)
        if perc > 50 and amount < 5:
            perc = 50
        xpm = data_xp[1] - data_xp[2]
        xpr = int(xpm / 100 * perc)

        if update["rpg"]["intelligence"] < 500:  # max 500
            update["rpg"]["intelligence"] += 1

        update["inventory"]["frozen_letter"] -= amount
        if update["inventory"]["frozen_letter"] < 1:
            del update["inventory"]["frozen_letter"]
        await self.bot.db.update_data(data, update, 'users')
        await self.bot.data.add_xp(ctx, xpr)

        seconds = 10
        text = f"<a:loading:520418506567843860>|`A leitura termina em` **{seconds * amount}** `segundos...`"
        embed = discord.Embed(color=self.bot.color, description=text)
        msg = await ctx.send(embed=embed)
        await sleep(seconds * amount)
        await msg.delete()

        if ctx.author.id in self.bot.lendo:
            self.bot.lendo.remove(ctx.author.id)

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        _class = data_user["rpg"]["class_now"]
        _db_class = data_user["rpg"]["sub_class"][_class]
        percent = calc_xp(int(_db_class['xp']), int(_db_class['level']))  # XP / LEVEL
        if _db_class['xp'] < 32:
            new_xp = f"{_db_class['xp']} / {percent[2]} | {percent[0] * 2} / 100%"
        else:
            new_xp = f"{_db_class['xp'] - percent[2]} / {percent[1] - percent[2]} | {percent[0] * 2} / 100%"
        text = f"**XP:** {new_xp}\n`{'█' * percent[0]}{'-' * (50 - percent[0])}`"
        embed = discord.Embed(color=self.bot.color, description=text)
        await ctx.send(embed=embed, delete_after=5.0)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @read.command(name='assemble')
    async def _assemble(self, ctx, amount: int = 1):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.lendo:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ LENDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "frozen_letter" not in data["inventory"].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if amount > data["inventory"]["frozen_letter"]:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM {amount} FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        recipes = ["potion_of_life", "potion_of_love", "celestial_cover_boots_divine",
                   "celestial_platinum_boots_divine", "celestial_leather_boots_divine"]

        if include(recipes, update["recipes"]):
            msg = f'<:alert:739251822920728708>│`VOCE JÁ TERMINOU DE LER ESSE GRIMORIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _INT = 50 - (amount // 2)
        if data['rpg']['intelligence'] < _INT:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM` **{_INT}** `pontos de inteligencia para ler ' \
                  f'esse grimorio`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.lendo.append(ctx.author.id)
        update["inventory"]["frozen_letter"] -= amount
        if update["inventory"]["frozen_letter"] < 1:
            del update["inventory"]["frozen_letter"]

        chance, msg_return, craft = randint(1, 100), False, None
        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            craft = choice(recipes)
            if craft not in update["recipes"]:
                msg_return = True
                update["recipes"].append(craft)
            else:
                try:
                    update['inventory']["unsealed_stone"] += 1
                except KeyError:
                    update['inventory']["unsealed_stone"] = 1
                icon, name = self.bot.items["unsealed_stone"][0], self.bot.items["unsealed_stone"][1]
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCE NAO CONSEGUIU UM CRAFT, MAS ACHOU UM` '
                               f'{icon} ✨ **1 {name.upper()}** ✨ `NO MEIO DO LIVRO`')
        await self.bot.db.update_data(data, update, 'users')

        seconds = 10
        text = f"<a:loading:520418506567843860>|`A leitura termina em` **{seconds * amount}** `segundos...`"
        file = discord.File('images/grimorios/Assemble Guide of Spells.jpg', filename="grimorio.jpg")
        embed = discord.Embed(title=text, color=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_image(url="attachment://grimorio.jpg")
        msg = await ctx.send(file=file, embed=embed)

        await sleep(seconds * amount)
        await msg.delete()

        if ctx.author.id in self.bot.lendo:
            self.bot.lendo.remove(ctx.author.id)

        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            if msg_return:
                craft = craft.replace("_", " ").upper()
                text = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Voce liberou o craft:`\n**{craft}**"
                file = discord.File('images/elements/success.jpg', filename="success.jpg")
                embed = discord.Embed(title=text, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://success.jpg")
                await ctx.send(file=file, embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @read.command(name='aungen', aliases=['a'])
    async def _aungen(self, ctx, amount: int = 1):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.lendo:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ LENDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "frozen_letter" not in data["inventory"].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if amount > data["inventory"]["frozen_letter"]:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM {amount} FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        recipes = ["potion_of_death", "potion_of_death", "celestial_cover_gloves_divine",
                   "celestial_platinum_gloves_divine", "celestial_leather_gloves_divine"]

        if include(recipes, update["recipes"]):
            msg = f'<:alert:739251822920728708>│`VOCE JÁ TERMINOU DE LER ESSE GRIMORIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _INT = 75 - (amount // 2)
        if data['rpg']['intelligence'] < _INT:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM` **{_INT}** `pontos de inteligencia para ler ' \
                  f'esse grimorio`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.lendo.append(ctx.author.id)
        update["inventory"]["frozen_letter"] -= amount
        if update["inventory"]["frozen_letter"] < 1:
            del update["inventory"]["frozen_letter"]

        chance, msg_return, craft = randint(1, 100), False, None
        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            craft = choice(recipes)
            if craft not in update["recipes"]:
                msg_return = True
                update["recipes"].append(craft)
            else:
                try:
                    update['inventory']["unsealed_stone"] += 1
                except KeyError:
                    update['inventory']["unsealed_stone"] = 1
                icon, name = self.bot.items["unsealed_stone"][0], self.bot.items["unsealed_stone"][1]
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCE NAO CONSEGUIU UM CRAFT, MAS ACHOU UM` '
                               f'{icon} ✨ **1 {name.upper()}** ✨ `NO MEIO DO LIVRO`')
        await self.bot.db.update_data(data, update, 'users')

        seconds = 10
        text = f"<a:loading:520418506567843860>|`A leitura termina em` **{seconds * amount}** `segundos...`"
        file = discord.File('images/grimorios/Aungens Book.jpg', filename="grimorio.jpg")
        embed = discord.Embed(title=text, color=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_image(url="attachment://grimorio.jpg")
        msg = await ctx.send(file=file, embed=embed)

        await sleep(seconds * amount)
        await msg.delete()

        if ctx.author.id in self.bot.lendo:
            self.bot.lendo.remove(ctx.author.id)

        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            if msg_return:
                craft = craft.replace("_", " ").upper()
                text = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Voce liberou o craft:`\n**{craft}**"
                file = discord.File('images/elements/success.jpg', filename="success.jpg")
                embed = discord.Embed(title=text, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://success.jpg")
                await ctx.send(file=file, embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @read.command(name='soul', aliases=['s'])
    async def _soul(self, ctx, amount: int = 1):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.lendo:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ LENDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "frozen_letter" not in data["inventory"].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if amount > data["inventory"]["frozen_letter"]:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM {amount} FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        recipes = ["potion_of_soul", "potion_of_rejuvenation", "celestial_cover_helmet_divine",
                   "celestial_platinum_helmet_divine", "celestial_leather_helmet_divine"]

        if include(recipes, update["recipes"]):
            msg = f'<:alert:739251822920728708>│`VOCE JÁ TERMINOU DE LER ESSE GRIMORIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _INT = 25 - (amount // 2)
        if data['rpg']['intelligence'] < _INT:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM` **{_INT}** `pontos de inteligencia para ler ' \
                  f'esse grimorio`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.lendo.append(ctx.author.id)
        update["inventory"]["frozen_letter"] -= amount
        if update["inventory"]["frozen_letter"] < 1:
            del update["inventory"]["frozen_letter"]

        chance, msg_return, craft = randint(1, 100), False, None
        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            craft = choice(recipes)
            if craft not in update["recipes"]:
                msg_return = True
                update["recipes"].append(craft)
            else:
                try:
                    update['inventory']["unsealed_stone"] += 1
                except KeyError:
                    update['inventory']["unsealed_stone"] = 1
                icon, name = self.bot.items["unsealed_stone"][0], self.bot.items["unsealed_stone"][1]
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCE NAO CONSEGUIU UM CRAFT, MAS ACHOU UM` '
                               f'{icon} ✨ **1 {name.upper()}** ✨ `NO MEIO DO LIVRO`')
        await self.bot.db.update_data(data, update, 'users')

        seconds = 10 - (amount // 2)
        text = f"<a:loading:520418506567843860>|`A leitura termina em` **{seconds * amount}** `segundos...`"
        file = discord.File('images/grimorios/Book of Soul.jpg', filename="grimorio.jpg")
        embed = discord.Embed(title=text, color=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_image(url="attachment://grimorio.jpg")
        msg = await ctx.send(file=file, embed=embed)

        await sleep(seconds * amount)
        await msg.delete()

        if ctx.author.id in self.bot.lendo:
            self.bot.lendo.remove(ctx.author.id)

        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            if msg_return:
                craft = craft.replace("_", " ").upper()
                text = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Voce liberou o craft:`\n**{craft}**"
                file = discord.File('images/elements/success.jpg', filename="success.jpg")
                embed = discord.Embed(title=text, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://success.jpg")
                await ctx.send(file=file, embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @read.command(name='nw', aliases=['n'])
    async def _nw(self, ctx, amount: int = 1):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.lendo:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ LENDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "frozen_letter" not in data["inventory"].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if amount > data["inventory"]["frozen_letter"]:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM {amount} FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        recipes = ["potion_of_weakening", "potion_of_weakening", "celestial_cover_leggings_divine",
                   "celestial_platinum_leggings_divine", "celestial_leather_leggings_divine",
                   "herb_red", "herb_green", "herb_blue"]

        if include(recipes, update["recipes"]):
            msg = f'<:alert:739251822920728708>│`VOCE JÁ TERMINOU DE LER ESSE GRIMORIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _INT = 100 - (amount // 2)
        if data['rpg']['intelligence'] < _INT:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM` **{_INT}** `pontos de inteligencia para ler ' \
                  f'esse grimorio`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.lendo.append(ctx.author.id)
        update["inventory"]["frozen_letter"] -= amount
        if update["inventory"]["frozen_letter"] < 1:
            del update["inventory"]["frozen_letter"]

        chance, msg_return, craft = randint(1, 100), False, None
        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            craft = choice(recipes)
            if craft not in update["recipes"]:
                msg_return = True
                update["recipes"].append(craft)
            else:
                try:
                    update['inventory']["unsealed_stone"] += 1
                except KeyError:
                    update['inventory']["unsealed_stone"] = 1
                icon, name = self.bot.items["unsealed_stone"][0], self.bot.items["unsealed_stone"][1]
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCE NAO CONSEGUIU UM CRAFT, MAS ACHOU UM` '
                               f'{icon} ✨ **1 {name.upper()}** ✨ `NO MEIO DO LIVRO`')
        await self.bot.db.update_data(data, update, 'users')

        seconds = 10
        text = f"<a:loading:520418506567843860>|`A leitura termina em` **{seconds * amount}** `segundos...`"
        file = discord.File('images/grimorios/Neverwinter Book.jpg', filename="grimorio.jpg")
        embed = discord.Embed(title=text, color=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_image(url="attachment://grimorio.jpg")
        msg = await ctx.send(file=file, embed=embed)

        await sleep(seconds * amount)
        await msg.delete()

        if ctx.author.id in self.bot.lendo:
            self.bot.lendo.remove(ctx.author.id)

        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            if msg_return:
                craft = craft.replace("_", " ").upper()
                text = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Voce liberou o craft:`\n**{craft}**"
                file = discord.File('images/elements/success.jpg', filename="success.jpg")
                embed = discord.Embed(title=text, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://success.jpg")
                await ctx.send(file=file, embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @read.command(name='waffen', aliases=['w'])
    async def _waffen(self, ctx, amount: int = 1):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.lendo:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ LENDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "frozen_letter" not in data["inventory"].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if amount > data["inventory"]["frozen_letter"]:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM {amount} FROZEN LETTER NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        recipes = ["celestial_necklace_sealed", "celestial_earring_sealed", "salvation", "celestial_ring_sealed",
                   "celestial_cover_breastplate_divine", "celestial_platinum_breastplate_divine",
                   "celestial_leather_breastplate_divine", "feather_white", "feather_gold", "feather_black"]

        if include(recipes, update["recipes"]):
            msg = f'<:alert:739251822920728708>│`VOCE JÁ TERMINOU DE LER ESSE GRIMORIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _INT = 150 - (amount // 2)
        if data['rpg']['intelligence'] < _INT:
            msg = f'<:negate:721581573396496464>│`VOCE NÃO TEM` **{_INT}** `pontos de inteligencia para ler ' \
                  f'esse grimorio`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.lendo.append(ctx.author.id)
        update["inventory"]["frozen_letter"] -= amount
        if update["inventory"]["frozen_letter"] < 1:
            del update["inventory"]["frozen_letter"]

        chance, msg_return, craft = randint(1, 100), False, None
        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            craft = choice(recipes)
            if craft not in update["recipes"]:
                msg_return = True
                update["recipes"].append(craft)
            else:
                try:
                    update['inventory']["unsealed_stone"] += 1
                except KeyError:
                    update['inventory']["unsealed_stone"] = 1
                icon, name = self.bot.items["unsealed_stone"][0], self.bot.items["unsealed_stone"][1]
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCE NAO CONSEGUIU UM CRAFT, MAS ACHOU UM` '
                               f'{icon} ✨ **1 {name.upper()}** ✨ `NO MEIO DO LIVRO`')
        await self.bot.db.update_data(data, update, 'users')

        seconds = 10
        text = f"<a:loading:520418506567843860>|`A leitura termina em` **{seconds * amount}** `segundos...`"
        file = discord.File('images/grimorios/Waffens Book.jpg', filename="grimorio.jpg")
        embed = discord.Embed(title=text, color=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_image(url="attachment://grimorio.jpg")
        msg = await ctx.send(file=file, embed=embed)

        await sleep(seconds * amount)
        await msg.delete()

        if ctx.author.id in self.bot.lendo:
            self.bot.lendo.remove(ctx.author.id)

        if chance <= 5 + (amount // 2) + (data['rpg']['intelligence'] // 50):
            if msg_return:
                craft = craft.replace("_", " ").upper()
                text = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Voce liberou o craft:`\n**{craft}**"
                file = discord.File('images/elements/success.jpg', filename="success.jpg")
                embed = discord.Embed(title=text, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://success.jpg")
                await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(OpenClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mOPEN\033[1;32m foi carregado com sucesso!\33[m')
