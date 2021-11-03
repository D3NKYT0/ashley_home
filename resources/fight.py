import copy
import discord

from asyncio import TimeoutError
from resources.utility import embed_creator
from random import randint, choice
from config import data as all_data
from resources.moon import get_moon

# variaveis globais
CLS, SET_EQUIPS, MONSTERS = all_data['skills'], all_data['set_equips'], all_data["battle"]['monsters']
LVL, MONSTERS_QUEST = [5, 10, 15, 20, 25], all_data["battle"]['quests']
SET_ARMOR = ["shoulder", "breastplate", "gloves", "leggings", "boots"]
_emo = ["<:versus:873745062192873512>", "<:HP:774699585070825503>", "<:MP:774699585620672534>"]
_ini = "<:inimigo:873756815287017552>"

# todos os equipamentos
equips_list = dict()
for ky in all_data['equips'].keys():
    for kk, vv in all_data['equips'][ky].items():
        equips_list[kk] = vv


class Entity(object):
    def __init__(self, data, is_player, is_pvp=False, is_wave=False, is_boss=False, is_mini_boss=False):
        # data da entidade
        self.data = data

        # status gerais
        self.is_player = is_player
        self.is_pvp = is_pvp
        self.is_wave = is_wave
        self.is_boss = is_boss
        self.is_mini_boss = is_mini_boss
        self.is_strike = False
        self.is_combo = False
        self.is_hold = False
        self.is_bluff = False

        # informações gerais
        self.name = self.data['name']
        self.img = self.data['img']
        self.xp = self.data['xp']
        self.level = self.data['level']
        self.effects = {}
        self.skills = {}
        self.skill = None
        self.potion = 0
        self.ls = 0  # level da skill atual (ultima skill)

        # informação de status
        self.status = self.data['status']
        self.pdef = self.data['pdef']
        self.mdef = self.data['mdef']
        self.soulshot = self.data['soulshot'] if self.is_player else None
        self.evasion = 0

        if self.is_player:
            self._class = self.data['class'] if self.level < 26 else self.data['class_now']
            self.combo = CLS[self._class]['combo']
            self.level_skill = self.data['skills']  # level de todas as skills atuais
            self.cc = [CLS[self._class]['cc'], self._class]  # critical e classe

            for c in range(5):
                if self.level >= LVL[c]:
                    self.skills[CLS[self.data['class_now']][str(c)]['name']] = CLS[self.data['class_now']][str(c)]
                else:
                    self.skills[CLS[self.data['class']][str(c)]['name']] = CLS[self.data['class']][str(c)]

            self.rate = [CLS[self._class]['rate']['life'], CLS[self._class]['rate']['mana']]
            if self.data['level'] > 25:
                self.rate[0] += CLS[self.data['class_now']]['rate']['life']
                self.rate[1] += CLS[self.data['class_now']]['rate']['mana']

            # sistema de combo
            self.combo_cont, self.next = 0, 0

            # definição do HP TOTAL e da MANA TOTAL
            self.tot_hp, self.tot_mp = self.status['con'] * self.rate[0], self.status['con'] * self.rate[1]
            self.status['hp'], self.status['mp'] = self.tot_hp, self.tot_mp

        else:
            self.is_enemy = False if self.data['enemy'] is None else True
            self.rate = [(6 + self.data['level'] // 10), (6 + self.data['level'] // 10)]
            if self.is_enemy:
                if self.data['enemy']['level'] > 25:
                    # drobra o rate (multiplicador do hp e mana)
                    self.rate = [(12 + self.data['level'] // 10), (12 + self.data['level'] // 10)]
            self.skills = self.data['atacks']
            self.level_skill = [0]
            self.cc = [self.data['cc'], "monster"]  # critical e classe
            self.tot_hp, self.tot_mp = self.status['con'] * self.rate[0], self.status['con'] * self.rate[1]
            self.status['hp'], self.status['mp'] = self.tot_hp, self.tot_mp
            # IA skills
            self.last_skill = None
            self.ultimate = False
            self.healthy = False
            self.ia_combo = False
            # classe nao definida
            self._class = None

    @property
    def get_class(self):
        return self._class

    async def verify_equips(self, ctx):
        for value in self.data["equipped_items"].values():
            if value in equips_list.keys():
                if "hero" in equips_list[value]["name"] and self.data['level'] < 80:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
                elif "violet" in equips_list[value]["name"] and self.data['level'] < 61:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
                elif "inspiron" in equips_list[value]["name"] and self.data['level'] < 41:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
                elif "mystic" in equips_list[value]["name"] and self.data['level'] < 21:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
                elif "silver" in equips_list[value]["name"] and self.data['level'] < 11:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
                elif self.data['class_now'] not in equips_list[value]["class"]:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DA SUA CLASSE!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
        return None

    def verify_combo(self, response):
        if response in self.combo:
            if self.combo[self.next] == response and not self.is_combo:
                if self.next < 2:
                    self.next += 1
                else:
                    self.is_combo = True
                    self.next = 0
                    self.combo_cont += 1
            else:
                self.next = 0 if self.combo[0] != response else self.next
                self.combo_cont += 1
        else:
            self.next = 0
            if self.is_combo:
                self.combo_cont += 1

    def calc_skill_attack(self, now, _att, lvs, c2):

        if self.cc[1] in ['necromancer', 'wizard', 'warlock']:
            tot_atk = _att * 1.75
        elif self.cc[1] in ['assassin', 'priest']:
            tot_atk = _att * 1.5
        else:
            tot_atk = _att * 1.25

        self.ls = lvs if 0 <= lvs <= 9 else 9
        ls, dado = self.ls, self.skills[c2]['damage'][self.ls]
        d1, d2 = int(dado[:dado.find('d')]), int(dado[dado.find('d') + 1:])
        dd, d3 = [d2, d2 * d1] if d2 != d2 * d1 else [d2, d2], int((lvs - 10) * 10)
        dd = [d2 + d3, d2 * d1] if lvs >= 11 else dd
        dd[1] = dd[0] + 1 if dd[0] > dd[1] else dd[1]
        _atk = [int(tot_atk / 100 * (50 + now)), int(tot_atk / 100 * (50 + (now * 10)))]

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

        return damage

    def get_skill_menu(self, entity, user, skills, wave_now):
        hate_no_mana, emojis, _hp, rr, _con = 0, list(), self.status['hp'], self.rate, self.status['con']
        _mp, ehp, econ, err = self.status['mp'], entity.status['hp'], entity.status['con'], entity.rate[0]

        extra = f" | WAVE: {wave_now}" if self.is_wave else ""

        title = f"{_emo[1]}:  [ {_hp if _hp > 0 else 0} / {_con * rr[0]} ]  |  " \
                f"{_emo[2]}:  [ {_mp if _mp > 0 else 0} / {_con * rr[1]} ]\n" \
                f"{_emo[0]}: {_ini} - [ {ehp if ehp > 0 else 0} / {econ * err} ] | LVL - {entity.level}{extra}"

        description, tot, attacks = '', len(skills), dict()
        for _ in range(0, len(skills)):
            attacks[_ + 1], lvs, c2, _att = skills[_], self.level_skill[_], skills[_], self.status['atk']

            damage = self.calc_skill_attack(_, _att, lvs, c2)
            icon, skill_type = self.skills[c2]['icon'], self.skills[c2]['type']
            emojis.append(self.skills[c2]['icon'])

            try:
                effect_skill = ", ".join(list(self.skills[c2]['effs'][self.ls].keys()))
            except (KeyError, TypeError):
                effect_skill = "sem efeito"

            rm = int(((self.status['con'] * self.rate[1]) / 100) * 35)
            ru = int(((self.status['con'] * self.rate[1]) / 100) * 50)
            a_mana = self.skills[c2]['mana'][self.ls]
            a_mana += self.level if 25 < self.level < 50 else a_mana
            a_mana += self.level * 2 if self.level >= 50 else a_mana
            _mana = a_mana if effect_skill != "cura" else rm
            _mana = ru if self.skills[c2]['type'] == "especial" else _mana

            description += f"**{_ + 1}** - {icon} **{c2.upper()}** `+{lvs}` | **{skill_type.lower()}**\n" \
                           f"`Dano:` **{damage}** | `Mana:` **{_mana}** | `Efeito(s):` **{effect_skill}**\n\n"

        regen = int(((self.status['con'] * self.rate[1]) / 100) * 50)
        pl = 3 if not self.is_wave else 3 + (wave_now // 2)

        description += f'**{tot + 1}** - <:MP:774699585620672534> **{"Pass turn MP".upper()}**\n' \
                       f'`MP Recovery:` **+{regen} de Mana**\n\n' \

        description += f'**{tot + 2}** - <:HP:774699585070825503> **{"Pass turn HP".upper()}**\n' \
                       f'`HP Recovery:` **25-35% de HP** (**{self.potion}**/{pl})\n\n' \

        description += f'**{tot + 3}** - <:fechar:749090949413732352> **Finalizar batalha**'

        skill_combo = f"\n\n**{tot + 4}** - <a:combo:834236942295891969> **[Combo] - Half Life** | **COMBO**\n" \
                      f"`Dano:` **50%** | `Mana:` **100%** | `Efeito(s):` **Sem Efeito**"

        if self.is_combo:
            description += skill_combo

        if self.soulshot[0]:
            soulshot = f"\n\n`Soulshot:` **{self.soulshot[1]}**"
            description += soulshot

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x000000
        )
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        return embed, attacks, hate_no_mana

    async def effects_resolve(self, ctx, effects, msg_return):
        type_effects = ["cegueira", "strike", "reflect", "confusion", "hold", "bluff"]
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
                        damage = int(((self.status['con'] * self.rate[1]) / 100) * self.effects[c]['damage'])

                        self.status['mp'] -= damage
                        if self.status['mp'] < 0:
                            self.status['mp'] = 0

                        if damage > 0:
                            _text6 = f"**{self.name.upper()}** `teve` **{damage}** `de mana " \
                                     f"drenada por efeito de` **{c.upper()}!**"
                            msg_return += f"{_text6}\n\n"

                    elif self.effects[c]['turns'] > 0 and c in type_effects:
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

        if not self.is_pvp and self.data["salvation"] and self.status['hp'] <= 0:
            self.data["salvation"] = False
            self.status['hp'] = self.tot_hp
            self.status['mp'] = self.tot_mp
            self.potion = 0
            await ctx.send(f'**{self.name.upper()}** `por esta equipado com` **SALVATION** `na hora da sua morte'
                           f' reviveu!`')

        return effects, msg_return

    def health_effect_resolve(self, msg_return):
        try:
            if self.skill['effs'] is not None:
                if self.is_player:
                    lvs = self.level_skill[self.skill['skill'] - 1]
                    self.ls = lvs if 0 <= lvs <= 9 else 9
                    if self.skill['effs'][self.ls]['cura']['type'] == "cura":
                        percent = self.skill['effs'][self.ls]['cura']['damage']
                        regen = int(((self.status['con'] * self.rate[0]) / 100) * percent)
                        if (self.status['hp'] + regen) <= (self.status['con'] * self.rate[0]):
                            self.status['hp'] += regen
                        else:
                            self.status['hp'] = (self.status['con'] * self.rate[0])
                        _text3 = f'**{self.name.upper()}** `recuperou` **{regen}** `de HP`'
                        msg_return += f"{_text3}\n\n"
                        self.skill = None
                else:
                    if self.skill['effs']['cura']['type'] == "cura":
                        percent = self.skill['effs']['cura']['damage']
                        regen = int(((self.status['con'] * self.rate[0]) / 100) * percent)
                        if (self.status['hp'] + regen) <= (self.status['con'] * self.rate[0]):
                            self.status['hp'] += regen
                        else:
                            self.status['hp'] = (self.status['con'] * self.rate[0])
                        _text4 = f'**{self.name.upper()}** `recuperou` **{regen}** `de HP`'
                        msg_return += f"{_text4}\n\n"
                        self.skill = None
        except (KeyError, TypeError):
            pass

        return msg_return

    async def turn(self, ctx, user, entity, wave_now=0):
        msg_return, stun, ice, self.skill = "", False, False, None,
        skills, effects = list(self.skills.keys()), list(self.effects.keys())

        if self.is_player:
            verify = await self.verify_equips(ctx)
            if verify is not None:
                return verify

            if self.combo_cont >= 3:
                self.is_combo = False
                self.combo_cont = 0

        if effects is not None:
            if 'stun' in effects:
                if self.effects['stun']['turns'] > 0:
                    stun = True

            if 'gelo' in effects:
                if self.effects['gelo']['turns'] > 0:
                    ice = True

        for eff in [['fraquesa', 'fisico'], ['silencio', 'magico']]:
            if eff[0] in effects:
                if self.effects[eff[0]]['turns'] > 0:
                    for sk in skills:
                        if self.skills[sk]['type'] == eff[1]:
                            skills.remove(sk)

        if stun is False and ice is False:
            if self.is_player:
                response = self.get_skill_menu(entity, user, skills, wave_now)
                embed, attacks, hate_no_mana = response[0], response[1], response[2]
                await ctx.send(embed=embed)

                while not ctx.bot.is_closed():
                    def check(m):
                        if m.author.id == user.id and m.channel.id == ctx.channel.id:
                            if m.content in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                return True
                        return False

                    try:
                        answer = await ctx.bot.wait_for('message', check=check, timeout=120.0)
                    except TimeoutError:
                        return "COMANDO-CANCELADO"

                    # verificador se esta sendo feito o combo
                    self.verify_combo(int(answer.content) - 1)

                    if int(answer.content) == len(skills) + 1:
                        # regeneração de MP
                        regen = int(((self.status['con'] * self.rate[1]) / 100) * 50)
                        if (self.status['mp'] + regen) <= self.tot_mp:
                            self.status['mp'] += regen
                        else:
                            self.status['mp'] = self.tot_mp

                        self.skill = "PASS-TURN-MP"
                        break

                    potion_limit = 3 if not self.is_wave else 3 + (wave_now // 2)
                    if int(answer.content) == len(skills) + 2 and self.potion < potion_limit:
                        # regeneração de HP
                        if self._class in ['priest', 'assassin', 'default']:
                            hp_regen = int(self.tot_hp / 100 * 35)

                        elif self._class in ['necromancer', 'wizard', 'warlock']:
                            hp_regen = int(self.tot_hp / 100 * 30)

                        else:
                            hp_regen = int(self.tot_hp / 100 * 25)

                        if (self.status['hp'] + hp_regen) <= self.tot_hp:
                            self.status['hp'] += hp_regen
                        else:
                            self.status['hp'] = self.tot_hp

                        self.skill = "PASS-TURN-HP"
                        self.potion += 1
                        break

                    if int(answer.content) == len(skills) + 3:
                        # cancela ou foge da batalha
                        return "BATALHA-CANCELADA"

                    if int(answer.content) == len(skills) + 4 and self.is_combo:
                        self.skill = "SKILL-COMBO"
                        self.is_combo = False
                        self.status['mp'] = 0
                        self.combo_cont = 0
                        break

                    potion_msg = False
                    for c in attacks.keys():
                        if int(c) == int(answer.content) or len(skills) + 2 == int(answer.content):
                            if int(c) == int(answer.content):

                                lvs = self.level_skill[self.skills[attacks[c]]['skill'] - 1]
                                self.ls = lvs if 0 <= lvs <= 9 else 9
                                a_mana = self.skills[attacks[c]]['mana'][self.ls]
                                a_mana += self.level if 25 < self.level < 50 else a_mana
                                a_mana += self.level * 2 if self.level >= 50 else a_mana
                                remove = a_mana

                                try:
                                    skill_effs = [k for k, v in self.skills[attacks[c]]['effs'][self.ls].items()]
                                except TypeError:
                                    skill_effs = ['nenhum']

                                heal = False
                                for eff in skill_effs:
                                    if eff == "cura":
                                        heal = True

                                if heal:
                                    remove = int(self.tot_mp / 100 * 35)

                                if self.skills[attacks[c]]['type'] == "especial":
                                    remove = int(self.tot_mp / 100 * 50)

                            else:  # que desgraça é essa ?
                                remove = 10000

                            potion_limit = 3 if not self.is_wave else 3 + (wave_now // 2)
                            if self.potion >= potion_limit and len(skills) + 2 == int(answer.content):

                                if self.is_wave:
                                    msg = f"`MATE OUTRO MONSTRO PARA AUMENTAR O SEU LIMITE, ESCOLHA UMA SKILL OU " \
                                          f"PASSE A VEZ...`\n**Obs:** Passar a vez regenera a mana ou vida!"
                                else:
                                    msg = f"`ENTÃO ESCOLHA UMA SKILL OU PASSE A VEZ...`\n" \
                                          f"**Obs:** Passar a vez regenera a mana ou vida!"

                                description = f"{user.name.upper()} VOCÊ JA ATINGIU O LIMITE DE POÇÃO DE VIDA!`\n{msg}"
                                embed = discord.Embed(description=description, color=0x000000)
                                embed.set_author(name=user.name, icon_url=user.avatar_url)

                                if not potion_msg:
                                    await ctx.send(embed=embed)
                                    self.next, potion_msg = 0, True
                                    hate_no_mana += 1
                                    if hate_no_mana > 5:
                                        await ctx.send(f"`Ficar repetindo esse tipo de msg no mesmo turno é "
                                                       f"considerado pratica` **ANTI-JOGO** `por isso a batalha foi"
                                                       f" cancelada e voce perdeu:` **{user.name.upper()}**")

                                        return "BATALHA-CANCELADA"

                            elif self.status['mp'] >= remove:
                                self.status['mp'] -= remove
                                self.skill = attacks[c]
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

                    if self.skill is not None:
                        break

            else:
                # IA Choice Skill
                _FALAS = [
                    f"`HA HA HA HA! QUEM FOI O LOUCO QUE DISSE QUE VOCE ERA UM` **HEROI**\n",
                    f"`HA HA HA HA! SE VOCE NAO BATER MAIS FORTE EU` **IREI**\n",
                    f"`HA HA HA HA! DEPOIS DESSE ATAQUE VAI PRECISAR FAZER UMA ARMADURA` **NOVA**\n",
                    f"`HA HA HA HA! TALVEZ EU DEVESSE EMPRESTAR A ARMA DO MEU SERVO,` **SEU FRACOTE**\n",
                    f"`HA HA HA HA! NAO ME SUBESTIME` **INSOLENTE**\n"
                ]
                try:
                    chance_skill_choice, mini_b = randint(1, 100), self.is_mini_boss

                    if self.tot_hp / 100 * 85 <= self.status["hp"] <= self.tot_hp or self.status["hp"] > self.tot_hp:
                        if not self.ultimate:
                            if "quest" in self.name.lower() or self.is_mini_boss:
                                if self.is_mini_boss and entity.is_player:
                                    if entity.get_class in ["warrior", "paladin"]:
                                        self.skill = "SKILL-COMBO"
                                        if self.is_mini_boss:
                                            msg_return += f"`olha só o que temos aqui... um` **{entity.get_class}**\n"
                                else:
                                    self.skill = choice(["especial - magia negra", "especial - ataque direto"])

                            elif self.name == "Mago Negro":
                                self.skill = choice(["magia negra", "ataque direto"])

                            elif self.name in ["Dragão Branco de Olho Azuis", "Slifer - O Dragão dos Céus"]:
                                self.skill = choice(["luz divina", "ataque supremo"])

                            else:
                                self.skill = choice(["luz divina", "ataque supremo"])

                            self.ultimate = True
                        else:
                            new_skills_full = list(skills)
                            new_skills_full.pop(skills.index("cura"))
                            self.ultimate, self.skill = False, choice(new_skills_full)
                            if self.is_mini_boss:
                                msg_return += f"`quando eu enfrento um fraco como voce, é assim que eu faço!`\n"

                    elif self.tot_hp / 100 * 65 <= self.status["hp"] <= self.tot_hp / 100 * 85 and not mini_b:
                        self.skill = choice(["stun", "gelo", "manadrain"])
                        if self.is_mini_boss:
                            msg_return += f"`HA HA HA HA! tente escapar` **DISSO**\n"

                    elif self.tot_hp / 100 * 35 <= self.status["hp"] <= self.tot_hp / 100 * 65 and not mini_b:
                        if chance_skill_choice <= 50 and not self.healthy:
                            self.skill = "cura"
                        self.skill = choice(["veneno", "queimadura", "silencio", "fraquesa"])
                        if self.is_mini_boss and self.skill == "cura":
                            msg_return += f"`VOCE NAO VAI ME VENCER TAO FACILMENTE!`\n"

                        if self.is_mini_boss and self.skill != "cura":
                            msg_return += f"`IREI DEBILITADO DE UMA FORMA OU OUTRA!`\n"

                    elif self.status["hp"] <= self.tot_hp / 100 * 35:
                        if 50 <= chance_skill_choice <= 75:
                            self.skill = choice(["stun", "gelo", "manadrain"])
                        if chance_skill_choice <= 50 and not self.healthy:
                            self.skill = "cura"
                        self.skill = choice(skills)

                        if self.is_mini_boss and self.skill == "cura":
                            msg_return += f"`VOCE NAO VAI ME VENCER TAO FACILMENTE!`\n"

                        if self.is_mini_boss and self.skill != "cura":
                            msg_return += f"`MALDITOOOOOOO VAI PARA O INFERNO!!`\n"

                    elif self.status["hp"] <= self.tot_hp / 100 * 15:
                        if chance_skill_choice <= 50 and not self.ia_combo:
                            self.skill = "SKILL-COMBO"
                        self.skill = choice(skills)

                        if self.is_mini_boss and self.skill == "SKILL-COMBO":
                            msg_return += f"`HA HA HA HA! VOCE ACHA QUE VAI SOBREVIVER DEPOIS` **DISSO**\n"

                        if self.is_mini_boss and self.skill != "SKILL-COMBO":
                            msg_return += f"`HA HA HA HA! TALVEZ EU DEVA MANDAR FAZER SEU` **CAIXAO**\n"

                    else:
                        new_skills_other = list(skills)
                        new_skills_other.pop(skills.index("cura"))
                        self.skill = choice(new_skills_other)

                        if self.is_mini_boss:
                            msg_return += choice(_FALAS)

                except (ValueError, IndexError, KeyError):
                    self.skill = choice(skills)
                    if self.is_mini_boss:
                        msg_return += choice(_FALAS)

                if self.last_skill == self.skill:  # proibido repetir a mesma skill duas vezes seguidas
                    try:
                        new_skills = list(skills)
                        new_skills.pop(skills.index(self.skill))
                        self.skill = choice(new_skills)
                        if self.is_mini_boss:
                            msg_return += choice(_FALAS)
                    except (ValueError, IndexError, KeyError):
                        self.skill = choice(skills)
                        if self.is_mini_boss:
                            msg_return += choice(_FALAS)

                self.last_skill = self.skill
                self.healthy = True if self.skill == "cura" else False
                self.ia_combo = True if self.skill == "SKILL-COMBO" else False

                if self.skill is None:
                    self.skill = "cura"

                _text1 = f"**{self.name.upper()}** `ESCOLHEU O ATAQUE:` **{self.skill.upper()}**"
                msg_return += f"{_text1}\n\n"

            if self.skill is not None and self.skill not in ["PASS-TURN-MP", "PASS-TURN-HP", "SKILL-COMBO"]:
                self.skill = self.skills[self.skill]

        else:
            _text2 = f'**{self.name.upper()}** `esta` **{"STUNADO" if stun else "CONGELADO"}**'
            msg_return += f"{_text2}\n\n"

        msg_return = self.health_effect_resolve(msg_return)
        effects, msg_return = await self.effects_resolve(ctx, effects, msg_return)
        hp_max, monster, img_ = self.status['con'] * self.rate[0], not self.is_player, None
        embed_ = embed_creator(msg_return, img_, monster, hp_max, self.status['hp'], self.img, self.name)

        if msg_return != "":
            await ctx.send(embed=embed_)

        return self.skill

    def verify_effect(self, effects, entity):
        skull, drain, bluff, hit_kill, hold = False, False, False, False, False
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
            if "hold" in effects.keys():
                if effects["hold"]["turns"] > 0 and entity.is_player:
                    hold = True
            if "lethal" in effects.keys():
                if effects["lethal"]["turns"] > 0 and not self.is_boss and not self.is_mini_boss:
                    if "bluff" in effects.keys() and "cegueira" in effects.keys():
                        if effects["bluff"]["turns"] > 0 and effects["cegueira"]["turns"] > 0:
                            hit_kill = True
        return skull, drain, bluff, hit_kill, hold

    def chance_effect_skill(self, entity, skill, msg_return, test, act_eff, bluff, confusion, lvs, _eff, chance):
        if skill['effs'] is not None and act_eff:
            key = [k for k in skill['effs'][self.ls].keys()] if test else [k for k in skill['effs'].keys()]
            for c in key:

                _percent = (1, 100) if not bluff else (25, 100)  # aumenta 25% de chance de pegar efeito de skill
                chance_effect, rate_chance = randint(_percent[0], _percent[1]) + lvs, 96.0
                rate_chance -= entity.status['luk'] * 0.5 if entity.status['luk'] > 0 else 0

                chance = True if chance_effect > rate_chance else False

                # o primeiro strike sempre vai funcionar
                if c == "strike" and not entity.is_strike:
                    entity.is_strike, chance = True, True

                # o primeiro hold sempre vai funcionar
                if c == "hold" and not entity.is_hold:
                    entity.is_hold, chance = True, True

                # o primeiro bluff sempre vai funcionar
                if c == "bluff" and not entity.is_bluff:
                    entity.is_bluff, chance = True, True

                if confusion:
                    chance = False

                if chance:
                    if c in self.effects.keys():
                        if self.effects[c]['turns'] > 0:
                            # laranja
                            _text1 = f'🟠 **{self.name.upper()}** `ainda está sob o efeito de` **{c.upper()}**'
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
                        # verde
                        _text2 = f'🟢 **{self.name.upper()}** `recebeu o efeito de` **{c.upper()}** `por` ' \
                                 f'**{turns}** `turno{"s" if turns > 1 else ""}`'
                        msg_return += f"{_text2}\n\n"
                else:
                    # vermelho
                    _text3 = f'🔴 **{self.name.upper()}** `não recebeu o efeito de` **{c.upper()}**'
                    msg_return += f"{_text3}\n\n"

        if skill['effs'] is not None and not act_eff:
            # branco
            _text_strike = f'⚪ **{self.name.upper()}** `não pode receber efeito dessa skill por que` ' \
                           f'**{entity.name}** `esta sob o efeito de` **STRIKE**'
            msg_return += f"{_text_strike}\n\n"

        return entity, msg_return, _eff, chance

    def calc_damage_skill(self, skill, test, lvs, enemy_cc, enemy_atk):
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

        return damage

    async def chance_critical(self, ctx, enemy_cc, enemy_luk, test, skull, damage, lethal):
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

        return critical, damage

    async def damage(self, ctx, entity, skill):
        if skill is None:
            description = f'**{entity.name.upper()}** `não atacou nesse turno!`'
            monster = not self.is_player if self.is_pvp else self.is_player
            img_ = "https://uploads1.yugioh.com/card_images/2110/detail/2004.jpg?1385103024"
            embed_ = embed_creator(description, img_, monster, self.tot_hp, self.status['hp'], entity.img, entity.name)
            await ctx.send(embed=embed_)
            return entity

        if skill == "PASS-TURN-MP":
            description = f'**{entity.name.upper()}** `passou o turno, usando a poção de MANA!`'
            monster = not self.is_player if self.is_pvp else self.is_player
            img_ = "https://vignette.wikia.nocookie.net/yugioh/images/6/61/OfferingstotheDoomed-TF04-JP-VG.png"
            embed_ = embed_creator(description, img_, monster, self.tot_hp, self.status['hp'], entity.img, entity.name)
            await ctx.send(embed=embed_)
            return entity

        if skill == "PASS-TURN-HP":
            description = f'**{entity.name.upper()}** `passou o turno, usando a poção de VIDA!`'
            monster = not self.is_player if self.is_pvp else self.is_player
            img_ = "https://vignette.wikia.nocookie.net/yugioh/images/6/61/OfferingstotheDoomed-TF04-JP-VG.png"
            embed_ = embed_creator(description, img_, monster, self.tot_hp, self.status['hp'], entity.img, entity.name)
            await ctx.send(embed=embed_)
            return entity

        if skill == "SKILL-COMBO":
            _damage = self.status['hp'] // 2
            _damage = _damage if not self.is_boss and not self.is_mini_boss else 0

            self.status['hp'] -= _damage
            if self.status['hp'] < 0:
                self.status['hp'] = 0

            monster = not self.is_player if self.is_pvp else self.is_player
            bmsg = "\n`boss e mini boss são imune a combo!`" if self.is_boss or self.is_mini_boss else ""
            description = f'**{self.name.upper()}** `recebeu` **{_damage}** `de dano, por levar um ` **combo!**{bmsg}'
            img = "https://media.giphy.com/media/INEBdVgN59AbWhyZCk/giphy.gif"
            embed_ = embed_creator(description, img, monster, self.tot_hp, self.status['hp'], self.img, self.name)
            await ctx.send(embed=embed_)

            if not self.is_pvp and self.data["salvation"] and self.status['hp'] <= 0:
                self.data["salvation"] = False
                self.status['hp'] = self.tot_hp
                self.status['mp'] = self.tot_mp
                self.potion = 0
                await ctx.send(f'**{self.name.upper()}** `por esta equipado com` **SALVATION** `na hora da sua morte'
                               f' reviveu!`')

            return entity

        msg_return, lethal, _eff, chance, msg_drain, test = "", False, 0, False, "", not self.is_player or self.is_pvp
        skull, drain, bluff, hit_kill, hold = self.verify_effect(self.effects, entity)
        lvs = entity.level_skill[int(skill['skill']) - 1] if test else entity.level_skill[0]
        self.ls, confusion, act_eff, _soulshot, bda, reflect = lvs if 0 <= lvs <= 9 else 9, False, True, 0, 0, False

        if entity.effects is not None:

            if "confusion" in entity.effects.keys():
                if entity.effects["confusion"]["turns"] > 0:
                    confusion = True if randint(1, 2) == 1 else False

            if "strike" in entity.effects.keys():
                if entity.effects["strike"]['turns'] > 0:
                    act_eff = False

        resp = self.chance_effect_skill(entity, skill, msg_return, test, act_eff, bluff, confusion, lvs, _eff, chance)
        entity, msg_return, _eff, chance = resp[0], resp[1], resp[2], resp[3]
        damage = self.calc_damage_skill(skill, test, lvs, entity.cc, entity.status['atk'])

        # verificação especial para que o EFFECT nao perca o seu primeiro turno
        skull, drain, bluff, hit_kill, hold = self.verify_effect(self.effects, entity)

        if test:
            if entity.soulshot[0] and entity.soulshot[1] > 1:
                entity.soulshot[1] -= 1
                _soulshot = CLS[entity.data['class_now']]['soulshot']
                bda = int(damage / 100 * _soulshot) if int(damage / 100 * _soulshot) < 100 else 99
                if skull:
                    bda = 0
                damage += bda

        res = await self.chance_critical(ctx, entity.cc, entity.status['luk'], test, skull, damage, lethal)
        defense, critical, damage = self.pdef if skill['type'] == "fisico" else self.mdef, res[0], res[1]

        if skill['type'] == "especial":
            defense = choice([self.pdef, self.mdef])
        _defense = randint(int(defense / 2), defense) if defense > 2 else defense

        if "reflect" in entity.effects.keys():
            reflect, damage = True, int(damage / 2)
            entity.effects['reflect']['damage'] = damage

        armor_now = _defense if _defense > 0 else 1
        armor_now = randint(int(armor_now * 0.75), armor_now)

        # efeito da hold
        if hold:
            armor_now = 0

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

            if self.is_boss and "_id" in entity.data.keys():
                ctx.bot.boss_players[entity.data["_id"]]["hpt"] += dn
                ctx.bot.boss_players[entity.data["_id"]]["hit"] += 1

                if critical:
                    ctx.bot.boss_players[entity.data["_id"]]["crit"] += 1

                if chance:
                    ctx.bot.boss_players[entity.data["_id"]]["eff"] += 1 * _eff

                # sistema de pontuação de MPV
                _score = ctx.bot.boss_players[entity.data["_id"]]["hpt"] // 1000 * 50
                _score += ctx.bot.boss_players[entity.data["_id"]]["hit"] * 25
                _score += ctx.bot.boss_players[entity.data["_id"]]["crit"] * 35
                _score += ctx.bot.boss_players[entity.data["_id"]]["eff"] * 50
                _score -= ctx.bot.boss_players[entity.data["_id"]]["dano"] // 1000 * 25

                ctx.bot.boss_players[entity.data["_id"]]["score"] = _score
                ctx.bot.boss_players[entity.data["_id"]]["dano_boss"] += dn

            if "_id" in self.data.keys():
                if self.data["_id"] in ctx.bot.boss_players.keys() and ctx.bot.boss_live:
                    if entity.name == ctx.bot.boss_now.name:
                        ctx.bot.boss_players[self.data["_id"]]["dano"] += dn

            if drain:
                dr = self.effects["drain"]["damage"]
                _dr = dr if dr == 50 else randint(50, dr)
                recovery = int(dn / 100 * _dr)
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

        monster = not self.is_player if self.is_pvp else self.is_player
        bed_ = embed_creator(msg_return, skill['img'], monster, self.tot_hp, self.status['hp'], self.img, self.name)
        if msg_return != "":
            await ctx.send(embed=bed_)

        if not self.is_pvp and self.data["salvation"] and self.status['hp'] <= 0:
            self.data["salvation"] = False
            self.status['hp'] = self.tot_hp
            self.status['mp'] = self.tot_mp
            self.potion = 0
            await ctx.send(f'**{self.name.upper()}** `por esta equipado com` **SALVATION** `na hora da sua morte'
                           f' reviveu!`')

        return entity


class Ext(object):
    def __init__(self):
        self.eq = equips_list
        self.m = MONSTERS
        self.q = MONSTERS_QUEST
        self.mini_boss = all_data['attribute']['moon_mini_boss']
        self.mb = all_data['battle']['miniboss']

    def set_monster(self, db_player, mini_boss=False):
        lvl = db_player['level']
        dif = 2 if lvl < 2 else 3 if 2 <= lvl <= 9 else 5 if 10 <= lvl <= 30 else 10 if 31 <= lvl <= 50 else 15
        min_, max_ = lvl - 5 if lvl - 5 > 1 else 1, lvl + dif if lvl + dif <= 60 else 60
        min_, moon_data = min_ if min_ <= 55 else 55, get_moon()
        mini_boss_monster = self.mb[self.mini_boss[moon_data[0]]]
        _monster = choice([m for m in self.m if min_ < self.m[self.m.index(m)]['level'] < max_])
        db_monster = copy.deepcopy(_monster) if not mini_boss else copy.deepcopy(mini_boss_monster)
        db_monster['enemy'], db_monster["pdef"], db_monster["mdef"] = db_player, lvl, lvl

        for k in db_monster["status"].keys():
            if db_player['level'] > 25:
                db_monster["status"][k] += randint(2, 4)

        for sts in db_player['equipped_items'].keys():
            if db_player['equipped_items'][sts] is not None:
                db_monster["status"]['luk'] += randint(0, 1)
                db_monster["status"]['atk'] += randint(0, 2)
                db_monster["status"]['con'] += randint(0, 2)

        db_monster["salvation"] = False
        return db_monster

    def set_monster_raid(self, db_player, rr):
        # configuração do monstro
        _min, _max = 20 + rr if rr + 20 < 55 else 55, 30 + rr if rr + 30 < 50 else 60
        m = [m for m in self.m if _min < self.m[self.m.index(m)]['level'] < _max]
        _monster = choice(m + self.q) if db_player["ESPECIAL"] else choice(m)
        _monster_now = copy.deepcopy(_monster)
        _monster_now['enemy'] = db_player
        _monster_now["pdef"] = rr * 20
        _monster_now["mdef"] = rr * 20
        _monster_now["status"]["con"] += rr * 10
        _monster_now["status"]["atk"] += rr * 2

        for k in _monster_now["status"].keys():
            if db_player['level'] > 25:
                _monster_now["status"][k] += randint(2, 4)

        for sts in db_player['equipped_items'].keys():
            if db_player['equipped_items'][sts] is not None:
                _monster_now["status"]["atk"] += randint(0, 2)
                _monster_now["status"]["con"] += randint(0, 2)
                _monster_now["status"]["luk"] += randint(0, 2)

        _monster_now["salvation"] = False
        return _monster_now

    def set_player(self, user, data):
        # configuração do player
        db_player, _class = data['rpg'], data["rpg"]["class_now"]
        db_player["_id"], db_player['name'] = user.id, user.name
        db_player["img"] = user.avatar_url_as(format="png")
        db_player["pdef"], db_player["mdef"] = 0, 0
        _db_class = data["rpg"]["sub_class"][_class]
        db_player["xp"], db_player["level"] = _db_class["xp"], _db_class["level"]

        # configurando soulshot
        soul, amount, set_e = False, 0, list()
        if data['rpg']["equipped_items"]['consumable'] is not None:
            if 'soushot' in data['rpg']["equipped_items"]['consumable']:
                soul = True
                amount += 1
                if data['rpg']["equipped_items"]['consumable'] in data['rpg']['items'].keys():
                    amount += data['rpg']['items'][data['rpg']["equipped_items"]['consumable']]

        # adicionando os bonus de class conforme o nivel do player
        for k in db_player["status"].keys():
            try:
                db_player["status"][k] += CLS[db_player['class']]['modifier'][k]
                if db_player['level'] > 25:
                    db_player["status"][k] += CLS[db_player['class_now']]['modifier'][k]
                if db_player['level'] > 49:
                    db_player["status"][k] += CLS[db_player['class_now']]['modifier_50'][k]
                if db_player['level'] > 79:
                    db_player["status"][k] += CLS[db_player['class_now']]['modifier_80'][k]
            except KeyError:
                pass

        salvation = False
        # configurando os equipamentos
        for c in db_player['equipped_items'].keys():
            if db_player["equipped_items"][c] is not None:

                if c == "consumable" and db_player["equipped_items"][c] == "salvation":
                    salvation = True

                if c in SET_ARMOR:
                    set_e.append(str(db_player['equipped_items'][c]))

                db_player["pdef"] += self.eq[db_player['equipped_items'][c]]['pdef']
                db_player["mdef"] += self.eq[db_player['equipped_items'][c]]['mdef']

                for name in db_player["status"].keys():
                    try:
                        db_player["status"][name] += self.eq[db_player['equipped_items'][c]]['modifier'][name]
                    except KeyError:
                        pass

        # configurando o set de bonus de uma armadura completa
        for kkk in SET_EQUIPS.values():
            if len([e for e in set_e if e in kkk['set']]) == 5:
                db_player["pdef"] += kkk["pdef"]
                db_player["mdef"] += kkk["mdef"]
                for name in db_player["status"].keys():
                    try:
                        db_player["status"][name] += kkk['modifier'][name]
                    except KeyError:
                        pass

        # sistema de enchants armors
        enchant, _pdef, _mdef = db_player['armors'], 0, 0
        for key in enchant.keys():
            for k in enchant[key]:
                if key in ["necklace", "earring", "ring"]:
                    _mdef += k * 0.25
                else:
                    _pdef += k * 0.25
                if k == 16:
                    db_player["status"]['con'] += 1

        db_player["pdef"] += int(_pdef)
        db_player["mdef"] += int(_mdef)
        db_player["soulshot"] = [soul, amount]
        db_player["salvation"] = salvation

        return db_player
