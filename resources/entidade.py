import discord

from asyncio import sleep, TimeoutError
from resources.utility import embed_creator
from random import randint, choice
from config import data

_class = data['skills']
levels = [5, 10, 15, 20, 25]

equips_list = dict()
for ky in data['equips'].keys():
    for kk, vv in data['equips'][ky].items():
        equips_list[kk] = vv


class Entity(object):
    def __init__(self, db, is_player, pvp=False, raid=False):
        self.db = db
        self.name = self.db['name']
        self.status = self.db['status']
        self.xp = self.db['xp']
        self.lvl = self.db['level']
        self.effects = {}
        self.atacks = {}
        self.atack = None
        self.chance = False
        self.is_player = is_player
        self.pdef = self.db['pdef']
        self.mdef = self.db['mdef']
        self.img = self.db['img']
        self.ln = self.db['lower_net']
        self.pvp = pvp
        self.raid = raid
        self.ls = 0
        self.potion = 0

        if self.is_player:
            # sistema de soulshot
            self.soulshot = self.db['soulshot']

            # sistema de strike
            self.is_strike = False

            for c in range(5):
                if self.lvl >= levels[c]:
                    self.combo = _class[self.db['class_now']]['combo']
                    self.atacks[_class[self.db['class_now']][str(c)]['name']] = _class[self.db['class_now']][str(c)]
                else:
                    self.combo = _class[self.db['class']]['combo']
                    self.atacks[_class[self.db['class']][str(c)]['name']] = _class[self.db['class']][str(c)]

            self.rate = [_class[self.db['class']]['rate']['life'], _class[self.db['class']]['rate']['mana']]
            if self.db['level'] > 25:
                self.rate[0] += _class[self.db['class_now']]['rate']['life']
                self.rate[1] += _class[self.db['class_now']]['rate']['mana']

            self.level_skill = self.db['skills']

            if self.db['level'] > 25:
                self.cc = [_class[self.db['class_now']]['cc'], self.db['class_now']]
            else:
                self.cc = [_class[self.db['class']]['cc'], self.db['class']]

            self.p_class = self.db['class_now'] if self.db['level'] > 25 else self.db['class']

            # sistema de combo
            self.is_combo = False
            self.combo_cont = 0
            self.next = 0
            self.boss = False

            # sistema de enchants armors
            self.enchant = self.db['armors']
            _pdef, _mdef = 0, 0
            for key in self.enchant.keys():
                for k in self.enchant[key]:
                    if key in ["necklace", "earring", "ring"]:
                        _mdef += k * 0.25
                    else:
                        _pdef += k * 0.25
                    if k == 16:
                        self.status['con'] += 1

            self.pdef += int(_pdef)
            self.mdef += int(_mdef)

            self.status['hp'] = self.status['con'] * self.rate[0]
            self.status['mp'] = self.status['con'] * self.rate[1]

        else:
            if self.db['enemy'] is not None:
                if self.db['enemy']['level'] > 25:
                    self.rate = [(12 + self.db['level'] // 10), (12 + self.db['level'] // 10)]
                else:
                    self.rate = [(6 + self.db['level'] // 10), (6 + self.db['level'] // 10)]
            else:
                self.rate = [(6 + self.db['level'] // 10), (6 + self.db['level'] // 10)]

            self.atacks = self.db['atacks']
            self.status['hp'] = self.status['con'] * self.rate[0]
            self.status['mp'] = self.status['con'] * self.rate[1]
            self.level_skill = 0
            self.cc = [self.db['cc'], "monster"]
            try:
                boss = self.db["boss"]
            except KeyError:
                boss = False
            self.boss = boss

    async def turn(self, e_info, bot, ctx, user=None, raid_num=0):
        msg_return, stun, ice, self.atack, atacks = "", False, False, None, list(self.atacks.keys())
        effects = None if self.effects is None else list(self.effects.keys())
        user = ctx.author if user is None else user

        if self.is_player:
            for value in self.db["equipped_items"].values():
                if value in equips_list.keys():
                    if "hero" in equips_list[value]["name"] and self.db['level'] < 80:
                        await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                       "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                        return "BATALHA-CANCELADA"
                    elif "violet" in equips_list[value]["name"] and self.db['level'] < 61:
                        await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                       "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                        return "BATALHA-CANCELADA"
                    elif "inspiron" in equips_list[value]["name"] and self.db['level'] < 41:
                        await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                       "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                        return "BATALHA-CANCELADA"
                    elif "mystic" in equips_list[value]["name"] and self.db['level'] < 21:
                        await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                       "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                        return "BATALHA-CANCELADA"
                    elif "silver" in equips_list[value]["name"] and self.db['level'] < 11:
                        await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                       "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                        return "BATALHA-CANCELADA"

        if self.is_player:
            if self.combo_cont >= 3:
                self.is_combo = False
                self.combo_cont = 0

        if effects is not None:
            for c in ['stun', 'gelo']:
                if c in effects:
                    if self.effects[c]['turns'] > 0:
                        if c == "stun":
                            stun = True
                        if c == "gelo":
                            ice = True

        for c in [['fraquesa', 'fisico'], ['silencio', 'magico']]:
            if c[0] in effects:
                if self.effects[c[0]]['turns'] > 0:
                    for c2 in atacks:
                        if self.atacks[c2]['type'] == c[1]:
                            atacks.remove(c2)

        if stun is False and ice is False:
            if self.is_player:
                _emo = ["<:versus:873745062192873512>", "<:HP:774699585070825503>", "<:MP:774699585620672534>"]
                _ini = "<:inimigo:873756815287017552>"
                hate_no_mana, emojis, _hp, rr, _con = 0, list(), self.status['hp'], self.rate, self.status['con']
                _mp, ehp, econ, err = self.status['mp'], e_info[0]['hp'], e_info[0]['con'], e_info[1][0]
                title = f"{_emo[1]}:  [ {_hp if _hp > 0 else 0} / {_con * rr[0]} ]  |  " \
                        f"{_emo[2]}:  [ {_mp if _mp > 0 else 0} / {_con * rr[1]} ]\n" \
                        f"{_emo[0]}: {_ini} - [ {ehp if ehp > 0 else 0} / {econ * err} ] | LVL - {e_info[3]}"
                description, tot, attks = '', len(atacks), dict()
                for c in range(0, len(atacks)):
                    attks[c + 1], lvs, c2, _att = atacks[c], self.level_skill[c], atacks[c], self.status['atk']

                    if self.cc[1] in ['necromancer', 'wizard', 'warlock']:
                        tot_atk = _att * 1.75
                    elif self.cc[1] in ['assassin', 'priest']:
                        tot_atk = _att * 1.5
                    else:
                        tot_atk = _att * 1.25

                    self.ls = lvs if 0 <= lvs <= 9 else 9
                    ls, dado = self.ls, self.atacks[c2]['damage'][self.ls]
                    d1, d2 = int(dado[:dado.find('d')]), int(dado[dado.find('d') + 1:])
                    dd, d3 = [d2, d2 * d1] if d2 != d2 * d1 else [d2, d2], int((lvs - 10) * 10)
                    dd = [d2 + d3, d2 * d1] if lvs >= 11 else dd
                    dd[1] = dd[0] + 1 if dd[0] > dd[1] else dd[1]
                    _atk = [int(tot_atk / 100 * (50 + c)), int(tot_atk / 100 * (50 + (c * 10)))]

                    if _atk[0] != _atk[1]:
                        if dd[0] != dd[1]:
                            damage = f"{_atk[0] + dd[0]}-{_atk[1] + dd[1]}"
                        else:
                            damage = f"{_atk[0] + dd[0]}-{_atk[1] + dd[0]}"
                    else:
                        if dd[0] != dd[1]:
                            damage = f"{_atk[0] + dd[0]}-{_atk[0] + dd[1]}"
                        else:
                            damage = f"{_atk[0] + dd[0]}"

                    icon, skill_type = self.atacks[c2]['icon'], self.atacks[c2]['type']
                    emojis.append(self.atacks[c2]['icon'])

                    try:
                        effect_skill = ", ".join(list(self.atacks[c2]['effs'][self.ls].keys()))
                    except KeyError:
                        effect_skill = "sem efeito"
                    except TypeError:
                        effect_skill = "sem efeito"

                    rm = int(((self.status['con'] * self.rate[1]) / 100) * 35)
                    ru = int(((self.status['con'] * self.rate[1]) / 100) * 50)
                    a_mana = self.atacks[c2]['mana'][self.ls]
                    a_mana += self.lvl if 25 < self.lvl < 50 else a_mana
                    a_mana += self.lvl * 2 if self.lvl >= 50 else a_mana
                    _mana = a_mana if effect_skill != "cura" else rm
                    _mana = ru if self.atacks[c2]['type'] == "especial" else _mana

                    description += f"**{c + 1}** - {icon} **{c2.upper()}** `+{lvs}` | **{skill_type.lower()}**\n" \
                                   f"`Dano:` **{damage}** | `Mana:` **{_mana}** | `Efeito(s):` **{effect_skill}**\n\n"

                regen = int(((self.status['con'] * self.rate[1]) / 100) * 50)
                pl = 3 if not self.raid else 3 + (raid_num // 2)

                description += f'**{tot + 1}** - <:MP:774699585620672534> **{"Pass turn MP".upper()}**\n' \
                               f'`MP Recovery:` **+{regen} de Mana**\n\n' \
                               f'**{tot + 2}** - <:HP:774699585070825503> **{"Pass turn HP".upper()}**\n' \
                               f'`HP Recovery:` **25-35% de HP** (**{self.potion}**/{pl})\n\n' \
                               f'**{tot + 3}** - <:fechar:749090949413732352> **Finalizar batalha**'

                skillcombo = f"\n\n**{tot + 4}** - <a:combo:834236942295891969> **[Combo] - Half Life** | **COMBO**\n" \
                             f"`Dano:` **50%** | `Mana:` **100%** | `Efeito(s):` **Sem Efeito**"
                if self.is_combo:
                    description += skillcombo

                if self.soulshot[0]:
                    soulshot = f"\n\n`Soulshot:` **{self.soulshot[1]}**"
                    description += soulshot

                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=0x000000
                )
                embed.set_author(name=user.name, icon_url=user.avatar_url)
                await ctx.send(embed=embed)

                while not bot.is_closed():
                    def check(m):
                        if m.author.id == user.id and m.channel.id == ctx.channel.id:
                            if m.content in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                return True
                        return False

                    try:
                        answer = await bot.wait_for('message', check=check, timeout=60.0)
                    except TimeoutError:
                        return "COMANDO-CANCELADO"

                    ns = int(answer.content) - 1
                    if ns in self.combo:
                        if self.combo[self.next] == ns and not self.is_combo:
                            if self.next < 2:
                                self.next += 1
                            else:
                                self.is_combo = True
                                self.next = 0
                                self.combo_cont += 1
                        else:
                            self.next = 0 if self.combo[0] != ns else self.next
                            self.combo_cont += 1
                    else:
                        self.next = 0
                        if self.is_combo:
                            self.combo_cont += 1

                    try:
                        if int(answer.content) == tot + 4 and self.is_combo:
                            self.atack = "SKILL-COMBO"
                            self.is_combo = False
                            self.status['mp'] = 0
                            self.combo_cont = 0
                            break

                        if int(answer.content) == tot + 1:
                            # regeneração de MP
                            regen = int(((self.status['con'] * self.rate[1]) / 100) * 50)
                            if (self.status['mp'] + regen) <= (self.status['con'] * self.rate[1]):
                                self.status['mp'] += regen
                            else:
                                self.status['mp'] = (self.status['con'] * self.rate[1])

                            self.atack = "PASS-TURN-MP"
                            break

                        potion_limit = 3 if not self.raid else 3 + (raid_num // 2)
                        if int(answer.content) == tot + 2 and self.potion < potion_limit:
                            # regeneração de HP
                            if self.p_class in ['priest', 'assassin', 'default']:
                                hp_regen = int(((self.status['con'] * self.rate[0]) / 100) * 35)

                            elif self.p_class in ['necromancer', 'wizard', 'warlock']:
                                hp_regen = int(((self.status['con'] * self.rate[0]) / 100) * 30)

                            else:
                                hp_regen = int(((self.status['con'] * self.rate[0]) / 100) * 25)

                            if (self.status['hp'] + hp_regen) <= (self.status['con'] * self.rate[0]):
                                self.status['hp'] += hp_regen
                            else:
                                self.status['hp'] = (self.status['con'] * self.rate[0])

                            self.atack = "PASS-TURN-HP"
                            self.potion += 1
                            break

                        if int(answer.content) == tot + 3:
                            return "BATALHA-CANCELADA"

                    except AttributeError:
                        pass

                    potion_msg = False
                    for c in attks.keys():
                        if int(c) == int(answer.content) or tot + 2 == int(answer.content):
                            if int(c) == int(answer.content):
                                test_atack = attks[c]
                                _atack = test_atack
                                lvs = self.level_skill[self.atacks[_atack]['skill'] - 1]
                                self.ls = lvs if 0 <= lvs <= 9 else 9

                                a_mana = self.atacks[_atack]['mana'][self.ls]
                                a_mana += self.lvl if 25 < self.lvl < 50 else a_mana
                                a_mana += self.lvl * 2 if self.lvl >= 50 else a_mana
                                remove = a_mana

                                try:
                                    effects_skill = [k for k, v in self.atacks[_atack]['effs'][self.ls].items()]
                                except TypeError:
                                    effects_skill = ['nenhum']
                                heal = False
                                for eff in effects_skill:
                                    if eff == "cura":
                                        heal = True
                                if heal:
                                    remove = int(((self.status['con'] * self.rate[1]) / 100) * 35)
                                if self.atacks[_atack]['type'] == "especial":
                                    remove = int(((self.status['con'] * self.rate[1]) / 100) * 50)
                            else:
                                remove = 10000
                                test_atack = None

                            potion_limit = 3 if not self.raid else 3 + (raid_num // 2)
                            if self.potion >= potion_limit and tot + 2 == int(answer.content):
                                if self.raid:
                                    msg = f"`MATE OUTRO MONSTRO PARA AUMENTAR O SEU LIMITE, ESCOLHA UMA SKILL OU " \
                                          f"PASSE A VEZ...`\n**Obs:** Passar a vez regenera a mana ou vida!"
                                else:
                                    msg = f"`ENTÃO ESCOLHA UMA SKILL OU PASSE A VEZ...`\n" \
                                          f"**Obs:** Passar a vez regenera a mana ou vida!"
                                embed = discord.Embed(
                                    description=f"`{user.name.upper()} VOCÊ JA ATINGIU O LIMITE DE POÇÃO DE VIDA!`\n"
                                                f"{msg}", color=0x000000)
                                embed.set_author(name=user.name, icon_url=user.avatar_url)
                                if not potion_msg:
                                    await ctx.send(embed=embed)
                                    self.next = 0
                                    potion_msg = True
                                    hate_no_mana += 1
                                    if hate_no_mana > 5:
                                        await ctx.send(f"`Ficar repetindo esse tipo de msg no mesmo turno é "
                                                       f"considerado pratica` **ANTI-JOGO** `por isso a batalha foi"
                                                       f" cancelada e voce perdeu:` **{user.name.upper()}**")
                                        return "BATALHA-CANCELADA"

                            elif self.status['mp'] >= remove:
                                self.status['mp'] -= remove
                                self.atack = test_atack
                                break

                            else:
                                embed = discord.Embed(
                                    description=f"`{user.name.upper()} VOCÊ NÃO TEM MANA O SUFICIENTE!`\n"
                                                f"`ENTÃO ESCOLHA OUTRA SKILL OU PASSE A VEZ...`\n"
                                                f"**Obs:** Passar a vez regenera a mana ou vida!",
                                    color=0x000000
                                )
                                embed.set_author(name=user.name, icon_url=user.avatar_url)
                                await ctx.send(embed=embed)
                                self.next = 0
                                hate_no_mana += 1
                                if hate_no_mana > 5:
                                    await ctx.send(f"`Ficar repetindo esse tipo de msg no mesmo turno é "
                                                   f"considerado pratica` **ANTI-JOGO** `por isso a batalha foi"
                                                   f" cancelada e voce perdeu:` **{user.name.upper()}**")
                                    return "BATALHA-CANCELADA"

                    if self.atack is not None:
                        break
            else:
                self.atack = choice(atacks)
                _text1 = f"**{self.name.upper()}** `ESCOLHEU O ATAQUE:` **{self.atack.upper()}**"
                msg_return += f"{_text1}\n\n"

            if self.atack is not None and self.atack not in ["PASS-TURN-MP", "PASS-TURN-HP", "SKILL-COMBO"]:
                self.atack = self.atacks[self.atack]

        else:
            _text2 = f'**{self.name.upper()}** `esta` **{"STUNADO" if stun else "CONGELADO"}**'
            msg_return += f"{_text2}\n\n"

        try:
            if self.atack['effs'] is not None:
                if self.is_player:
                    lvs = self.level_skill[self.atack['skill'] - 1]
                    self.ls = lvs if 0 <= lvs <= 9 else 9
                    if self.atack['effs'][self.ls]['cura']['type'] == "cura":
                        percent = self.atack['effs'][self.ls]['cura']['damage']
                        regen = int(((self.status['con'] * self.rate[0]) / 100) * percent)
                        if (self.status['hp'] + regen) <= (self.status['con'] * self.rate[0]):
                            self.status['hp'] += regen
                        else:
                            self.status['hp'] = (self.status['con'] * self.rate[0])
                        _text3 = f'**{self.name.upper()}** `recuperou` **{regen}** `de HP`'
                        msg_return += f"{_text3}\n\n"
                        self.atack = None
                else:
                    if self.atack['effs']['cura']['type'] == "cura":
                        percent = self.atack['effs']['cura']['damage']
                        regen = int(((self.status['con'] * self.rate[0]) / 100) * percent)
                        if (self.status['hp'] + regen) <= (self.status['con'] * self.rate[0]):
                            self.status['hp'] += regen
                        else:
                            self.status['hp'] = (self.status['con'] * self.rate[0])
                        _text4 = f'**{self.name.upper()}** `recuperou` **{regen}** `de HP`'
                        msg_return += f"{_text4}\n\n"
                        self.atack = None
        except KeyError:
            pass
        except TypeError:
            pass

        _non_effects = ["cegueira", "strike", "reflect", "confusion", "hold", "bluff"]
        if effects is not None:
            for c in effects:
                try:
                    if 'damage' in self.effects[c]['type']:
                        damage, burn = self.effects[c]['damage'], ""

                        if c == "queimadura" and randint(1, 2) == 2:
                            damage += int(damage / 100 * 50)
                            burn += "\n `levou 50% a mais por queimadura profunda`"

                        if c == "veneno" and randint(1, 2) == 2:
                            damage += int(damage / 100 * 50)
                            burn += "\n `levou 50% a mais por intoxicação aguda`"

                        self.status['hp'] -= damage
                        if self.status['hp'] < 0:
                            self.status['hp'] = 0
                        if damage > 0:
                            _text5 = f"**{self.name.upper()}** `sofreu` **{damage}** `de dano " \
                                     f"por efeito de` **{c.upper()}!**{burn}"
                            msg_return += f"{_text5}\n\n"
                    elif 'manadrain' in self.effects[c]['type']:
                        damage = self.effects[c]['damage']
                        damage = int(((self.status['con'] * self.rate[1]) / 100) * damage)
                        self.status['mp'] -= damage
                        if self.status['mp'] < 0:
                            self.status['mp'] = 0
                        if damage > 0:
                            _text6 = f"**{self.name.upper()}** `teve` **{damage}** `de mana " \
                                     f"drenada por efeito de` **{c.upper()}!**"
                            msg_return += f"{_text6}\n\n"
                    elif self.effects[c]['turns'] > 0 and c in _non_effects:
                        _text7 = f"**{self.name.upper()}** `esta sobe o efeito de` **{c.upper()}!**"
                        msg_return += f"{_text7}\n\n"
                except KeyError:
                    pass

                try:
                    if self.effects[c]['turns'] > 0:
                        if "reflect" in self.effects.keys():
                            if self.effects['reflect']['damage'] > 0:
                                self.effects['reflect']['damage'] = 0
                            self.effects[c]['turns'] -= 1
                        else:
                            self.effects[c]['turns'] -= 1

                    if self.effects[c]['turns'] < 1:
                        del self.effects[c]
                except KeyError:
                    pass

        hp_max = self.status['con'] * self.rate[0]
        monster = not self.is_player
        img_ = None
        embed_ = embed_creator(msg_return, img_, monster, hp_max, self.status['hp'], self.img, self.ln, self.name)
        if msg_return != "":
            await ctx.send(embed=embed_)
        return self.atack

    async def damage(self, ctx, entity, skill, enemy_atk):
        lvl_skill, name, enemy_cc, enemy_img = entity.level_skill, entity.name, entity.cc, entity.img
        enemy_luk, effects, msg_return, lethal, _eff = entity.status['luk'], entity.effects, "", False, 0
        bluff, hit_kill, drain, msg_drain, test = False, False, False, "", not self.is_player or self.pvp

        skull = False
        if effects is not None:
            if "skull" in effects.keys():
                if effects["skull"]["turns"] > 0:
                    skull = True
            if "reflect" in effects.keys():
                if effects["reflect"]["turns"] > 0:
                    effects['reflect']['damage'] = 0
            if "drain" in effects.keys():
                if effects["drain"]["turns"] > 0:
                    drain = True
            if "bluff" in effects.keys():
                if effects["bluff"]["turns"] > 0:
                    bluff = True
            if "lethal" in effects.keys():
                if effects["lethal"]["turns"] > 0 and not self.boss:
                    if "bluff" in effects.keys() and "cegueira" in effects.keys():
                        if effects["bluff"]["turns"] > 0 and effects["cegueira"]["turns"] > 0:
                            hit_kill = True

        if skill is None:
            description = f'**{name.upper()}** `não atacou nesse turno!`'
            hp_max = self.status['con'] * self.rate[0]
            monster = not self.is_player if self.pvp else self.is_player
            img_ = "https://uploads1.yugioh.com/card_images/2110/detail/2004.jpg?1385103024"
            embed_ = embed_creator(description, img_, monster, hp_max, self.status['hp'], enemy_img, self.ln, self.name)
            await ctx.send(embed=embed_)
            return entity

        if skill == "PASS-TURN-MP":
            description = f'**{name.upper()}** `passou o turno, usando a poção de MANA!`'
            hp_max = self.status['con'] * self.rate[0]
            monster = not self.is_player if self.pvp else self.is_player
            img_ = "https://vignette.wikia.nocookie.net/yugioh/images/6/61/OfferingstotheDoomed-TF04-JP-VG.png"
            embed_ = embed_creator(description, img_, monster, hp_max, self.status['hp'], enemy_img, self.ln, self.name)
            await ctx.send(embed=embed_)
            return entity

        if skill == "PASS-TURN-HP":
            description = f'**{name.upper()}** `passou o turno, usando a poção de VIDA!`'
            hp_max = self.status['con'] * self.rate[0]
            monster = not self.is_player if self.pvp else self.is_player
            img_ = "https://vignette.wikia.nocookie.net/yugioh/images/6/61/OfferingstotheDoomed-TF04-JP-VG.png"
            embed_ = embed_creator(description, img_, monster, hp_max, self.status['hp'], enemy_img, self.ln, self.name)
            await ctx.send(embed=embed_)
            return entity

        if skill == "SKILL-COMBO":
            _damage = self.status['hp'] // 2
            _damage = _damage if not self.boss else 0
            self.status['hp'] -= _damage
            if self.status['hp'] < 0:
                self.status['hp'] = 0
            hp_max = self.status['con'] * self.rate[0]
            monster = not self.is_player if self.pvp else self.is_player
            bmsg = "\n`boss é imune a combo!`" if self.boss else ""
            description = f'**{self.name.upper()}** `recebeu` **{_damage}** `de dano, por levar um ` **combo!**{bmsg}'
            img = "https://media.giphy.com/media/INEBdVgN59AbWhyZCk/giphy.gif"
            embed_ = embed_creator(description, img, monster, hp_max, self.status['hp'], self.img, self.ln, self.name)
            await ctx.send(embed=embed_)
            return entity

        lvs = lvl_skill[int(skill['skill']) - 1] if test else lvl_skill
        self.ls = lvs if 0 <= lvs <= 9 else 9
        confusion, act_eff = False, True

        if entity.effects is not None:
            if "confusion" in entity.effects.keys():
                if entity.effects["confusion"]["turns"] > 0:
                    confusion = True if randint(1, 2) == 1 else False
            if "strike" in entity.effects.keys():
                if entity.effects["strike"]['turns'] > 0:
                    act_eff = False

        if skill['effs'] is not None and act_eff:
            key = [k for k in skill['effs'][self.ls].keys()] if test else [k for k in skill['effs'].keys()]
            for c in key:

                _percent = (1, 100) if not bluff else (25, 100)  # aumenta 25% de chance de pegar efeito de skill
                chance_effect, rate_chance = randint(_percent[0], _percent[1]) + lvs, 96.0
                rate_chance -= enemy_luk * 0.5 if enemy_luk > 0 else 0

                self.chance = True if chance_effect > rate_chance else False
                if c == "strike" and not entity.is_strike:
                    entity.is_strike, self.chance = True, True

                if confusion:
                    self.chance = False

                if self.chance:
                    if c in self.effects.keys():
                        if self.effects[c]['turns'] > 0:
                            _text1 = f'**{self.name.upper()}** `ainda está sob o efeito de` **{c.upper()}**'
                            msg_return += f"{_text1}\n\n"
                    else:
                        if test:
                            self.effects[c] = skill['effs'][self.ls][c]
                            min_turn, max_turn = 2, skill['effs'][self.ls][c]['turns']
                            min_turn = 3 if c in ["bluff"] else min_turn
                            max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                            self.effects[c]['turns'] = randint(min_turn, max_turn)
                        else:
                            self.effects[c] = skill['effs'][c]
                            min_turn, max_turn = 2, skill['effs'][c]['turns']
                            min_turn = 3 if c in ["bluff"] else min_turn
                            max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                            self.effects[c]['turns'] = randint(min_turn, max_turn)

                        turns = self.effects[c]['turns']
                        _eff += turns
                        _text2 = f'**{self.name.upper()}** `recebeu o efeito de` **{c.upper()}** `por` ' \
                                 f'**{turns}** `turno{"s" if turns > 1 else ""}`'
                        msg_return += f"{_text2}\n\n"
                else:
                    _text3 = f'**{self.name.upper()}** `não recebeu o efeito de` **{c.upper()}**'
                    msg_return += f"{_text3}\n\n"

        if skill['effs'] is not None and not act_eff:
            _text_strike = f'**{self.name.upper()}** `não pode receber efeito dessa skill por que` **{entity.name}**' \
                           f' `esta sob o efeito de` **STRIKE**'
            msg_return += f"{_text_strike}\n\n"

        damage_enchant = skill['damage'][self.ls] if test else skill['damage']
        d1 = int(damage_enchant[:damage_enchant.find('d')])
        d2 = int(damage_enchant[damage_enchant.find('d') + 1:])
        dd, d3 = [d2, d2 * d1] if d2 != d2 * d1 else [d2, d2], int((lvs - 10) * 10)
        dd = [d2 + d3, d2 * d1] if lvs >= 11 else dd
        dd[1] = dd[0] + 1 if dd[0] > dd[1] else dd[1]
        bk = randint(dd[0], dd[1]) if dd[0] != dd[1] else dd[0]

        if test:
            if enemy_cc[1] in ['necromancer', 'wizard', 'warlock']:
                tot_enemy_atk = enemy_atk * 1.4
            elif enemy_cc[1] in ['assassin', 'priest']:
                tot_enemy_atk = enemy_atk * 1.1
            else:
                tot_enemy_atk = enemy_atk * 1.2
            damage_skill = int(tot_enemy_atk / 100 * (50 + randint(skill['skill'], skill['skill'] * 10)))
            damage = damage_skill + bk
        else:
            damage = enemy_atk + bk

        _soulshot, bda = 0, 0
        if test:
            if entity.soulshot[0] and entity.soulshot[1] > 1:
                entity.soulshot[1] -= 1
                _soulshot = _class[entity.db['class_now']]['soulshot']
                bda = int(damage / 100 * _soulshot) if int(damage / 100 * _soulshot) < 100 else 99
                if skull:
                    bda = 0
                damage += bda

        critical, critical_chance, critical_damage, value_critical = False, randint(1, 30), enemy_cc[0], 29
        if enemy_cc[1] in ['necromancer', 'wizard', 'warlock']:
            value_critical = 27
        if enemy_cc[1] in ['assassin', 'priest']:
            value_critical = 25
        if test:
            value_critical -= int(enemy_luk / 5)
        if "cegueira" in self.effects.keys():
            lethal = True if self.effects["cegueira"]['turns'] > 0 else False
        if critical_chance >= value_critical or lethal:
            critical = True

        if skull:
            critical = False

        if critical:
            _cd = randint(int(critical_damage / 2), critical_damage)
            damage = int(damage + (damage / 100 * _cd))
            embed = discord.Embed(title="CRITICAL", color=0x38105e)
            file = discord.File("images/elements/critical.gif", filename="critical.gif")
            embed.set_thumbnail(url="attachment://critical.gif")
            await ctx.send(file=file, embed=embed)

        defense = self.pdef if skill['type'] == "fisico" else self.mdef
        if skill['type'] == "especial":
            defense = choice([self.pdef, self.mdef])
        _defense = randint(int(defense / 2), defense) if defense > 2 else defense

        reflect = False
        if "reflect" in effects.keys():
            reflect, damage = True, int(damage / 2)
            effects['reflect']['damage'] = damage

        armor_now = _defense if _defense > 0 else 1
        percent = abs(int(armor_now / (damage / 100)))
        if percent < 50:
            dn = abs(int(damage - armor_now))
        else:
            dn_chance = randint(1, 100)
            dn = abs(int(damage - armor_now) if dn_chance < 25 else int(damage / 100 * randint(50, 70)))

        if reflect:
            _text4 = f'**{self.name.upper()}** `refletiu` **50%** `do dano que recebeu`'
            msg_return += f"{_text4}\n\n"

        if dn < 0:
            _text5 = f'**{self.name.upper()}** `obsorveu todo o dano e recebeu` **0** `de dano`'
            msg_return += f"{_text5}\n\n"
        else:

            if self.boss:
                ctx.bot.boss_players[ctx.author.id]["hpt"] += dn
                ctx.bot.boss_players[ctx.author.id]["hit"] += 1
                if critical:
                    ctx.bot.boss_players[ctx.author.id]["crit"] += 1
                if self.chance:
                    ctx.bot.boss_players[ctx.author.id]["eff"] += 1 * _eff
                # sistema de pontuação de MPV
                _score = ctx.bot.boss_players[ctx.author.id]["hpt"] // 1000 * 50
                _score += ctx.bot.boss_players[ctx.author.id]["hit"] * 25
                _score += ctx.bot.boss_players[ctx.author.id]["crit"] * 35
                _score += ctx.bot.boss_players[ctx.author.id]["eff"] * 50
                _score -= ctx.bot.boss_players[ctx.author.id]["dano"] // 1000 * 25
                ctx.bot.boss_players[ctx.author.id]["score"] = _score

            if "_id" in self.db.keys():
                if self.db["_id"] in ctx.bot.boss_players.keys() and ctx.bot.boss_live:
                    if entity.name == ctx.bot.boss_now.name:
                        ctx.bot.boss_players[self.db["_id"]]["dano"] += dn

            if drain:
                recovery = int(dn / 100 * effects["drain"]["damage"])
                entity.status['hp'] += recovery
                if entity.status['hp'] > entity.status['con'] * entity.rate[0]:
                    entity.status['hp'] = entity.status['con'] * entity.rate[0]
                msg_drain += f'\n**{entity.name.upper()}** `recuperou` **{recovery}** `de HP pelo efeito` **drain**'

            if not confusion and not hit_kill:
                self.status['hp'] -= dn
                if self.status['hp'] < 0:
                    self.status['hp'] = 0
                bb = "" if bda == 0 else f"\n`e` **{_soulshot}%** `de dano a mais por causa da soulshot:` **{bda}**"
                if defense > 0:
                    descrip = f'**{self.name.upper()}** `absorveu` **{armor_now}** `de dano, recebendo` **{dn}** {bb}'
                else:
                    descrip = f'**{self.name.upper()}** `recebeu` **{damage}** `de dano` {bb}'
            elif hit_kill and not confusion:
                _lethal = self.status['hp'] - 1
                self.status['hp'] = 1
                descrip = f'**{self.name.upper()}** `recebeu` **{_lethal}** `de dano` **LETHAL!**'
            else:
                entity.status['hp'] -= dn
                if entity.status['hp'] < 0:
                    entity.status['hp'] = 0
                bb = "" if bda == 0 else f"\n`e` **{_soulshot}%** `de dano a mais por causa da soulshot:` **{bda}**"
                confusy = "`, por está confuso o golpe acertou a si mesmo!`"
                descrip = f'**{entity.name.upper()}** `recebeu` **{damage}** `de dano` {bb}{confusy}'

            descrip += msg_drain
            msg_return += f"{descrip}\n\n"

        hp_max = self.status['con'] * self.rate[0]
        monster = not self.is_player if self.pvp else self.is_player
        bed_ = embed_creator(msg_return, skill['img'], monster, hp_max, self.status['hp'], self.img, self.ln, self.name)
        if msg_return != "":
            await ctx.send(embed=bed_)

        entity.effects = effects
        return entity
