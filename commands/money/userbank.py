import discord

from random import choice, randint
from asyncio import sleep, TimeoutError
from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.utility import convert_item_name, paginator

coin, cost, plus = 0, 0, 0
git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class UserBank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.money = 0
        self.gold = 0
        self.silver = 0
        self.bronze = 0
        self.items = self.bot.config['attribute']['shop']
        self.items_shopping = self.bot.config['attribute']['shopping']
        self.items_shop_vote = self.bot.config['attribute']['shop_vote']
        self.rewards_lucky = self.bot.config['attribute']['rewards_lucky']

    @staticmethod
    def format_num(num, f=False):
        a = '{:,.0f}'.format(float(num)) if not f else '{:,.2f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='wallet', aliases=['carteira'])
    async def wallet(self, ctx):
        """Comando usado para verificar quanto dinheiro você tem
        Use ash wallet"""
        if ctx.invoked_subcommand is None:
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            self.money = data['treasure']['money']
            self.gold = data['treasure']['gold']
            self.silver = data['treasure']['silver']
            self.bronze = data['treasure']['bronze']
            blessed = self.format_num(data['true_money']['blessed'])
            fragment = self.format_num(data['true_money']['fragment'])
            real = self.format_num(data['true_money']['real'], True)
            adfly = self.format_num(data['true_money']['adfly'])
            d = self.format_num(self.money, True)
            msg = f"<:coins:519896825365528596>│ **{ctx.author}** No total  você tem **R$ {d}** de `ETHERNYAS` na " \
                  f"sua carteira!\n {self.bot.money[2]} **{self.format_num(self.gold)}** | " \
                  f"{self.bot.money[1]} **{self.format_num(self.silver)}** | " \
                  f"{self.bot.money[0]} **{self.format_num(self.bronze)}**\n" \
                  f"**{blessed}** - `Blessed Ethernyas` | **{fragment}** - `Fragmentos de Blessed Ethernyas`\n" \
                  f"**R$ {real}** - `Reais` | **{adfly}** - `ADFLY/ADLINK COMMANDS`"
            await ctx.send(msg)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @wallet.group(name='convert', aliases=['c'])
    async def _add(self, ctx, amount: int = 0, money: str = None):
        if amount is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia.`")
        if amount < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if money is None and not data_user["config"]["vip"]:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer qual moeda quer converter.`")

        if update_user["true_money"]["fragment"] < amount * 1000:
            quantidade = update_user["true_money"]["fragment"] // 1000
            return await ctx.send(f"<:alert:739251822920728708>│`Você só pode fazer` **{quantidade}** `conversões.`")

        if not data_user["config"]["vip"]:
            if money.lower() not in ["blessed", "real", "reais"]:
                return await ctx.send("<:alert:739251822920728708>│`Você só pode converter para:` **BLESSED e REAIS!**")

        update_user["true_money"]["fragment"] -= 1000 * amount
        if not data_user["config"]["vip"]:
            if money.lower() == "blessed":
                update_user["true_money"]["blessed"] += amount
            else:
                update_user["true_money"]["real"] += amount
        else:
            update_user["true_money"]["blessed"] += amount
            update_user["true_money"]["real"] += amount
        await self.bot.db.update_data(data_user, update_user, 'users')

        if not data_user["config"]["vip"]:
            extra = "Blessed Ethernyas" if money == "blessed" else "Reais"
            return await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 `Você converteu:` "
                                  f"**{amount * 1000}** `fragmentos de ethernyas, por:` **{amount} {extra}!**")
        await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 `Você converteu:` "
                       f"**{amount * 1000}** `fragmentos de ethernyas, por:` **{amount} [Reais e Blessed Ethernyas]!**")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='shop', aliases=['buy', 'comprar', 'loja'])
    async def shop(self, ctx, quant: int = None, *, item=None):
        """A lojinha da ashley, compre itens e crafts que voce ainda nao conseguiu pegar em outros comandos."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if item is None:
            await ctx.send(f"<:alert:739251822920728708>│`ITENS DISPONIVEIS PARA COMPRA ABAIXO`\n"
                           f"**EXEMPLO:** `USE` **ASH SHOP 50 FICHAS** `PARA COMPRAR 50 FICHAS!`")
            embed = ['Loja de Itens:', self.bot.color, 'Lista: \n']
            if quant is None:
                return await paginator(self.bot, self.items, self.items, embed, ctx)
            else:
                num = quant - 1 if quant > 0 else 0
                return await paginator(self.bot, self.items, self.items, embed, ctx, num)

        if quant < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")

        name = None
        for key in self.items.keys():
            if key.lower() == item.lower():
                name = key

        if name is None:
            return await ctx.send("<:alert:739251822920728708>│`ESSE ITEM NAO EXISTE OU NAO ESTA DISPONIVEL!`")

        if update['treasure']['money'] < self.items[name] * int(quant):
            return await ctx.send("<:alert:739251822920728708>│`VOCE NAO TEM ETHERNYAS SUFICIENTES DISPONIVEIS!`")

        item_reward = None
        for k, v in self.bot.items.items():
            if v[1] == name:
                item_reward = k
        if item_reward is None:
            return await ctx.send("<:negate:721581573396496464>│`ITEM NAO ENCONTRADO!`")

        try:
            update['inventory'][item_reward] += int(quant)
        except KeyError:
            update['inventory'][item_reward] = int(quant)

        update['treasure']['money'] -= self.items[name] * int(quant)
        await self.bot.db.update_data(data, update, 'users')
        a = '{:,.2f}'.format(float(self.items[name] * int(quant)))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        await ctx.send(f"<:confirmed:721581574461587496>|`SUA COMPRA FOI FEITA COM SUCESSO` **{quant}** "
                       f"`{name.upper()} ADICIONADO NO SEU INVENTARIO COM SUCESSO QUE CUSTOU` "
                       f"**R$ {d}** `ETHERNYAS`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='shopping', aliases=['sp'])
    async def shopping(self, ctx, quant: int = None, *, item=None):
        """A lojinha da ashley, compre itens e crafts que voce ainda nao conseguiu pegar em outros comandos."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if item is None:
            await ctx.send(f"<:alert:739251822920728708>│`ITENS DISPONIVEIS PARA COMPRA ABAIXO`\n"
                           f"**EXEMPLO:** `USE` **ASH SHOPPING 5 ALGEL WING** `PARA COMPRAR 5 ALGEL WING!`")
            embed = ['Shopping Premium:', self.bot.color, 'Lista: \n']

            if quant is None:
                return await paginator(self.bot, self.items_shopping, self.items_shopping, embed, ctx)

            else:
                num = quant - 1 if quant > 0 else 0
                return await paginator(self.bot, self.items_shopping, self.items_shopping, embed, ctx, num)

        if quant < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")

        name = None
        for key in self.items_shopping.keys():
            if key.lower() == item.lower():
                name = key

        if name is None:
            return await ctx.send("<:alert:739251822920728708>│`ESSE ITEM NAO EXISTE OU NAO ESTA DISPONIVEL!`")

        if update['true_money']['blessed'] < self.items_shopping[name] * int(quant):
            return await ctx.send("<:alert:739251822920728708>│`VOCE NAO TEM BLESSED ETHERNYAS SUFICIENTES!`")

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        item_reward, type_item = None, None
        for i in equips_list:
            if i[1]["name"] == name:
                item_reward, type_item = i[0], "equip"

        if item_reward is None:
            for k, v in self.bot.items.items():
                if v[1] == name:
                    item_reward, type_item = k, "inventory"

        if type_item == "inventory":
            try:
                update['inventory'][item_reward] += int(quant)
            except KeyError:
                update['inventory'][item_reward] = int(quant)

        if type_item == "equip":
            try:
                update['rpg']['items'][item_reward] += int(quant)
            except KeyError:
                update['rpg']['items'][item_reward] = int(quant)

        update['true_money']['blessed'] -= self.items_shopping[name] * int(quant)
        await self.bot.db.update_data(data, update, 'users')
        a = '{:,.2f}'.format(float(self.items_shopping[name] * int(quant)))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        await ctx.send(f"<:confirmed:721581574461587496>|`SUA COMPRA FOI FEITA COM SUCESSO` **{quant}** "
                       f"`{name.upper()} ADICIONADO NO SEU INVENTARIO COM SUCESSO QUE CUSTOU` "
                       f"**R$ {d}** `BLESSED ETHERNYAS`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='shop_vote', aliases=['sv'])
    async def shop_vote(self, ctx, quant: int = None, *, item=None):
        """A lojinha da ashley, compre itens e crafts que voce ainda nao conseguiu pegar em outros comandos."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if item is None:
            await ctx.send(f"<:alert:739251822920728708>│`ITENS DISPONIVEIS PARA COMPRA ABAIXO`\n"
                           f"**EXEMPLO:** `USE` **ASH SV 1 ALGEL WING** `PARA COMPRAR 1 ALGEL WING!`")
            embed = ['Shop Vote:', self.bot.color, 'Lista: \n']

            if quant is None:
                return await paginator(self.bot, self.items_shop_vote, self.items_shop_vote, embed, ctx)

            else:
                num = quant - 1 if quant > 0 else 0
                return await paginator(self.bot, self.items_shop_vote, self.items_shop_vote, embed, ctx, num)

        if quant < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")

        name = None
        for key in self.items_shop_vote.keys():
            if key.lower() == item.lower():
                name = key

        if name is None:
            return await ctx.send("<:alert:739251822920728708>│`ESSE ITEM NAO EXISTE OU NAO ESTA DISPONIVEL!`")

        if 'vote_coin' not in update['inventory'].keys():
            return await ctx.send("<:alert:739251822920728708>│`VOCE NAO TEM VOCE COINS SUFICIENTES!`")

        if update['inventory']['vote_coin'] < self.items_shop_vote[name] * int(quant):
            return await ctx.send("<:alert:739251822920728708>│`VOCE NAO TEM VOCE COINS SUFICIENTES!`")

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        item_reward, type_item = None, None
        for i in equips_list:
            if i[1]["name"] == name:
                item_reward, type_item = i[0], "equip"

        if item_reward is None:
            for k, v in self.bot.items.items():
                if v[1] == name:
                    item_reward, type_item = k, "inventory"

        if type_item == "inventory":
            try:
                update['inventory'][item_reward] += int(quant)
            except KeyError:
                update['inventory'][item_reward] = int(quant)

        if type_item == "equip":
            try:
                update['rpg']['items'][item_reward] += int(quant)
            except KeyError:
                update['rpg']['items'][item_reward] = int(quant)

        update['inventory']['vote_coin'] -= self.items_shop_vote[name] * int(quant)
        if update['inventory']['vote_coin'] <= 0:
            del update['inventory']['vote_coin']

        await self.bot.db.update_data(data, update, 'users')
        d = self.items_shop_vote[name] * int(quant)
        await ctx.send(f"<:confirmed:721581574461587496>|`SUA COMPRA FOI FEITA COM SUCESSO` **{quant}** "
                       f"`{name.upper()} ADICIONADO NO SEU INVENTARIO COM SUCESSO QUE CUSTOU` **{d}** `VOTE COINS`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='pay', aliases=['pagar'])
    async def pay(self, ctx, member: discord.Member = None, amount: int = None):
        """Pague aquele dinheiro que voce ficou devendo"""
        if member is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa mencionar alguem.`")
        if amount is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia.`")
        if amount < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")
        if member.id == ctx.author.id:
            return await ctx.send("<:alert:739251822920728708>│`Você não pode pagar a si mesmo.`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        data_member = await self.bot.db.get_data("user_id", member.id, "users")
        update_user = data_user
        update_member = data_member
        if data_member is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)
        if member.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`O membro está jogando, aguarde para quando"
                                  " ele estiver livre!`")

        data_guild_native = await self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        data_guild_native_member = await self.bot.db.get_data("guild_id", data_member['guild_id'], "guilds")
        update_guild_native = data_guild_native
        update_guild_native_member = data_guild_native_member

        if data_user['treasure']["money"] >= amount:
            update_user['treasure']['money'] -= amount
            update_guild_native['data'][f'total_money'] -= amount
            update_member['treasure']['money'] += amount
            update_guild_native_member['data'][f'total_money'] += amount
            await self.bot.db.update_data(data_user, update_user, 'users')
            await self.bot.db.update_data(data_member, update_member, 'users')
            await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')
            await self.bot.db.update_data(data_guild_native_member, update_guild_native_member, 'guilds')
            await ctx.send(f'<:coins:519896825365528596>│`PARABENS, VC PAGOU R$ {self.format_num(amount)},00 '
                           f'DE ETHERNYAS PARA {member.name} COM SUCESSO!`')
            await self.bot.data.add_sts(ctx.author, "pay", 1)
        else:
            await ctx.send(f"<:alert:739251822920728708>│`VOCÊ NÃO TEM ESSE VALOR DISPONIVEL DE "
                           f"ETHERNYAS!`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='give', aliases=['dar'])
    async def give(self, ctx, member: discord.Member = None, amount: int = None, *, item=None):
        """De aquele item de craft como presente para um amigo seu ou troque com alguem."""
        if member is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa mencionar alguem!`")
        if amount is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia!`")
        if amount < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")
        if member.id == ctx.author.id:
            return await ctx.send("<:alert:739251822920728708>│`Você não pode dar um item a si mesmo!`")
        if item is None:
            return await ctx.send("<:alert:739251822920728708>│`Você esqueceu de falar o nome do item para dar!`")

        item_key = convert_item_name(item, self.bot.items)
        if item_key is None:
            return await ctx.send("<:alert:739251822920728708>│`Item Inválido!`")
        if self.bot.items[item_key][2] is False:
            return await ctx.send("<:alert:739251822920728708>│`Você não pode dar esse tipo de item.`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        data_member = await self.bot.db.get_data("user_id", member.id, "users")
        update_user = data_user
        update_member = data_member

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if data_member is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        if member.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`O membro está jogando, aguarde para quando"
                                  " ele estiver livre!`")

        if member.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`O membro está batalhando!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        item_name = self.bot.items[item_key][1]

        if item_key in data_user['inventory']:
            if data_user['inventory'][item_key] >= amount:
                update_user['inventory'][item_key] -= amount
                if update_user['inventory'][item_key] < 1:
                    del update_user['inventory'][item_key]
                try:
                    update_member['inventory'][item_key] += amount
                except KeyError:
                    update_member['inventory'][item_key] = amount
                await self.bot.db.update_data(data_user, update_user, 'users')
                await self.bot.db.update_data(data_member, update_member, 'users')
                await ctx.send(f'<:confirmed:721581574461587496>│`PARABENS, VC DEU {amount} DE '
                               f'{item_name.upper()} PARA {member.name} COM SUCESSO!`')
                await self.bot.data.add_sts(ctx.author, "give", 1)
            else:
                await ctx.send(f"<:alert:739251822920728708>│`VOCÊ NÃO TEM ESSA QUANTIDADE DISPONIVEL DE "
                               f"{item_name.upper()}!`")
        else:
            await ctx.send(f"<:alert:739251822920728708>│`Você não tem {item_name.upper()} no seu "
                           f"inventario!`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='ticket', aliases=['raspadinha', 'rifa'])
    async def ticket(self, ctx, stone: int = None, upgrade: int = None):
        """raspadinha da sorte da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        global coin, cost, plus

        if upgrade is not None:
            if not data['config']['vip']:
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, Apenas vip pode dizer a porcentagem!`')
            if upgrade < 1 or upgrade > 100:
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, a chance precisa ser entre 1 a 100`')

        n_cost = [500, 75, 25]
        if stone not in [1, 2, 3]:
            return await ctx.send(f"🎫│`Que tipo de` **PEDRA** `voce deseja gastar?"
                                  f" Escolha uma dessas opções abaixo!`\n"
                                  f"**[ ash ticket 1 ]** - `Para` {self.bot.money[0]} "
                                  f"`Custa:` **{n_cost[0]}** "
                                  f"`Bonus de Chance:` **+1%**\n"
                                  f"**[ ash ticket 2 ]** - `Para` {self.bot.money[1]} "
                                  f"`Custa:` **{n_cost[1]}** "
                                  f"`Bonus de Chance:` **+2%**\n"
                                  f"**[ ash ticket 3 ]** - `Para` {self.bot.money[2]} "
                                  f"`Custa:` **{n_cost[2]}** "
                                  f"`Bonus de Chance:` **+3%**")

        else:
            if stone == 1:
                cost = n_cost[0]
                coin = "bronze"
                plus = 1
            if stone == 2:
                cost = n_cost[1]
                coin = "silver"
                plus = 2
            if stone == 3:
                cost = n_cost[2]
                coin = "gold"
                plus = 3

        # quantidade de pedras para retirar
        up = cost * upgrade if upgrade is not None else cost

        if data['treasure'][coin] < up:
            pp = up if upgrade is not None else ""
            return await ctx.send(f'<:negate:721581573396496464>│`Desculpe, você não tem {pp} pedras suficientes.` '
                                  f'**COMANDO CANCELADO**')

        # DATA DO MEMBRO
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        update_user['treasure'][coin] -= up
        if update_user['treasure'][coin] < 0:
            update_user['treasure'][coin] = 0
        await self.bot.db.update_data(data_user, update_user, 'users')

        # DATA NATIVA DO SERVIDOR
        data_guild_native = await self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        if update_guild_native is not None:
            update_guild_native['data'][f"total_{coin}"] -= up
            if update_guild_native['data'][f"total_{coin}"] < 0:
                update_guild_native['data'][f"total_{coin}"] = 0
            await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')

        msg = await ctx.send("<a:loading:520418506567843860>│`RASPANDO TICKET...`")
        await sleep(1)
        await msg.delete()

        awards = self.bot.config['artifacts']
        reward = choice(list(awards.keys()))
        exodia = ["braço_direito", "braço_esquerdo", "perna_direita", "perna_esquerda", "the_one"]
        reliquia = ["anel", "balança", "chave", "colar", "enigma", "olho", "vara"]
        lucky = "EXODIA" if reward in exodia else "RELIQUIA" if reward in reliquia else "ARMADURA"
        a = await ctx.send(f"<:alert:739251822920728708>│`SUA SORTE ESTÁ PARA:` **{lucky}**")

        msg = await ctx.send("<a:loading:520418506567843860>│`SEU PREMIO FOI...`")
        await sleep(3)
        await msg.delete()

        percent = randint(1, 100)
        chance_ar = awards[reward]["chance"]
        chance = 100 * chance_ar + plus / 2 if randint(1, 10) > 5 else 100 * chance_ar + plus
        if upgrade is not None:
            chance = upgrade
        if percent <= chance:
            if reward in data["artifacts"]:
                data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update = data
                try:
                    update['inventory'][reward] += 1
                except KeyError:
                    update['inventory'][reward] = 1
                await self.bot.db.update_data(data, update, 'users')
                await ctx.send(f">>> <a:blue:525032762256785409> `VOCE TIROU UM ARTEFATO` "
                               f"**{self.bot.items[reward][1]}** `REPETIDO, PELO MENOS VOCE GANHOU ESSA "
                               f"RELIQUIA NO SEU INVENTARIO`")

            else:
                file = discord.File(awards[reward]["url"], filename="reward.png")
                embed = discord.Embed(title='VOCÊ GANHOU! 🎊 **PARABENS** 🎉', color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://reward.png")
                await ctx.send(file=file, embed=embed)

                msg = await ctx.send("<a:loading:520418506567843860>│`SALVANDO SEU PREMIO...`")
                await sleep(3)
                await msg.delete()

                data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update = data
                update["artifacts"][reward] = awards[reward]
                await self.bot.db.update_data(data, update, 'users')
                await ctx.send(f"<:confirmed:721581574461587496>│`PREMIO SALVO COM SUCESSO!`", delete_after=5.0)

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            if len(data['artifacts'].keys()) == 24 and not update['vip_free'] and not update['config']['vip']:
                update['true_money']['blessed'] += 20
                try:
                    update['inventory']['vip_coin'] += 1
                except KeyError:
                    update['inventory']['vip_coin'] = 1
                update['vip_free'] = True
                img = choice(git)
                embed = discord.Embed(color=self.bot.color)
                embed.set_image(url=img)
                await ctx.send(embed=embed)
                await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 `VOCE COMPLETOU TODOS OS ARTEFATOS!`"
                               f" ✨ **AGORA VC GANHOU 20 BLESSED ETHERNYA, PRA COMPRAR 1 MÊS DE VIP** ✨")
                await self.bot.db.update_data(data, update, 'users')
                await self.bot.data.add_sts(ctx.author, "ticket", 1)

            if upgrade is not None:
                await ctx.send(f'<:confirmed:721581574461587496>│`Você gastou {up} pedras!`')

        else:
            await ctx.send(f"> `A SORTE NAO ESTAVA COM VOCE`", delete_after=30.0)
        await a.delete()

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='bollash', aliases=['pokebola', 'boll', 'bola'])
    async def bollash(self, ctx, stone: int = None):
        """bola para capitura dos pets da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        global coin, cost, plus

        n_cost = [1000, 150, 50]

        if stone not in [1, 2, 3]:
            return await ctx.send(f"🎫│`Que tipo de` **PEDRA** `voce deseja gastar?"
                                  f" Escolha uma dessas opções abaixo!`\n"
                                  f"**[ ash bollash 1 ]** - `Para` {self.bot.money[0]} "
                                  f"`Custa:` **{n_cost[0]}** "
                                  f"`Bonus de Chance:` **+1%**\n"
                                  f"**[ ash bollash 2 ]** - `Para` {self.bot.money[1]} "
                                  f"`Custa:` **{n_cost[1]}** "
                                  f"`Bonus de Chance:` **+2%**\n"
                                  f"**[ ash bollash 3 ]** - `Para` {self.bot.money[2]} "
                                  f"`Custa:` **{n_cost[2]}** "
                                  f"`Bonus de Chance:` **+3%**")
        else:
            if stone == 1:
                cost = n_cost[0]
                coin = "bronze"
                plus = 1
            if stone == 2:
                cost = n_cost[1]
                coin = "silver"
                plus = 2
            if stone == 3:
                cost = n_cost[2]
                coin = "gold"
                plus = 3

        if data['treasure'][coin] < cost:
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não tem pedras suficientes.` '
                                  '**COMANDO CANCELADO**')

        # DATA DO MEMBRO
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        update_user['treasure'][coin] -= cost
        if update_user['treasure'][coin] < 0:
            update_user['treasure'][coin] = 0
        await self.bot.db.update_data(data_user, update_user, 'users')

        # DATA NATIVA DO SERVIDOR
        data_guild_native = await self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        if update_guild_native is not None:
            update_guild_native['data'][f"total_{coin}"] -= cost
            if update_guild_native['data'][f"total_{coin}"] < 0:
                update_guild_native['data'][f"total_{coin}"] = 0
            await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')

        msg = await ctx.send("<a:loading:520418506567843860>│`TENTANDO DROPAR UMA ASHBOLL...`")
        await sleep(1)
        await msg.delete()

        percent = randint(1, 100)
        chance = 100 * 0.04 + plus / 2 if randint(1, 10) > 5 else 100 * 0.04 + 100 * 0.04 / 2 + plus
        if percent <= chance:

            embed = discord.Embed(title='🎊 **PARABENS** 🎉 VOCÊ DROPOU', color=self.bot.color,
                                  description=f"{self.bot.items['?-Bollash'][0]} `{1}` "
                                              f"`{self.bot.items['?-Bollash'][1]}`")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

            msg = await ctx.send("<a:loading:520418506567843860>│`SALVANDO SEU PREMIO...`")
            await sleep(3)
            await msg.delete()

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory']['?-Bollash'] += 1
            except KeyError:
                update['inventory']['?-Bollash'] = 1
            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f"<:confirmed:721581574461587496>│`PREMIO SALVO COM SUCESSO!`", delete_after=5.0)
            await self.bot.data.add_sts(ctx.author, "bollash", 1)

        else:
            await ctx.send(f"> `A SORTE NAO ESTAVA COM VOCE`", delete_after=30.0)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='stone', aliases=['pedra'])
    async def stone(self, ctx, stone: int = None):
        """pedra da liberação usada para tirar o selo das armaduras seladas."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        global coin, cost, plus

        n_cost = [2000, 300, 100]

        if stone not in [1, 2, 3]:
            return await ctx.send(f"🎫│`Que tipo de` **PEDRA** `voce deseja gastar?"
                                  f" Escolha uma dessas opções abaixo!`\n"
                                  f"**[ ash stone 1 ]** - `Para` {self.bot.money[0]} "
                                  f"`Custa:` **{n_cost[0]}** "
                                  f"`Bonus de Chance:` **+1%**\n"
                                  f"**[ ash stone 2 ]** - `Para` {self.bot.money[1]} "
                                  f"`Custa:` **{n_cost[1]}** "
                                  f"`Bonus de Chance:` **+2%**\n"
                                  f"**[ ash stone 3 ]** - `Para` {self.bot.money[2]} "
                                  f"`Custa:` **{n_cost[2]}** "
                                  f"`Bonus de Chance:` **+3%**")
        else:
            if stone == 1:
                cost = n_cost[0]
                coin = "bronze"
                plus = 1
            if stone == 2:
                cost = n_cost[1]
                coin = "silver"
                plus = 2
            if stone == 3:
                cost = n_cost[2]
                coin = "gold"
                plus = 3

        if data['treasure'][coin] < cost:
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não tem pedras suficientes.` '
                                  '**COMANDO CANCELADO**')

        # DATA DO MEMBRO
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        update_user['treasure'][coin] -= cost
        if update_user['treasure'][coin] < 0:
            update_user['treasure'][coin] = 0
        await self.bot.db.update_data(data_user, update_user, 'users')

        # DATA NATIVA DO SERVIDOR
        data_guild_native = await self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        if update_guild_native is not None:
            update_guild_native['data'][f"total_{coin}"] -= cost
            if update_guild_native['data'][f"total_{coin}"] < 0:
                update_guild_native['data'][f"total_{coin}"] = 0
            await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')

        msg = await ctx.send("<a:loading:520418506567843860>│`TENTANDO DROPAR UMA UNSEALED STONE...`")
        await sleep(1)
        await msg.delete()

        percent = randint(1, 100)
        chance = 100 * 0.05 + plus / 2 if randint(1, 10) > 5 else 100 * 0.01 + 100 * 0.05 / 2 + plus
        if percent <= chance:

            embed = discord.Embed(title='🎊 **PARABENS** 🎉 VOCÊ DROPOU', color=self.bot.color,
                                  description=f"{self.bot.items['unsealed_stone'][0]} `{1}` "
                                              f"`{self.bot.items['unsealed_stone'][1]}`")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

            msg = await ctx.send("<a:loading:520418506567843860>│`SALVANDO SEU PREMIO...`")
            await sleep(3)
            await msg.delete()

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory']['unsealed_stone'] += 1
            except KeyError:
                update['inventory']['unsealed_stone'] = 1
            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f"<:confirmed:721581574461587496>│`PREMIO SALVO COM SUCESSO!`", delete_after=5.0)
            await self.bot.data.add_sts(ctx.author, "stone", 1)

        else:
            await ctx.send(f"> `A SORTE NAO ESTAVA COM VOCE`", delete_after=30.0)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='lucky', aliases=['sorte'])
    async def lucky(self, ctx, stone: int = None):
        """pedra da liberação usada para tirar o selo das armaduras seladas."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        global coin, cost, plus

        n_cost = [2000, 300, 100]

        if stone not in [1, 2, 3]:
            return await ctx.send(f"🎫│`Que tipo de` **PEDRA** `voce deseja gastar?"
                                  f" Escolha uma dessas opções abaixo!`\n"
                                  f"**[ ash lucky 1 ]** - `Para` {self.bot.money[0]} "
                                  f"`Custa:` **{n_cost[0]}** "
                                  f"`Bonus de Chance:` **+1%**\n"
                                  f"**[ ash lucky 2 ]** - `Para` {self.bot.money[1]} "
                                  f"`Custa:` **{n_cost[1]}** "
                                  f"`Bonus de Chance:` **+2%**\n"
                                  f"**[ ash lucky 3 ]** - `Para` {self.bot.money[2]} "
                                  f"`Custa:` **{n_cost[2]}** "
                                  f"`Bonus de Chance:` **+3%**")
        else:
            if stone == 1:
                cost = n_cost[0]
                coin = "bronze"
                plus = 1
            if stone == 2:
                cost = n_cost[1]
                coin = "silver"
                plus = 2
            if stone == 3:
                cost = n_cost[2]
                coin = "gold"
                plus = 3

        if data['treasure'][coin] < cost:
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não tem pedras suficientes.` '
                                  '**COMANDO CANCELADO**')

        # DATA DO MEMBRO
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        update_user['treasure'][coin] -= cost
        if update_user['treasure'][coin] < 0:
            update_user['treasure'][coin] = 0
        await self.bot.db.update_data(data_user, update_user, 'users')

        # DATA NATIVA DO SERVIDOR
        data_guild_native = await self.bot.db.get_data("guild_id", data_user['guild_id'], "guilds")
        update_guild_native = data_guild_native
        if update_guild_native is not None:
            update_guild_native['data'][f"total_{coin}"] -= cost
            if update_guild_native['data'][f"total_{coin}"] < 0:
                update_guild_native['data'][f"total_{coin}"] = 0
            await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')

        msg = await ctx.send("<a:loading:520418506567843860>│`VERIFICANDO SUA SORTE...`")
        await sleep(1)
        await msg.delete()

        percent = randint(1, 100)
        chance = 100 * 0.05 + plus / 2 if randint(1, 10) > 5 else 100 * 0.01 + 100 * 0.05 / 2 + plus
        if percent <= chance:

            # ESCOLHENDO O PREMIO:
            list_items = []
            for i_, amount in self.rewards_lucky.items():
                list_items += [i_] * amount
            reward = choice(list_items)

            embed = discord.Embed(title='🎊 **PARABENS** 🎉 VOCÊ DROPOU', color=self.bot.color,
                                  description=f"{self.bot.items[reward][0]} `{1}` "
                                              f"`{self.bot.items[reward][1]}`")
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
            await self.bot.data.add_sts(ctx.author, "lucky", 1)

        else:
            await ctx.send(f"> `A SORTE NAO ESTAVA COM VOCE`", delete_after=30.0)


def setup(bot):
    bot.add_cog(UserBank(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mUSERBANK\033[1;32m foi carregado com sucesso!\33[m')
