import disnake

from disnake.ext import commands
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
        self.sets = self.bot.config['attribute']['sets']
        self.set_equips = self.bot.config["set_equips"]

    def rarity_item(self, data):
        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        equipped_items = dict()
        for key, value in data['rpg']["equipped_items"].items():
            for i in equips_list:
                if i[0] == value:
                    equipped_items[key] = i[1]['name']

        _KK = equipped_items.keys()
        for key in data['rpg']["equipped_items"].keys():
            if key not in _KK:
                equipped_items[key] = ""

        return equipped_items

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='equip', aliases=['e', 'equipamento'])
    async def equip(self, ctx):
        """Comando para mostrar o painel de equipamentos do seu personagem"""
        if ctx.invoked_subcommand is None:
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")

            perms = ctx.channel.permissions_for(ctx.me)
            if not perms.add_reactions:
                return await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                    "REAÇÕES, PARA PODER FUNCIONAR CORRETAMENTE!**")

            try:
                if self.he[ctx.author.id]:
                    if str(ctx.command) in self.he[ctx.author.id].keys():
                        pass
                    else:
                        self.he[ctx.author.id][str(ctx.command)] = False
            except KeyError:
                self.he[ctx.author.id] = {str(ctx.command): False}

            if not data['rpg']['active']:
                embed = disnake.Embed(
                    color=self.bot.color,
                    description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
                return await ctx.send(embed=embed)

            eq = dict()
            for ky in self.bot.config['equips'].keys():
                for k, v in self.bot.config['equips'][ky].items():
                    eq[k] = v

            _class = data["rpg"]["class_now"]
            _db_class = data["rpg"]["sub_class"][_class]

            set_armor, full_armor = list(), False
            sts = {"atk": 0, "agi": 0, "prec": 0, "con": 0, "luk": 0}
            set_value = ["shoulder", "breastplate", "gloves", "leggings", "boots"]
            dagguer_dual = False

            for c in data['rpg']['equipped_items'].keys():
                if data['rpg']["equipped_items"][c] is not None:

                    if c in set_value:
                        set_armor.append(str(data['rpg']['equipped_items'][c]))

                    if c == "sword":
                        weapon_name = self.bot.config['equips']["weapons"][data['rpg']["equipped_items"][c]]["name"]
                        weapon_class = weapon_name.split()[0]

                        if "assassin celestial" in weapon_name and "knife" not in weapon_name:
                            dagguer_dual = True

                        if "silver" in weapon_name:

                            atk_weapon_bonus = 0
                            if weapon_class in ['assassin', 'priest']:
                                atk_weapon_bonus += 40

                            if weapon_class in ['paladin', 'warrior']:
                                atk_weapon_bonus += 20

                            if weapon_class in ['necromancer', 'wizard', 'warlock']:
                                atk_weapon_bonus += 30

                            sts["atk"] += int(_db_class["status"]["atk"]) + atk_weapon_bonus

                        if "mystic" in weapon_name:

                            atk_weapon_bonus = 0
                            if weapon_class in ['assassin', 'priest']:
                                atk_weapon_bonus += 60

                            if weapon_class in ['paladin', 'warrior']:
                                atk_weapon_bonus += 30

                            if weapon_class in ['necromancer', 'wizard', 'warlock']:
                                atk_weapon_bonus += 45

                            sts["atk"] += int(_db_class["status"]["atk"]) + atk_weapon_bonus

                        if "inspiron" in weapon_name:

                            atk_weapon_bonus = 0
                            if weapon_class in ['assassin', 'priest']:
                                atk_weapon_bonus += 80

                            if weapon_class in ['paladin', 'warrior']:
                                atk_weapon_bonus += 40

                            if weapon_class in ['necromancer', 'wizard', 'warlock']:
                                atk_weapon_bonus += 60

                            sts["atk"] += int(_db_class["status"]["atk"]) + atk_weapon_bonus

                        if "violet" in weapon_name:

                            atk_weapon_bonus = 0
                            if weapon_class in ['assassin', 'priest']:
                                atk_weapon_bonus += 100

                            if weapon_class in ['paladin', 'warrior']:
                                atk_weapon_bonus += 50

                            if weapon_class in ['necromancer', 'wizard', 'warlock']:
                                atk_weapon_bonus += 75

                            sts["atk"] += int(_db_class["status"]["atk"]) + atk_weapon_bonus

                        if "hero" in weapon_name:

                            atk_weapon_bonus = 0
                            if weapon_class in ['assassin', 'priest']:
                                atk_weapon_bonus += 120

                            if weapon_class in ['paladin', 'warrior']:
                                atk_weapon_bonus += 60

                            if weapon_class in ['necromancer', 'wizard', 'warlock']:
                                atk_weapon_bonus += 90

                            sts["atk"] += int(_db_class["status"]["atk"]) + atk_weapon_bonus

                        if "divine" in weapon_name:

                            atk_weapon_bonus = 0
                            if weapon_class in ['assassin', 'priest']:
                                atk_weapon_bonus += 300

                            if weapon_class in ['paladin', 'warrior']:
                                atk_weapon_bonus += 200

                            if weapon_class in ['necromancer', 'wizard', 'warlock']:
                                atk_weapon_bonus += 250

                            sts["atk"] += int(_db_class["status"]["atk"]) + atk_weapon_bonus

                    for name in _db_class["status"].keys():
                        if name in ["luk", "pdh"]:
                            continue
                        sts[name] += eq[data['rpg']['equipped_items'][c]]['modifier'][name]

            for kkk in self.bot.config["set_equips"].values():
                if len([e for e in set_armor if e in kkk['set']]) == 5:
                    full_armor = True
                    for name in sts.keys():
                        sts[name] += kkk['modifier'][name]

            # sistema de enchants armors
            enchant = data['rpg']['armors']
            for key in enchant.keys():
                for k in enchant[key]:
                    if k == 16:
                        sts['con'] += 1

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

            _EQUIPPED = self.rarity_item(data)

            data_equips = {
                "name": ctx.author.name,
                "class": str(data['rpg']['class_now']),
                "set": full_armor,
                "sex": data['rpg']['sex'],
                "skin": data['rpg']['skin'],

                "dagguer_dual": dagguer_dual,

                "status_base": {
                    "atk": str(data['rpg']["sub_class"][_class]['status']['atk']),
                    "dex": str(data['rpg']["sub_class"][_class]['status']['agi']),
                    "acc": str(data['rpg']["sub_class"][_class]['status']['prec']),
                    "con": str(data['rpg']["sub_class"][_class]['status']['con']),
                    "luk": str(data['rpg']["sub_class"][_class]['status']['luk'])
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
                    "breastplate": (data['rpg']["equipped_items"]['breastplate'], _EQUIPPED['breastplate']),
                    "leggings": (data['rpg']["equipped_items"]['leggings'], _EQUIPPED['leggings']),
                    "boots": (data['rpg']["equipped_items"]['boots'], _EQUIPPED['boots']),
                    "gloves": (data['rpg']["equipped_items"]['gloves'], _EQUIPPED['gloves']),
                    "shoulder": (data['rpg']["equipped_items"]['shoulder'], _EQUIPPED['shoulder']),
                    "sword": (data['rpg']["equipped_items"]['sword'], _EQUIPPED['sword']),
                    "shield": (data['rpg']["equipped_items"]['shield'], _EQUIPPED['shield']),
                    "consumable": (data['rpg']["equipped_items"]['consumable'], _EQUIPPED['consumable']),
                    "necklace": (data['rpg']["equipped_items"]['necklace'], _EQUIPPED['necklace']),
                    "earring": (data['rpg']["equipped_items"]['earring'], _EQUIPPED['earring']),
                    "ring": (data['rpg']["equipped_items"]['ring'], _EQUIPPED['ring'])
                }
            }

            equips(data_equips)
            _id = create_id()
            self.botmsg[_id] = await ctx.send(file=disnake.File('equips.png'),
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
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
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
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
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
            embed = disnake.Embed(color=self.bot.color, description=msg)
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
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
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
                                      "**ASH ES**")

            return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM NAO EXISTE...`\n"
                                  "`Verifique se vc digitou o comando corretamente:`\n"
                                  "`Ex:` **ash e i EARRING OF DIAMOND - HERO**")

        _classes = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_classes]

        if "divine" in item and _db_class['level'] < 99:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ SÓ PODE USAR ESSE ITEM NO LEVEL 99!`")
        elif "hero" in item and _db_class['level'] < 80:
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

        if "assassin celestial" in item and update['rpg']["equipped_items"]['shield'] is not None:
            if "knife" not in item:
                return await ctx.send("<:negate:721581573396496464>│`VOCÊ NAO PODE USAR ESSA ARMA JUNTO COM UM "
                                      "ESCUDO!`")

        if item == "celestial leather - shield divine" and update['rpg']["equipped_items"]['sword'] is not None:
            if update['rpg']["equipped_items"]['sword'] not in self.bot.config["attribute"]["weapons_no_dual"]:
                return await ctx.send("<:negate:721581573396496464>│`VOCÊ NAO PODE USAR ESSE ESCUDO JUNTO COM UMA "
                                      "ARMA!`")

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
    @equip.command(name='set', aliases=['s'])
    async def _set(self, ctx, *, set_equip=None):
        """Esse comando equipa um conjunto de equipamentos no seu personagem"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        _class = ["paladin", "warrior", "necromancer", "wizard", "warlock", "priest", "assassin"]

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if set_equip is None:
            return await ctx.send("<:negate:721581573396496464>│`Você precisa colocar o nome de um conjunto que deseja"
                                  " equipar em voce:` **ash equip set leather hero** `voce consegue ver os conjuntos"
                                  " usando o comando:` **ash sets**")

        if set_equip not in self.sets.keys():
            return await ctx.send("<:negate:721581573396496464>│`ESSE CONJUNTO NAO EXISTE...`\n"
                                  "`Verifique se vc digitou o comando corretamente:`\n"
                                  "`Ex:` **ash equip set leather hero**")

        _classes = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_classes]

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        if "divine" in set_equip and _db_class['level'] < 99:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ SÓ PODE USAR ESSE CONJUNTO NO LEVEL 99!`")
        elif "hero" in set_equip and _db_class['level'] < 80:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ SÓ PODE USAR ESSE CONJUNTO ABAIXO DO LEVEL 80!`")
        elif "violet" in set_equip and _db_class['level'] < 61:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE CONJUNTO ABAIXO DO LEVEL 61!`")
        elif "inspiron" in set_equip and _db_class['level'] < 41:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE CONJUNTO ABAIXO DO LEVEL 41!`")
        elif "mystic" in set_equip and _db_class['level'] < 21:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE CONJUNTO ABAIXO DO LEVEL 21!`")
        elif "silver" in set_equip and _db_class['level'] < 11:
            return await ctx.send("<:negate:721581573396496464>│`VOCÊ NÃO PODE USAR ESSE CONJUNTO ABAIXO DO LEVEL 11!`")

        if "jewel" not in set_equip:
            if "leather" not in set_equip and _classes in ["assassin", "priest"]:
                return await ctx.send("<:negate:721581573396496464>│`SUA CLASSE NAO PODE USAR ESSE CONJUNTO...`")
            if "platinum" not in set_equip and _classes in ["warrior", "paladin"]:
                return await ctx.send("<:negate:721581573396496464>│`SUA CLASSE NAO PODE USAR ESSE CONJUNTO...`")
            if "cover" not in set_equip and _classes in ["necromancer", "wizard", "warlock"]:
                return await ctx.send("<:negate:721581573396496464>│`SUA CLASSE NAO PODE USAR ESSE CONJUNTO...`")

        equipped_items = list()
        for value in update['rpg']["equipped_items"].values():
            for i in equips_list:
                if i[0] == value:
                    equipped_items.append(i[0])

        items_inventory = list()
        for key in update['rpg']["items"].keys():
            for i in equips_list:
                if i[0] == key:
                    items_inventory.append(i[0])

        if "jewel" in set_equip:
            set_now = self.sets[set_equip]
        else:
            set_now = self.set_equips[self.sets[set_equip]]["set"]

        for i in set_now:
            if i not in items_inventory:
                return await ctx.send("<:negate:721581573396496464>│`VOCE NAO TEM UM DOS ITENS DESSE CONJUNTO!`")

        # ------------------------------------------------------------------------------------------------------------

        for item in set_now:

            data_item = None
            for di in equips_list:
                if di[0] == item:
                    data_item = di[1]

            if data_item is None:
                print(f"ERRO NA DATA DO ITEM: {item}")
                continue

            if item in equipped_items:
                continue

            else:
                msg = await ctx.send(f"<a:loading:520418506567843860>│`EQUIPANDO` **{data_item['name'].upper()}**")
                await sleep(1)

                # aqui esta tirando o item do inventario
                update['rpg']['items'][item] -= 1
                if update['rpg']['items'][item] < 1:
                    del update['rpg']['items'][item]

                # se o slot do item esta vazio, apenas equipa o item!
                if update['rpg']["equipped_items"][data_item["slot"]] is None:
                    update['rpg']["equipped_items"][data_item["slot"]] = item
                    await msg.delete()

                # caso contrario, retira o item para add o novo
                else:
                    # retira o item antigo de coloca no inventario de volta!
                    item_equipped = update['rpg']["equipped_items"][data_item["slot"]]
                    if item_equipped in update['rpg']['items'].keys():
                        update['rpg']['items'][item_equipped] += 1
                    else:
                        update['rpg']['items'][item_equipped] = 1

                    # adiciona o item novo no lugar do antigo
                    update['rpg']["equipped_items"][data_item["slot"]] = item

                    await sleep(1)
                    await msg.delete()

        await self.bot.db.update_data(data, update, 'users')
        await ctx.send(f"<:confirmed:721581574461587496>│`O CONJUNTO` **{set_equip.upper()}** "
                       f"`FOI EQUIPADO COM SUCESSO!`")

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
    @commands.command(name='sets', aliases=['conjuntos'])
    async def sets(self, ctx):
        """Comando usado pra ver os conjuntos de equipamentos disponiveis"""
        sets = ""
        for conjunto in self.sets:
            sets += f"\n**{conjunto.upper()}**"
        await ctx.send(f"<:confirmed:721581574461587496>|`SEGUE ABAIXO A LISTA DOS CONJUNTOS DISPONIVEIS:`\n{sets}")

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
