import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from asyncio import TimeoutError
from config import data as _data
from random import randint
from resources.utility import create_id, convert_item_name
from resources.fight import Ext
limit, limit_weapon, extension, _class = 16, 20, Ext(), _data['skills']
levels = [5, 10, 15, 20, 25]


class EnchanterClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.atacks = {}
        self.up_chance = 0
        self.chance_skill = self.bot.config['attribute']['chance_skill']
        self.chance_armor = self.bot.config['attribute']['chance_armor']
        self.chance_weapon = self.bot.config['attribute']['chance_weapon_enchant']
        self.botmsg = {}
        self.he = self.bot.help_emoji

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='enchant', aliases=['encantar', 'en'])
    async def enchant(self, ctx):
        """Comando usado pra ver os encantamentos das suas habilidades no rpg da Ashley
        Use ash enchant"""
        if ctx.invoked_subcommand is None:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                member = ctx.author

            try:
                if self.he[ctx.author.id]:
                    if str(ctx.command) in self.he[ctx.author.id].keys():
                        pass
                    else:
                        self.he[ctx.author.id][str(ctx.command)] = False
            except KeyError:
                self.he[ctx.author.id] = {str(ctx.command): False}

            data = await self.bot.db.get_data("user_id", member.id, "users")

            if not data['rpg']['active']:
                embed = discord.Embed(
                    color=self.bot.color,
                    description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
                return await ctx.send(embed=embed)

            self.atacks = {}
            data_player = extension.set_player(ctx.guild.get_member(ctx.author.id), data)
            rate = [_class["default"]['rate']['life'], _class["default"]['rate']['mana']]
            if data_player['level'] > 25:
                rate[0] += _class[data_player['class_now']]['rate']['life']
                rate[1] += _class[data_player['class_now']]['rate']['mana']

            lvl = data_player['level']
            tot_mp = _class[data_player['class_now']]['tot_mana'] if lvl > 25 else _class['default']['tot_mana']
            tot_mp += (rate[1] + data_player['mana_bonus']) * 2

            data_player['status']['hp'] = data_player['status']['con'] * rate[0]
            data_player['status']['mp'] = tot_mp

            self.db = data_player
            for c in range(5):
                if self.db['level'] >= levels[c]:
                    self.atacks[_class[self.db['class_now']][str(c)]['name']] = _class[self.db['class_now']][str(c)]
                else:
                    self.atacks[_class[self.db['class']][str(c)]['name']] = _class[self.db['class']][str(c)]
            atacks = list(self.atacks.keys())

            description = ''
            for c in range(0, len(atacks)):
                lvs = self.db['skills'][c]
                lvl_skill = lvs if 0 <= lvs <= 9 else 9
                c2, ls, _att = atacks[c], lvs, self.db['status']['atk']

                if self.db['class_now'] in ['necromancer', 'wizard', 'warlock']:
                    tot_atk = int(_att * 1.6)
                elif self.db['class_now'] in ['assassin', 'priest']:
                    tot_atk = int(_att * 1.4)
                else:
                    tot_atk = int(_att * 1.2)

                dado = self.atacks[c2]['damage'][lvl_skill]
                d1, d2 = int(dado[:dado.find('d')]), int(dado[dado.find('d') + 1:])
                dd, d3 = [d2, d2 * d1] if d2 != d2 * d1 else [d2, d2], int((lvs - 10) * 10)
                dd = [d2 + d3, d2 * d1] if lvs >= 11 else dd
                dd[1] = dd[0] + 1 if dd[0] > dd[1] else dd[1]
                skill_number = c + 1
                _atk = [int(tot_atk / 100 * (50 + skill_number)), int(tot_atk / 100 * (50 + (skill_number * 10)))]
                _damage = [_atk[0] + dd[0], _atk[1] + dd[1]]
                if _damage[0] == _damage[1]:
                    damage = f"{_damage[0]}"
                else:
                    damage = f"{_damage[0]}-{_damage[1]}"
                icon, sk_tp = self.atacks[c2]['icon'], self.atacks[c2]['type']

                try:
                    effect_skill = ", ".join(list(self.atacks[c2]['effs'][lvl_skill].keys()))
                except KeyError:
                    effect_skill = "sem efeito"
                except TypeError:
                    effect_skill = "sem efeito"

                lsv, sk_xp = self.db["skill_level"][c][0], self.db["skill_level"][c][1]
                rm = int((tot_mp / 100) * 35)
                ru = int((tot_mp / 100) * 50)
                a_mana = self.atacks[c2]['mana'][lsv]
                _mana = a_mana if effect_skill != "cura" else rm
                _mana = ru if self.atacks[c2]['type'] == "especial" else _mana
                lvn, name, _type = lsv + 1, c2.upper(), sk_tp.upper()

                description += f"{icon} **{name}** `+{lvs}` | **{_type}** `Lv: {lvn}` **({sk_xp}/100)**\n" \
                               f"`Dano:` **{damage}** | `Mana:` **{_mana}** | `Efeito(s):` **{effect_skill}**\n\n"

            _TM = int(tot_mp)
            description += f"`MDEF:` **{int(data_player['mdef'])}**  |  `PDEF:` **{int(data_player['pdef'])}**"
            title = f"ENCHANTER PANEL - TOTAL MANA: {_TM}"
            embed = discord.Embed(title=title, description=description, color=0x000000)
            embed.set_thumbnail(url=member.avatar_url)

            _id = create_id()

            self.botmsg[_id] = await ctx.send(embed=embed)
            if not self.he[ctx.author.id][str(ctx.command)]:
                await self.botmsg[_id].add_reaction('<a:help:767825933892583444>')
                await self.botmsg[_id].add_reaction(self.bot.config['emojis']['arrow'][4])

            text = "```Markdown\n[>>]: PARA ENCANTAR UMA SKILL USE O COMANDO\n<ASH ENCHANT ADD NUMERO_DA_SKILL>```"

            again = False
            msg = None
            if not self.he[ctx.author.id][str(ctx.command)]:
                self.he[ctx.author.id][str(ctx.command)] = True
                while not self.bot.is_closed():
                    try:
                        reaction = await self.bot.wait_for('reaction_add', timeout=30.0)
                        while reaction[1].id != ctx.author.id:
                            reaction = await self.bot.wait_for('reaction_add', timeout=30.0)

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
                                    try:
                                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>",
                                                                               ctx.author)
                                    except discord.errors.Forbidden:
                                        pass
                                    msg = await ctx.send(text)

                            elif _reaction == emoji and reaction[0].message.id == self.botmsg[_id].id and again:
                                if reaction[1].id == ctx.author.id:
                                    again = False
                                    try:
                                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>",
                                                                               ctx.author)
                                    except discord.errors.Forbidden:
                                        pass
                                    await msg.delete()

                            if _reaction == emoji_2 and reaction[0].message.id == self.botmsg[_id].id:
                                if reaction[1].id == ctx.author.id:
                                    self.he[ctx.author.id][str(ctx.command)] = False
                                    await self.botmsg[_id].remove_reaction(
                                        self.bot.config['emojis']['arrow'][4], ctx.me)
                                    await self.botmsg[_id].remove_reaction(
                                        "<a:help:767825933892583444>", ctx.me)
                                    return

                        except AttributeError:
                            pass
                    except TimeoutError:
                        self.he[ctx.author.id][str(ctx.command)] = False
                        await self.botmsg[_id].remove_reaction(self.bot.config['emojis']['arrow'][4], ctx.me)
                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>", ctx.me)
                        return

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @enchant.command(name='add', aliases=['adicionar'])
    async def _add(self, ctx, skill: str = None, *, enchant: str = None):
        """Comando usado pra encantar suas habilidades no rpg da Ashley
        Use ash enchant add numero_da_skill"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        
        _class_now = update["rpg"]["class_now"]

        if not update['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if skill is None:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA DIZER UMA SKILL PARA ENCANTAR`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        try:
            if 0 < int(skill) < 6:
                pass
            else:
                msg = '<:negate:721581573396496464>│`SKILL INVALIDA!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)
        except ValueError:
            msg = '<:negate:721581573396496464>│`SKILL INVALIDA!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        try:
            if update['inventory']['angel_stone'] >= 1:
                pass
            else:
                msg = '<:negate:721581573396496464>│`VOCE NÃO TEM ANGEL STONE!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)
        except KeyError:
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM ANGEL STONE!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1] == limit:
            msg = '<:negate:721581573396496464>│`ESSA SKILL JA ATINGIU O ENCANTAMENTO MAXIMO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1] >= 10:
            try:
                if update['inventory']['angel_wing'] >= 1:
                    update['inventory']['angel_wing'] -= 1
                    if update['inventory']['angel_wing'] < 1:
                        del update['inventory']['angel_wing']
                else:
                    msg = '<:negate:721581573396496464>│`VOCE NÃO TEM ANGEL WING, A PARTIR DO ENCANTAMENTO +10 VOCE ' \
                          'PRECISA DE 1 ANGEL STONE E 1 ANGEL WING!`'
                    embed = discord.Embed(color=self.bot.color, description=msg)
                    return await ctx.send(embed=embed)
            except KeyError:
                msg = '<:negate:721581573396496464>│`VOCE NÃO TEM ANGEL WING, A PARTIR DO ENCANTAMENTO +10 VOCE ' \
                      'PRECISA DE 1 ANGEL STONE E 1 ANGEL WING!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        if enchant is not None:
            if enchant.lower() == "Blessed Enchant Skill".lower():
                if "blessed_enchant_skill" in update['inventory'].keys():
                    if update['inventory']["blessed_enchant_skill"] > 0:
                        update['inventory']['blessed_enchant_skill'] -= 1
                        if update['inventory']['blessed_enchant_skill'] < 1:
                            del update['inventory']['blessed_enchant_skill']
                    else:
                        msg = '<:negate:721581573396496464>│`VOCE NÃO TEM BLESSED ENCHANT SKILL!`'
                        embed = discord.Embed(color=self.bot.color, description=msg)
                        return await ctx.send(embed=embed)
                else:
                    msg = '<:negate:721581573396496464>│`VOCE NÃO TEM BLESSED ENCHANT SKILL!`'
                    embed = discord.Embed(color=self.bot.color, description=msg)
                    return await ctx.send(embed=embed)

        update['inventory']['angel_stone'] -= 1
        if update['inventory']['angel_stone'] < 1:
            del update['inventory']['angel_stone']
        await self.bot.db.update_data(data, update, 'users')
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        self.up_chance = 0
        self.up_chance = self.chance_skill[skill][update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1]]
        chance = randint(1, 100)

        if enchant is not None:
            if enchant.lower() == "Blessed Enchant Skill".lower():
                chance = 0

        if chance < self.up_chance:
            update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1] += 1
            await self.bot.db.update_data(data, update, "users")

            msg = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `SEU ENCANTAMENTO PASSOU " \
                  f"PARA` **+{update['rpg']['sub_class'][_class_now]['skills'][int(skill) - 1]}**"
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_win"])

        elif chance == self.up_chance:
            msg = f'<:alert:739251822920728708>│{ctx.author.mention} `SEU ENCANTAMENTO FALHOU, MAS VOCE NAO REGREDIU' \
                  f' O SEU ENCANTAMENTO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_lose"])

        else:
            update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1] -= 1
            if update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1] < 0:
                update['rpg']["sub_class"][_class_now]['skills'][int(skill) - 1] = 0
            await self.bot.db.update_data(data, update, "users")

            amount = update["rpg"]["sub_class"][_class_now]["skills"][int(skill) - 1]
            msg = f'<:negate:721581573396496464>│{ctx.author.mention} `SEU ENCANTAMENTO QUEBROU, POR CONTA DISSO ' \
                  f'SEU ENCANTAMENTO REGREDIU PARA` **+{amount}**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_lose"])

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @enchant.command(name='recovery', aliases=['recuperar', 'r'])
    async def _recovery(self, ctx):
        """Comando usado pra encantar suas habilidades no rpg da Ashley
        Use ash enchant add numero_da_skill"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        _class_now = update["rpg"]["class_now"]

        if not update['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "skills" not in update['rpg'].keys():
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM ENCHANTS PARA RECUPERAR!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "recovery" in update['rpg'].keys():
            msg = '<:negate:721581573396496464>│`VOCE JA RECUPEROU SEUS ENCHANTS!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        update['rpg']["sub_class"][_class_now]['skills'] = update['rpg']['skills']
        update['rpg']["recovery"] = True  # comprovação da recuperação
        await self.bot.db.update_data(data, update, "users")

        msg = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `SEUS ENCANTAMENTOS FORAM " \
              f"RECUPERADOS PARA A CLASSE:` **{_class_now.upper()}**"
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='enchanter_armor', aliases=['ena'])
    async def enchanter_armor(self, ctx, armor: str = None, *, enchant: str = None):
        """Comando usado pra encantar suas habilidades no rpg da Ashley
        Use ash enchant add numero_da_skill"""
        query = {"_id": 0, "user_id": 1, "inventory": 1, "rpg": 1}
        data = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        if not data['rpg']['active']:
            msg = '<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        armors = ["shoulder", "breastplate", "gloves", "leggings", "boots", "shield", "necklace", "earring", "ring"]
        if armor not in armors or armor is None:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA DIZER UMA PARTE DA ARMADURA VÁLIDA, EXEMPLO:`\n' \
                  'ash ena **gloves** blessed_armor_silver,\n' \
                  '`Partes validas:`\n**"shoulder", "breastplate", "gloves", "leggings", "boots", "shield", ' \
                  '"necklace", "earring", "ring"**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if enchant is None:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA DIZER UM ENCANTAMENTO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        enchants = ["armor_hero", "armor_violet", "armor_inspiron", "armor_mystic", "armor_silver",
                    "blessed_armor_hero", "blessed_armor_violet", "blessed_armor_inspiron",
                    "blessed_armor_mystic", "blessed_armor_silver", "armor_divine", "blessed_armor_divine"]

        item_key = convert_item_name(enchant, self.bot.items)
        if item_key not in enchants:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA DIZER UM ENCANTAMENTO VÁLIDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if item_key not in data['inventory'].keys():
            msg = f'<:negate:721581573396496464>│`VOCE NAO TEM {enchant.upper()} NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _TIER = ["silver", "mystic", "inspiron", "violet", "hero", "divine"]
        tt = _TIER.index(enchant.split()[-1])
        if data['rpg']['armors'][armor][tt] >= limit:
            msg = '<:negate:721581573396496464>│`ESSA ARMADURA JA ATINGIU O ENCANTAMENTO MAXIMO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        data['inventory'][item_key] -= 1
        if data['inventory'][item_key] < 1:
            del data['inventory'][item_key]

        up_chance = self.chance_armor[str(tt + 1)][data['rpg']['armors'][armor][tt]]
        chance = randint(1, 100) if "blessed" not in enchant.lower() else 1
        if chance < up_chance:
            data['rpg']['armors'][armor][tt] += 1
            msg = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `SEU ENCANTAMENTO PASSOU " \
                  f"PARA` **+{data['rpg']['armors'][armor][tt]}**"
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_win"])

        elif chance == up_chance:
            msg = f'<:alert:739251822920728708>│{ctx.author.mention} `SEU ENCANTAMENTO FALHOU, MAS VOCE NAO REGREDIU' \
                  f' O SEU ENCANTAMENTO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_lose"])

        else:
            data['rpg']['armors'][armor][tt] -= 1
            if data['rpg']['armors'][armor][tt] < 0:
                data['rpg']['armors'][armor][tt] = 0
            msg = f'<:negate:721581573396496464>│{ctx.author.mention} `SEU ENCANTAMENTO QUEBROU, POR CONTA DISSO ' \
                  f'SEU ENCANTAMENTO REGREDIU PARA` **+{data["rpg"]["armors"][armor][tt]}**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_lose"])

        cl = await self.bot.db.cd("users")
        query = {"$set": {"rpg": data["rpg"], "inventory": data["inventory"]}}
        await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='enchanter_weapon', aliases=['enw'])
    async def enchanter_weapon(self, ctx, *, enchant: str = None):
        """Comando usado pra encantar suas habilidades no rpg da Ashley
        Use ash enchant add numero_da_skill"""
        query = {"_id": 0, "user_id": 1, "inventory": 1, "rpg": 1}
        data = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        if not data['rpg']['active']:
            msg = '<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if enchant is None:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA DIZER UM ENCANTAMENTO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        enchants = ["enchant_hero", "enchant_violet", "enchant_inspiron", "enchant_mystic", "enchant_silver",
                    "blessed_enchant_hero", "blessed_enchant_violet", "blessed_enchant_inspiron",
                    "blessed_enchant_mystic", "blessed_enchant_silver", "enchant_divine", "blessed_enchant_divine"]

        item_key = convert_item_name(enchant, self.bot.items)
        if item_key not in enchants:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA DIZER UM ENCANTAMENTO VÁLIDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if item_key not in data['inventory'].keys():
            msg = f'<:negate:721581573396496464>│`VOCE NAO TEM {enchant.upper()} NO SEU INVENTARIO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        sword_id = data['rpg']["equipped_items"]['sword']
        if sword_id is None:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA TER UMA ARMA EQUIPADA PARA ENCANTAR!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)
        sword = [i[1]["name"] for i in equips_list if i[0] == sword_id][0]

        _TIER = ["silver", "mystic", "inspiron", "violet", "hero", "divine"]
        tt = _TIER.index(sword.split()[-2 if "+" in sword.split()[-1] else -1])
        tt_enchant = _TIER.index(enchant.split()[-1])
        if tt != tt_enchant:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA USAR UM ENCANTAMENTO DA MESMA RARIDADE DA SUA ARMA!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        lw = int(str(sword.split()[-1]).replace("+", "")) if "+" in sword.split()[-1] else 0
        if lw >= limit_weapon:
            msg = '<:negate:721581573396496464>│`ESSA ARMA JA ATINGIU O SEU ENCANTAMENTO MAXIMO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        data['inventory'][item_key] -= 1
        if data['inventory'][item_key] < 1:
            del data['inventory'][item_key]

        up_chance = self.chance_weapon[str(tt + 1)][lw]
        chance = randint(1, 100) if "blessed" not in enchant.lower() else 1
        if chance < up_chance:
            sn = " ".join(sword.split()[:]) if lw == 0 else " ".join(sword.split()[:-1])
            sn += f" +{lw + 1}"
            weapon_key = [i[0] for i in equips_list if i[1]["name"] == sn][0]
            data['rpg']["equipped_items"]['sword'] = weapon_key
            msg = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `SEU ENCANTAMENTO PASSOU " \
                  f"PARA` **+{lw + 1}**"
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_win"])

        elif chance == up_chance:
            msg = f'<:alert:739251822920728708>│{ctx.author.mention} `SEU ENCANTAMENTO FALHOU, MAS VOCE NAO REGREDIU' \
                  f' O SEU ENCANTAMENTO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_lose"])

        else:
            sn = " ".join(sword.split()[:]) if lw == 0 else " ".join(sword.split()[:-1])
            sn += f" +{lw - 1}" if lw > 1 else ""
            weapon_key = [i[0] for i in equips_list if i[1]["name"] == sn][0]
            data['rpg']["equipped_items"]['sword'] = weapon_key
            msg = f'<:negate:721581573396496464>│{ctx.author.mention} `SEU ENCANTAMENTO QUEBROU, POR CONTA DISSO ' \
                  f'SEU ENCANTAMENTO REGREDIU PARA` **+{lw - 1}**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            await ctx.send(embed=embed)
            await self.bot.data.add_sts(ctx.author, ["enchants", "enchant_lose"])

        cl = await self.bot.db.cd("users")
        query = {"$set": {"rpg": data["rpg"], "inventory": data["inventory"]}}
        await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)


def setup(bot):
    bot.add_cog(EnchanterClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mENCHANTER\033[1;32m foi carregado com sucesso!\33[m')
