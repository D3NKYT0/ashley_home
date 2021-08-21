import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.utility import convert_item_name, create_id, paginator

item_key_equip, item_key_craft, _type = None, None, None
_MAX, _MAX_VIP = 10, 20


class MerchantClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='merchant', aliases=['mercado'])
    async def merchant(self, ctx, page: int = 0):
        """Mercado da ashley, onde todas as lojas sao dos proprios jogadores"""
        data = await self.bot.db.get_all_data("merchant")

        if len(data) == 0:
            return await ctx.send(f"<:negate:721581573396496464>|`NÃO HA LOJAS CADASTRADAS NO MERCADO, "
                                  f"PARA CRIAR UMA LOJA USE O COMANDO:`\n"
                                  f"**ash merc add <valor_da_und> <quantidade> <nome_do_item>**")

        embed = ['Mercado de Itens/Equipamentos:', self.bot.color, 'Lojas: \n']
        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))
        await ctx.send('```Para criar uma loja use o comando:\n'
                       'ash ma <preço_da_unidade> <quantidade> <nome_do_item>\n\n'
                       'Para comprar um item use o comando:\n'
                       'ash mb <codigo_da_loja> <quantidade>\n\n'
                       'Para remover uma loja use o comando:\n'
                       'ash mr <codigo_da_loja>\n\n'
                       'Para monstrar todas as suas lojas use o comando:\n'
                       'ash ml```')
        num = page - 1 if page > 0 else None
        await paginator(self.bot, equips_list, data, embed, ctx, num)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='merc add', aliases=['ma'])
    async def mercadd(self, ctx, value: int = None, amount: int = None, *, item=None):
        """Comando para adicionar loja no mercado"""
        global item_key_equip, item_key_craft, _type
        if value is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer o preço da unidade!`")
        if value < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")
        if amount is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantidade de itens!`")
        if amount < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")
        if item is None:
            return await ctx.send("<:alert:739251822920728708>│`Você esqueceu de falar o nome do item para colocar "
                                  "na loja!`")

        if item.lower() in ["medalhas", "rank points", "vote coin", "medalha", "rank point"]:
            return await ctx.send("<:alert:739251822920728708>│`Você não pode vender esse tipo de item.`")

        item_key_equip, item_key_craft, _type, count = None, None, None, 0
        data = await self.bot.db.get_all_data("merchant")
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if len(data) > 0:
            for key in data:
                if key['owner'] == ctx.author.id:
                    count += 1
        _TOT = _MAX_VIP if data_user['config']['vip'] else _MAX
        if count > _TOT:
            return await ctx.send("<:alert:739251822920728708>│`Você atingiu a quantidade maxima de lojas disponiveis"
                                  " por usuario, voce pode esperar as lojas esvaziarem por compras ou pode "
                                  "editar/remover a loja do mercado.`")

        item_key_craft = convert_item_name(item, self.bot.items)
        if item_key_craft is not None:
            _type = "craft"
            if self.bot.items[item_key_craft][2] is False:
                if self.bot.items[item_key_craft][3] in [8, 12, 14]:
                    return await ctx.send("<:alert:739251822920728708>│`Você não pode vender esse tipo de item.`")

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        if item not in [i[1]["name"] for i in equips_list]:
            if "sealed" in item.lower() and item.lower() != "unsealed stone":
                return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM ESTÁ SELADO, ANTES DISSO TIRE O SELO "
                                      "USANDO O COMANDO:` **ASH LIBERAR**")
            if _type is None:
                return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM NAO É NEM UM CRAFT NEM UM EQUIPAMENTO "
                                      "VALIDO, VERIFIQUE O NOME DO ITEM E TENTE NOVAMENTE...`")

        if item in [i[1]["name"] for i in equips_list] and _type is None:
            _type = "equip"

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if not update['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if _type == "craft":
            item_name = self.bot.items[item_key_craft][1]
            if item_key_craft not in update['inventory']:
                return await ctx.send("<:alert:739251822920728708>│`Você não tem esse item no seu inventario!`")
            if update['inventory'][item_key_craft] < amount:
                return await ctx.send(f"<:alert:739251822920728708>│`VOCÊ NÃO TEM ESSA QUANTIDADE DISPONIVEL DE "
                                      f"{item_name.upper()}!`")
            update['inventory'][item_key_craft] -= amount
            if update['inventory'][item_key_craft] < 1:
                del update['inventory'][item_key_craft]

        item_key_equip = None
        if _type == "equip":
            for key in update['rpg']['items'].keys():
                for name in equips_list:
                    if name[0] == key and name[1]["name"] == item:
                        item_key_equip = name
            if item_key_equip is None:
                return await ctx.send("<:negate:721581573396496464>│`VOCE NAO TEM ESSE ITEM...`")
            if update['rpg']['items'][item_key_equip[0]] < amount:
                return await ctx.send(f"<:alert:739251822920728708>│`VOCÊ NÃO TEM ESSA QUANTIDADE DISPONIVEL DE "
                                      f"{item_key_equip[1]['name'].upper()}!`")
            update['rpg']['items'][item_key_equip[0]] -= amount
            if update['rpg']['items'][item_key_equip[0]] < 1:
                del update['rpg']['items'][item_key_equip[0]]

        if _type == "craft":
            item_merchant = item_key_craft
        else:
            item_merchant = item_key_equip[0]
        _id = create_id()
        a = '{:,.2f}'.format(float(value))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')

        data_merchant = {
            "_id": _id, "owner": ctx.author.id, "type": _type, "amount": amount, "item": item_merchant, "value": value
        }
        await self.bot.db.push_data(data_merchant, "merchant")
        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f'<:confirmed:721581574461587496>│`PARABENS, VC ACABOU DE CRIAR UMA LOJA` **{_id}** '
                       f'`NO MERCADO, CONTENDO` **{amount}** `DE` **{item.upper()}** `CUSTANDO` **R$ {d}** '
                       f'`A UNIDADE COM SUCESSO!`')
        await self.bot.data.add_sts(ctx.author, "merchant_add", 1)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='merc list', aliases=['ml'])
    async def merclist(self, ctx, page: int = 0):
        """Comando para ver as lojas no mercado"""
        data = await self.bot.db.get_all_data("merchant")
        if len(data) == 0:
            return await ctx.send(f"<:negate:721581573396496464>|`NÃO HA LOJAS CADASTRADAS NO MERCADO, "
                                  f"PARA CRIAR UMA LOJA USE O COMANDO:`\n"
                                  f"**ash merc add <valor_da_und> <quantidade> <nome_do_item>**")

        embed = ['Mercado de Itens/Equipamentos:', self.bot.color, 'Minhas Lojas: \n']
        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        lojas = list()
        if len(data) > 0:
            for key in data:
                if key['owner'] == ctx.author.id:
                    lojas.append(key)

        if len(lojas) == 0:
            return await ctx.send(f"<:negate:721581573396496464>|`VOCE NÃO TEM LOJAS CADASTRADAS NO MERCADO, "
                                  f"PARA CRIAR UMA LOJA USE O COMANDO:`\n"
                                  f"**ash merc add <valor_da_und> <quantidade> <nome_do_item>**")

        num = page - 1 if page > 0 else None
        await paginator(self.bot, equips_list, lojas, embed, ctx, num)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='merc rem', aliases=['mr'])
    async def mercrem(self, ctx, id_shop: str = None):
        """Comando para remover uma loja do mercado"""
        if id_shop is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer o codigo da loja!`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " você estiver livre!`")

        if not data_user['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        data_shop = await self.bot.db.get_data("_id", id_shop.upper(), "merchant")

        if data_shop is None:
            return await ctx.send("<:alert:739251822920728708>│`Essa loja não existe, verifique o codigo da loja e"
                                  " tente novamente!`")

        if data_shop['owner'] != ctx.author.id:
            return await ctx.send("<:alert:739251822920728708>│`Essa loja não é sua, apenas o dono da loja pode"
                                  " remove-la do mercado!`")

        if data_shop['type'] == "craft":
            try:
                update_user['inventory'][data_shop['item']] += data_shop['amount']
            except KeyError:
                update_user['inventory'][data_shop['item']] = data_shop['amount']
        else:
            try:
                update_user['rpg']['items'][data_shop['item']] += data_shop['amount']
            except KeyError:
                update_user['rpg']['items'][data_shop['item']] = data_shop['amount']

        await self.bot.db.delete_data({"_id": data_shop['_id']}, "merchant")
        await self.bot.db.update_data(data_user, update_user, 'users')
        await ctx.send(f"<:confirmed:721581574461587496>│`PARABENS, VOCE ACABOU DE REMOVER SUA LOJA DO MERCADO COM"
                       f" SUCESSO, OS ITENS DA LOJA VOLTARAM PARA SEU INVENTARIO.`")
        await self.bot.data.add_sts(ctx.author, "merchant_remove", 1)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='merc buy', aliases=['mb'])
    async def mercbuy(self, ctx, id_shop: str = None, amount: int = None):
        """Comando para comprar itens das lojas do mercado."""
        if id_shop is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer o codigo da loja!`")
        if amount is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantidade de itens!`")
        if amount < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " você estiver livre!`")

        if not data_user['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        data_shop = await self.bot.db.get_data("_id", id_shop.upper(), "merchant")
        update_shop = data_shop

        if update_shop is None:
            return await ctx.send("<:alert:739251822920728708>│`Essa loja não existe, verifique o codigo da loja e"
                                  " tente novamente!`")

        if update_shop['amount'] < amount:
            msg = '<:negate:721581573396496464>│`ESSA LOJA NAO TEM ESSA QUANTIDADE DO ITEM!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        money = amount * update_shop['value']
        if data_user['treasure']["money"] < money:
            return await ctx.send(f"<:alert:739251822920728708>│`VOCÊ NÃO TEM ESSE VALOR DISPONIVEL DE "
                                  f"ETHERNYAS!`")

        msg = await self.bot.db.take_money(ctx, money)
        await ctx.send(msg)
        await self.bot.db.give_money(ctx, money, data_shop['owner'])

        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        if update_shop['type'] == "craft":
            try:
                update_user['inventory'][update_shop['item']] += amount
            except KeyError:
                update_user['inventory'][update_shop['item']] = amount
        else:
            try:
                update_user['rpg']['items'][update_shop['item']] += amount
            except KeyError:
                update_user['rpg']['items'][update_shop['item']] = amount

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))
        if data_shop['type'] == "craft":
            item_now = self.bot.items[data_shop["item"]]
            icon, name = item_now[0], item_now[1]
        else:
            item_now = [i[1] for i in equips_list if i[0] == data_shop["item"]]
            icon, name = item_now[0]["icon"], item_now[0]["name"]

        update_shop['amount'] -= amount
        if update_shop['amount'] <= 0:
            try:
                _user = self.bot.get_user(data_shop['owner'])
                await _user.send(f"<:confirmed:721581574461587496>│`Sua lojinha acabou de esvaziar todos os itens que"
                                 f" tinha disponiveis. Estarei enviando em anexo a essa mensagem os dados da sua "
                                 f"lojinha para você identificar qual das suas lojinhas foi finalizada do "
                                 f"mercado.`\n`CODIGO:` **{data_shop['_id']}**\n`ITEM:` {icon} `{name}`")
            except discord.errors.Forbidden:
                pass
            except AttributeError:
                pass
            await self.bot.db.delete_data({"_id": data_shop['_id']}, "merchant")
        await self.bot.db.update_data(data_shop, update_shop, 'merchant')
        await self.bot.db.update_data(data_user, update_user, 'users')
        await ctx.send(f"<:confirmed:721581574461587496>│`PARABENS, VOCE ACABOU DE COMPRAR` {icon} **{amount}** "
                       f"`{name.upper()}`")
        await self.bot.data.add_sts(ctx.author, "merchant_buy", 1)


def setup(bot):
    bot.add_cog(MerchantClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMERCHANT_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
