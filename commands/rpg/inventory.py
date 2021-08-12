import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.utility import paginator
from resources.img_edit import equips
from asyncio import sleep, TimeoutError
from resources.utility import create_id


class InventoryClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.i = self.bot.items
        self.color = self.bot.color
        self.botmsg = {}
        self.he = self.bot.help_emoji

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='equip', aliases=['e', 'equipamento'])
    async def equip(self, ctx):
        """Comando para mostrar o painel de equipamentos do seu personagem"""
        if ctx.invoked_subcommand is None:
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")

            try:
                if self.he[ctx.author.id]:
                    if str(ctx.command) in self.he[ctx.author.id].keys():
                        pass
                    else:
                        self.he[ctx.author.id][str(ctx.command)] = False
            except KeyError:
                self.he[ctx.author.id] = {str(ctx.command): False}

            if not data['rpg']['active']:
                embed = discord.Embed(
                    color=self.bot.color,
                    description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
                return await ctx.send(embed=embed)

            eq = dict()
            for ky in self.bot.config['equips'].keys():
                for k, v in self.bot.config['equips'][ky].items():
                    eq[k] = v

            set_armor = list()
            sts = {"atk": 0, "agi": 0, "prec": 0, "con": 0, "luk": 0}
            set_value = ["shoulder", "breastplate", "gloves", "leggings", "boots"]
            for key in data['rpg']["equipped_items"].keys():
                if data['rpg']["equipped_items"][key] is not None:
                    if key in set_value:
                        set_armor.append(data['rpg']["equipped_items"][key])
                    for k in sts.keys():
                        try:
                            sts[k] += eq[data['rpg']["equipped_items"][key]]["modifier"][k]
                        except KeyError:
                            pass

            for kkk in self.bot.config["set_equips"].values():
                if kkk['set'] == set_armor:
                    for name in sts.keys():
                        try:
                            sts[name] += kkk['modifier'][name]
                        except KeyError:
                            pass

            atk = self.bot.config["skills"][data['rpg']['class']]['modifier']['atk']
            dex = self.bot.config["skills"][data['rpg']['class']]['modifier']['agi']
            acc = self.bot.config["skills"][data['rpg']['class']]['modifier']['prec']
            con = self.bot.config["skills"][data['rpg']['class']]['modifier']['con']
            luk = self.bot.config["skills"][data['rpg']['class']]['modifier']['luk']

            _class = data["rpg"]["class_now"]
            _db_class = data["rpg"]["sub_class"][_class]
            if _db_class['level'] > 25:
                atk += self.bot.config['skills'][data['rpg']['class_now']]['modifier']['atk']
                dex += self.bot.config['skills'][data['rpg']['class_now']]['modifier']['agi']
                acc += self.bot.config['skills'][data['rpg']['class_now']]['modifier']['prec']
                con += self.bot.config['skills'][data['rpg']['class_now']]['modifier']['con']
                luk += self.bot.config["skills"][data['rpg']['class_now']]['modifier']['luk']

            _class = data["rpg"]["class_now"]
            _db_class = data["rpg"]["sub_class"][_class]
            if _db_class['level'] > 49:
                atk += self.bot.config['skills'][data['rpg']['class_now']]['modifier_50']['atk']
                dex += self.bot.config['skills'][data['rpg']['class_now']]['modifier_50']['agi']
                acc += self.bot.config['skills'][data['rpg']['class_now']]['modifier_50']['prec']
                con += self.bot.config['skills'][data['rpg']['class_now']]['modifier_50']['con']
                luk += self.bot.config["skills"][data['rpg']['class_now']]['modifier_50']['luk']

            _class = data["rpg"]["class_now"]
            _db_class = data["rpg"]["sub_class"][_class]
            if _db_class['level'] > 79:
                atk += self.bot.config['skills'][data['rpg']['class_now']]['modifier_80']['atk']
                dex += self.bot.config['skills'][data['rpg']['class_now']]['modifier_80']['agi']
                acc += self.bot.config['skills'][data['rpg']['class_now']]['modifier_80']['prec']
                con += self.bot.config['skills'][data['rpg']['class_now']]['modifier_80']['con']
                luk += self.bot.config["skills"][data['rpg']['class_now']]['modifier_80']['luk']

            data_equips = {
                "name": ctx.author.name,
                "class": str(data['rpg']['class_now']),

                "status_base": {
                    "atk": str(data['rpg']['status']['atk']),
                    "dex": str(data['rpg']['status']['agi']),
                    "acc": str(data['rpg']['status']['prec']),
                    "con": str(data['rpg']['status']['con']),
                    "luk": str(data['rpg']['status']['luk'])
                },

                "status_class": {
                    "atk": str(atk),
                    "dex": str(dex),
                    "acc": str(acc),
                    "con": str(con),
                    "luk": str(luk)
                },

                "status_equip": {
                    "atk": str(sts["atk"]),
                    "dex": str(sts["agi"]),
                    "acc": str(sts["prec"]),
                    "con": str(sts["con"]),
                    "luk": str(sts["luk"])
                },

                "enchants": {
                    "shoulder": data['rpg']['armors']['shoulder'],
                    "breastplate": data['rpg']['armors']['breastplate'],
                    "gloves": data['rpg']['armors']['gloves'],
                    "leggings": data['rpg']['armors']['leggings'],
                    "boots": data['rpg']['armors']['boots'],
                    "shield": data['rpg']['armors']['shield'],
                    "necklace": data['rpg']['armors']['necklace'],
                    "earring": data['rpg']['armors']['earring'],
                    "ring": data['rpg']['armors']['ring']
                },

                'equipped': {
                    "breastplate": data['rpg']["equipped_items"]['breastplate'],
                    "leggings": data['rpg']["equipped_items"]['leggings'],
                    "boots": data['rpg']["equipped_items"]['boots'],
                    "gloves": data['rpg']["equipped_items"]['gloves'],
                    "shoulder": data['rpg']["equipped_items"]['shoulder'],
                    "sword": data['rpg']["equipped_items"]['sword'],
                    "shield": data['rpg']["equipped_items"]['shield'],
                    "consumable": data['rpg']["equipped_items"]['consumable'],
                    "necklace": data['rpg']["equipped_items"]['necklace'],
                    "earring": data['rpg']["equipped_items"]['earring'],
                    "ring": data['rpg']["equipped_items"]['ring']
                }
            }

            equips(data_equips)
            _id = create_id()
            self.botmsg[_id] = await ctx.send(file=discord.File('equips.png'),
                                              content="> `CLIQUE NA IMAGEM PARA MAIORES DETALHES`")
            if not self.he[ctx.author.id][str(ctx.command)]:
                await self.botmsg[_id].add_reaction('<a:help:767825933892583444>')
                await self.botmsg[_id].add_reaction(self.bot.config['emojis']['arrow'][4])

            text = "```Markdown\n[>>]: PARA EQUIPAR UM ITEM USE O COMANDO\n<ASH EQUIP ITEM NOME_DO_ITEM>\n" \
                   "[>>]: PARA RESETAR OS EQUIPAMENTOS USE O COMANDO\n<ASH EQUIP RESET>\n\n" \
                   "[>>]: PARA MAIS INFORMAÇÕES USE O COMANDO\n<ASH EQUIP INFO>```"

            again = False
            msg = None
            if not self.he[ctx.author.id][str(ctx.command)]:
                self.he[ctx.author.id][str(ctx.command)] = True
                while not self.bot.is_closed():
                    try:
                        def check(react, member):
                            try:
                                if react.message.id == self.botmsg[_id].id:
                                    if member.id == ctx.author.id:
                                        return True
                                return False
                            except AttributeError:
                                return False

                        reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

                        emo = "<a:help:767825933892583444>"
                        emoji = str(emo).replace('<a:', '').replace(emo[emo.rfind(':'):], '')
                        emo_2 = self.bot.config['emojis']['arrow'][4]
                        emoji_2 = str(emo_2).replace('<:', '').replace(emo_2[emo_2.rfind(':'):], '')

                        try:
                            try:
                                _reaction = reaction[0].emoji.name
                            except AttributeError:
                                _reaction = reaction[0].emoji

                            if _reaction == emoji and reaction[0].message.id == self.botmsg[_id].id and not again:
                                if reaction[1].id == ctx.author.id:
                                    again = True
                                    perms = ctx.channel.permissions_for(ctx.me)
                                    if perms.manage_messages:
                                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>",
                                                                               ctx.author)
                                    msg = await ctx.send(text)

                            elif _reaction == emoji and reaction[0].message.id == self.botmsg[_id].id and again:
                                if reaction[1].id == ctx.author.id:
                                    again = False
                                    perms = ctx.channel.permissions_for(ctx.me)
                                    if perms.manage_messages:
                                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>",
                                                                               ctx.author)
                                    await msg.delete()

                            if _reaction == emoji_2 and reaction[0].message.id == self.botmsg[_id].id:
                                if reaction[1].id == ctx.author.id:
                                    self.he[ctx.author.id][str(ctx.command)] = False
                                    perms = ctx.channel.permissions_for(ctx.me)
                                    if perms.manage_messages:
                                        await self.botmsg[_id].remove_reaction(
                                            self.bot.config['emojis']['arrow'][4], ctx.me)
                                        await self.botmsg[_id].remove_reaction(
                                            "<a:help:767825933892583444>", ctx.me)
                                    return

                        except AttributeError:
                            pass
                    except TimeoutError:
                        self.he[ctx.author.id][str(ctx.command)] = False
                        perms = ctx.channel.permissions_for(ctx.me)
                        if perms.manage_messages:
                            await self.botmsg[_id].remove_reaction(self.bot.config['emojis']['arrow'][4], ctx.me)
                            await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>", ctx.me)
                        return

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @equip.command(name='info')
    async def _info(self, ctx):
        """Comando que mostra as informações dos equipamentos do seu personagem"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        equipped_items = list()
        for value in update['rpg']["equipped_items"].values():
            for i in equips_list:
                if i[0] == value:
                    equipped_items.append(i[1])

        if len(equipped_items) == 0:
            msg = "VOCE NAO TEM ITENS EQUIPADOS NO MOMENTO, USE O COMANDO \"ASH ES\" PARA VER OS ITEMS PARA EQUIPAR," \
                  " LOGO APOS USE O COMANDO \"ASH E I <NOME_DO_ITEM>\" PARA EQUIPAR O SEU ITEM."
            return await ctx.send(f"<:confirmed:721581574461587496>│`ITENS EQUIPADOS EM VOCE:`\n```{msg}```")

        msg = '```Markdown\n'
        for item in equipped_items:
            msg += f"[>>]: {item['name'].upper()}\n<DEFENSE: PDEF = {item['pdef']} MDEF = \"{item['mdef']}\">\n" \
                   f"<STATUS: ATK = \"{item['modifier']['atk']}\" DEX = \"{item['modifier']['agi']}\" " \
                   f"ACC = \"{item['modifier']['prec']}\" CON = \"{item['modifier']['con']}\">\n\n"
        msg += "```"
        await ctx.send(f"<:confirmed:721581574461587496>│`ITENS EQUIPADOS EM VOCE:`\n{msg}")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @equip.command(name='reset', aliases=['r'])
    async def _reset(self, ctx):
        """Esse comando retira todos os equipamentos do seu persoangem, para o seu inventario"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        equipped_items = list()
        for value in update['rpg']["equipped_items"].values():
            for i in equips_list:
                if i[0] == value:
                    equipped_items.append(i[1]["name"])

        equip_out = list()
        for key in update['rpg']["equipped_items"].keys():
            if update['rpg']["equipped_items"][key] is not None:
                for name in equips_list:
                    if name[0] == update['rpg']["equipped_items"][key]:
                        equip_out.append(update['rpg']['equipped_items'][key])
                        update['rpg']['equipped_items'][key] = None

        if len(equip_out) > 0:
            for item in equip_out:
                try:
                    update['rpg']['items'][item] += 1
                except KeyError:
                    update['rpg']['items'][item] = 1

            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f"<:confirmed:721581574461587496>│`OS ITENS ESTAO NO SEU INVENTARIO DE EQUIPAMENTOS!`")

        else:
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM ITEM EQUIPADO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @equip.command(name='item', aliases=['i'])
    async def _item(self, ctx, *, item=None):
        """Esse comando equipa um item do seu inventario de equipamento no seu personagem"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        _class = ["paladin", "warrior", "necromancer", "wizard", "warlock", "priest", "assassin"]

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if item is None:
            return await ctx.send("<:negate:721581573396496464>│`Você precisa colocar o nome de um item que deseja "
                                  "equipar em voce:` **ash equip i <nome_do_item>** `voce consegue ver os itens "
                                  "usando o comando:` **ash es**")

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        if item not in [i[1]["name"] for i in equips_list]:
            if "sealed" in item:
                return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM ESTÁ SELADO, ANTES DISSO TIRE O SELO "
                                      "USANDO O COMANDO:` **ASH LIBERAR** `E USE O NOME DO COMANDO:` "
                                      "**ASH INVENTORY EQUIP** `OU` **ASH I E**")

            return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM NAO EXISTE...`\n"
                                  "`Verifique se vc digitou o comando corretamente:`\n"
                                  "`Ex:` **ash e i EARRING OF DIAMOND - HERO**")

        _classes = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_classes]

        if "hero" in item and _db_class['level'] < 80:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ SÓ PODE USAR ESSE ITEM NO LEVEL 80!`")
        elif "violet" in item and _db_class['level'] < 61:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE ITEM ABAIXO DO LEVEL 61!`")
        elif "inspiron" in item and _db_class['level'] < 41:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE ITEM ABAIXO DO LEVEL 41!`")
        elif "mystic" in item and _db_class['level'] < 21:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE ITEM ABAIXO DO LEVEL 21!`")
        elif "silver" in item and _db_class['level'] < 11:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE ITEM ABAIXO DO LEVEL 11!`")

        consumable = update['rpg']["equipped_items"]['consumable']
        _consumable = consumable if consumable is not None else ""
        _ss = True if "soushot_" in _consumable else False

        if item.split()[0] in _class and _ss:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ PRECISA TIRAR A SOULSHOT PRIMEIRO,"
                                  " ANTES DE TIRAR A ARMA!`\n**Use o comando: \"ash e info\" verifique o nome do "
                                  "item existente, entao use o comando \"ash e i <nome_do_item>\" "
                                  "para desequipar o item atual, entao voce usa o comando novamente "
                                  "com o nome do item que voce quer equipar.**")

        if "soulshot" in item and not _ss:
            if update['rpg']["equipped_items"]['sword'] is None:
                return await ctx.send("<:negate:721581573396496464>│`VOCÊ PRECISA DE UMA ARMA PARA USAR SOULSHOT!`")

            sword_id = update['rpg']["equipped_items"]['sword']
            sword = [i[1]["name"] for i in equips_list if i[0] == sword_id][0]
            _n1 = -2 if "+" in item.split()[-1] else -1
            _n2 = -2 if "+" in sword.split()[-1] else -1
            if item.split()[_n1] != sword.split()[_n2]:
                return await ctx.send("<:negate:721581573396496464>│`VOCÊ NAO PODE USAR SOULSHOT COM UMA ARMA DE "
                                      "RARIDADE DIFERENTE DA MESMA!`")

        equipped_items = list()
        for value in update['rpg']["equipped_items"].values():
            for i in equips_list:
                if i[0] == value:
                    equipped_items.append(i[1]["name"])

        items_inventory = list()
        for key in update['rpg']["items"].keys():
            for i in equips_list:
                if i[0] == key:
                    items_inventory.append(i[1]["name"])

        if item in equipped_items:
            msg = await ctx.send("<a:loading:520418506567843860>│`O ITEM JA ESTA EQUIPADO EM VOCE, DESEQUIPANDO...`")
            plus = "DESEQUIPADO"
            equip_out = None

            for key in update['rpg']["equipped_items"].keys():
                if update['rpg']["equipped_items"][key] is not None:
                    for name in equips_list:
                        if name[1]["name"] == item and name[0] == update['rpg']["equipped_items"][key]:
                            equip_out = update['rpg']['equipped_items'][key]
                            update['rpg']['equipped_items'][key] = None

            if equip_out is not None:
                try:
                    update['rpg']['items'][equip_out] += 1
                except KeyError:
                    update['rpg']['items'][equip_out] = 1

        elif item in items_inventory:
            msg = await ctx.send("<a:loading:520418506567843860>│`O ITEM ESTA NO SEU INVENTARIO, EQUIPANDO...`")
            await sleep(1)
            plus = "EQUIPADO"
            equip_in = None

            # aqui esta verificando qual o ID do item
            for key in update['rpg']['items'].keys():
                for name in equips_list:
                    if name[0] == key and name[1]["name"] == item:
                        equip_in = name

            if equip_in is not None:
                if data['rpg']['class_now'] in equip_in[1]["class"]:

                    # aqui esta tirando o item do inventario
                    update['rpg']['items'][equip_in[0]] -= 1
                    if update['rpg']['items'][equip_in[0]] < 1:
                        del update['rpg']['items'][equip_in[0]]

                    # se o slot do item esta vazio, apenas equipa o item!
                    if update['rpg']["equipped_items"][equip_in[1]["slot"]] is None:
                        update['rpg']["equipped_items"][equip_in[1]["slot"]] = equip_in[0]

                    # caso contrario, inicia os testes...
                    else:
                        await sleep(1)
                        await msg.delete()
                        return await ctx.send("<:negate:721581573396496464>│`VOCE PRECISA DESEQUIPAR O ITEM "
                                              "EXISTENTE...`\n**Use o comando: \"ash e info\" verifique o nome do "
                                              "item existente, entao use o comando \"ash e i <nome_do_item>\" "
                                              "para desequipar o item atual, entao voce usa o comando novamente "
                                              "com o nome do item que voce quer equipar.**")

                else:
                    await sleep(1)
                    await msg.delete()
                    return await ctx.send("<:negate:721581573396496464>│`SUA CLASSE NAO PODE USAR ESSE ITEM...`")

        else:
            return await ctx.send("<:negate:721581573396496464>│`VOCE NAO TEM ESSE ITEM...`")

        await sleep(1)
        await msg.delete()
        await ctx.send(f"<:confirmed:721581574461587496>│`O ITEM {item.upper()} FOI {plus} COM SUCESSO!`")
        await self.bot.db.update_data(data, update, 'users')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='inventory', aliases=['inventario', 'i'])
    async def inventory(self, ctx, page: int = 0):
        """Comando usado pra ver seu inventario
        Use ash i ou ash inventory"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        embed = ['Inventário de itens:', self.color, 'Items: \n']
        num = page - 1 if page > 0 else None
        await paginator(self.bot, self.i, data['inventory'], embed, ctx, num)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='equips', aliases=['es', 'eq', 'equipamentos'])
    async def equips(self, ctx, page: int = 0):
        """Comando usado pra ver seu inventario de equipamentos"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")

        if len(data['rpg']['items'].keys()) == 0:
            return await ctx.send(f"<:negate:721581573396496464>|`SEU INVENTARIO DE EQUIPAMENTOS ESTÁ VAZIO!`")

        embed = ['Inventário de equipamentos:', self.color, 'Equipamentos: \n']

        eq = dict()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                eq[k] = v

        num = page - 1 if page > 0 else None
        await paginator(self.bot, eq, data['rpg']['items'], embed, ctx, num)


def setup(bot):
    bot.add_cog(InventoryClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mINVENTORYCLASS\033[1;32m foi carregado com sucesso!\33[m')
