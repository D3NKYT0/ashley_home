import copy
import disnake

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
_EFFECTS = ["bluff", "ignition", "rage", "impulse", "confusion", "target", "headshot"]

# todos os equipamentos
equips_list = dict()
for ky in all_data['equips'].keys():
    for kk, vv in all_data['equips'][ky].items():
        equips_list[kk] = vv


class Entity(object):
    def __init__(self, data, is_player, is_pvp=False, is_wave=False, is_boss=False, is_mini_boss=False, is_champ=False):
        # data da entidade
        self.data = data

        # status gerais
        self.is_player = is_player
        self.is_pvp = is_pvp
        self.is_wave = is_wave
        self.is_boss = is_boss
        self.is_mini_boss = is_mini_boss
        self.is_champion = is_champ
        self.is_strike = False
        self.is_combo = False
        self.is_hold = False
        self.is_bluff = False
        self.is_ignition = False
        self.is_duelist = False
        self.is_charge = False
        self.is_rage = False
        self.is_target = False
        self.is_confine = True
        self.is_cegueira = False
        self.is_bluff = False
        self.smoke_now = False

        # informações gerais
        self.name = self.data['name']
        self.img = self.data['img']
        self.xp = self.data['xp']
        self.level = self.data['level']
        self.effects = {}
        self.skills = {}
        self.skills_p = {}  # skills de passiva
        self.skill = None
        self.potion = 0
        self.ls = 0  # level da skill atual (ultima skill)
        self.rage_damage = 0  # dano do efeito acumulado de RAGE

        # informação de status
        self.status = self.data['status']
        self.pdef = self.data['pdef']
        self.mdef = self.data['mdef']
        self.soulshot = self.data['soulshot'] if self.is_player else None
        self.evasion = 0

        # limit de uso de skill
        self.limit = [0, 0, 0, 0, 0]  # skill 1 a 5

        self.OPTIONS = list()

        # sistema de passiva
        self.passive = ""
        self.is_passive = False
        self.is_combo_passive = False

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

            self.rate = [CLS["default"]['rate']['life'], CLS["default"]['rate']['mana']]
            if self.data['level'] > 25:
                self.rate[0] += CLS[self.data['class_now']]['rate']['life']
                self.rate[1] += CLS[self.data['class_now']]['rate']['mana']

            # sistema de combo
            self.combo_cont, self.next = 0, 0

            # definição do HP TOTAL e da MANA TOTAL
            self.tot_hp, lvl = self.status['con'] * self.rate[0], self.data['level']
            self.tot_mp = CLS[self.data['class_now']]['tot_mana'] if lvl > 25 else CLS["default"]['tot_mana']
            self.tot_mp += (self.rate[1] + self.data['mana_bonus']) * 2
            self.status['hp'], self.status['mp'] = self.tot_hp, self.tot_mp

            # sistema de passivas

            if self.data['class_now'] == "paladin":
                self.passive = self.data['class_now']
                self.progress = 0

                self.devotion = 0
                self.confine = None

            elif self.data['class_now'] == "warrior":
                self.passive = self.data['class_now']
                self.progress = 0

                self.passive_mode = 0
                self.passive_key = ["atk", "def"]
                self.passive_progress = [0, 0]

                self.IRON_FISTS = False
                self.TITAN_WALL = False

                self.ultimate_defense = self.pdef + self.mdef

            elif self.data['class_now'] == "necromancer":
                self.passive = self.data['class_now']
                self.progress = 0

                for c in range(5):
                    if self.level >= LVL[c]:
                        _SK = f"T{c}"
                        self.skills_p[CLS[self.data['class_now']][_SK]['name']] = CLS[self.data['class_now']][_SK]
                    else:
                        self.skills[CLS[self.data['class']][str(c)]['name']] = CLS[self.data['class']][str(c)]

            elif self.data['class_now'] == "wizard":
                self.passive = self.data['class_now']
                self.progress = 0
                self.stack = 1
                self.SPELLCASTER_FIRER = False

                for c in range(5):
                    if self.level >= LVL[c]:
                        if c in [1, 4]:
                            _SK = f"N{c}"
                            self.skills_p[CLS[self.data['class_now']][_SK]['name']] = CLS[self.data['class_now']][_SK]
                        else:
                            _SK = f"{c}"
                            self.skills_p[CLS[self.data['class_now']][_SK]['name']] = CLS[self.data['class_now']][_SK]
                    else:
                        self.skills[CLS[self.data['class']][str(c)]['name']] = CLS[self.data['class']][str(c)]

            elif self.data['class_now'] == "warlock":
                self.passive = self.data['class_now']
                self.progress = 0
                self.stack = 1
                self.SPEAR_OF_DESTINY = False

            elif self.data['class_now'] == "priest":
                self.passive = self.data['class_now']
                self.type_skill_passive = 0
                self.type_skill_await = 1
                self.progress = 0

            elif self.data['class_now'] == "assassin":
                self.passive = self.data['class_now']
                self.progress = 0
                self.CLAWS_STUCK = False

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

    class View(disnake.ui.View):
        def __init__(self, author):
            self.author_id = author
            super().__init__()

        async def interaction_check(self, interaction):
            if interaction.user.id != self.author_id:
                msg = "🚫 `VOCÊ NÃO PODE INTERAGIR AQUI!`"
                await interaction.response.send_message(content=msg, ephemeral=True)
                return False
            else:
                return True

    class SelectSkill(disnake.ui.Select):
        def __init__(self, options):
            self.value = 0
            self.options_param = options
            super().__init__(placeholder='Escolha uma skill', min_values=1, max_values=1, options=self.options_param)

        async def callback(self, interaction: disnake.Interaction):
            self.value = self.values[0]
            self.disabled = True
            try:
                await interaction.response.edit_message(view=None)
            except disnake.errors.NotFound:
                return

    @property
    def get_class(self):
        return self._class

    async def verify_equips(self, ctx):
        for value in self.data["equipped_items"].values():
            if value in equips_list.keys():
                if "divine" in equips_list[value]["name"] and self.data['level'] < 99:
                    await ctx.send("<:negate:721581573396496464>│`VOCÊ TEM UM ITEM QUE NAO É DO SEU LEVEL!`\n"
                                   "`PARA CONCERTAR ISSO USE O COMANDO:` **ASH E RESET**")
                    return "BATALHA-CANCELADA"
                elif "hero" in equips_list[value]["name"] and self.data['level'] < 80:
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

    def calc_skill_attack(self, now, _att, lvs, c2, skills_now):

        if self.cc[1] in ['necromancer', 'wizard', 'warlock']:
            tot_atk = int(_att * 1.6)
        elif self.cc[1] in ['assassin', 'priest']:
            tot_atk = int(_att * 1.4)
        else:
            tot_atk = int(_att * 1.2)

        self.ls = lvs if 0 <= lvs <= 9 else 9  # verificação de segurança para o limit (+10) de bonus
        # as skills so tem bonus ate o limit do indice 9 (+10) apos isso so existe bonus de ataque
        dado = skills_now[c2]['damage'][self.ls]  # define o valor variante do dano do enchant
        d1, d2 = int(dado[:dado.find('d')]), int(dado[dado.find('d') + 1:])  # define os dados
        dd, d3 = [d2, d2 * d1] if d2 != d2 * d1 else [d2, d2], int((lvs - 10) * 10)
        # dd = é a variante do valor maximo e minimo dos dados, onde o indice 0 e 1 correspondem a
        # um RANDINT(dd[0], dd[1]) [valor minimo e maximo]
        # d3 = é um valor bonus sobre a quantidade de encantamentos sobressalentes
        # +11 ate +16 (adicionando x * 10, para cada encantamento adicional)
        # esse valor de d3 é inserido no indice 0 da variavel dd
        dd = [d2 + d3, d2 * d1] if lvs >= 11 else dd  # adiciona d3 se o encantamento for maior do que +10
        dd[1] = dd[0] + 1 if dd[0] > dd[1] else dd[1]  # verificação de segurança para quando o dd[0] for maior
        # do que o dd[1] adicionando um variante para o "RANDINT()" function
        skill_number = now + 1
        _atk = [int(tot_atk / 100 * (50 + skill_number)), int(tot_atk / 100 * (50 + (skill_number * 10)))]
        # _atk = é um variante da força total da skill junto com o bonus de encantamento e o atributo de atk
        # o calculo consiste em 50% do valor do atak atual + x% da skill atual (1 a 5)
        # no proximo valor se repente o calculo para o x% * 10 da variante do RANDINT()

        _damage = [_atk[0] + dd[0], _atk[1] + dd[1]]  # aqui ocorre a soma do dano de atk mais o bonus de enchant

        if _damage[0] == _damage[1]:
            damage = f"{_damage[0]}"  # se os valores sao iquais nao existe variação
        else:
            damage = f"{_damage[0]}-{_damage[1]}"  # se os valores sao diferentes existe variação

        return damage  # o retorno do dano estimado nao calcula efeitos ou soulshots

    def get_skill_menu(self, entity, user, skills, wave_now, passive_skill, skills_now):
        hate_no_mana, emojis, _hp, rr, _con = 0, list(), self.status['hp'], self.rate, self.status['con']
        _mp, ehp, econ, err = self.status['mp'], entity.status['hp'], entity.status['con'], entity.rate[0]
        hate_no_limit = 0

        extra = f" | WAVE: {wave_now}" if self.is_wave else ""

        title = f"{_emo[1]}:  [ {_hp if _hp > 0 else 0} / {_con * rr[0]} ]  |  " \
                f"{_emo[2]}:  [ {_mp if _mp > 0 else 0} / {self.tot_mp} ]\n" \
                f"{_emo[0]}: {_ini} - [ {ehp if ehp > 0 else 0} / {econ * err} ] | LVL - {entity.level}{extra}"

        description = ""

        if not passive_skill and not self.is_passive:

            self.OPTIONS.append(
                disnake.SelectOption(
                    emoji="<:skill_base:912134358813523989>",
                    label="0 - SKILL BASE | COMUM",
                    description="Dano: Base | Mana: 0 | Efeito(s): sem efeito",
                    value=str(0)
                )
            )

        else:
            passive_name = CLS[self.data['class_now']]["passive"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"]['icon']
            passive_amount = CLS[self.data['class_now']]["passive"]['amount']
            text_passive = ""
            if not self.is_passive:
                progress_now = self.progress
                if self.passive == "warrior":
                    key = self.passive_key[self.passive_mode]
                    passive_name = CLS[self.data['class_now']]["passive"][key]['name']
                    passive_icon = CLS[self.data['class_now']]["passive"][key]['icon']
                    passive_amount = CLS[self.data['class_now']]["passive"][key]['amount']
                    progress_now = self.passive_progress[self.passive_mode]

                text_passive += f"Progress: {progress_now}/{passive_amount}"

                selection = disnake.SelectOption(
                    emoji=passive_icon,
                    label=f"0 - {passive_name.upper()} | PASSIVE",
                    description=f"Dano: base | Mana: 0 | {text_passive}",
                    value=str(0)
                )
                self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "priest":
            passive_name = CLS[self.data['class_now']]["passive"][f"{self.type_skill_passive}"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"][f"{self.type_skill_passive}"]['icon']
            text_passive = "veneno, fraquesa" if self.type_skill_passive == 0 else "curse, queimadura"
            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | DH MODE",
                description=f"Dano: base | Mana: 0 | {text_passive}",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "assassin":
            passive_name = CLS[self.data['class_now']]["passive"]["0"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"]["0"]['icon']
            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | MIRAGE MODE",
                description=f"Dano: base | Mana: 0 | Efeito(s): gelo",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "warlock":
            passive_name = CLS[self.data['class_now']]["passive"][f"{self.stack}"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"][f"{self.stack}"]['icon']
            if self.stack == 1:
                text_passive = "silencio"
            elif self.stack == 2:
                text_passive = "silencio, fraquesa"
            elif self.stack == 3:
                text_passive = "silencio, fraquesa, strike"
            else:
                text_passive = "silencio, fraquesa, strike, skull"

            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | SOD MODE",
                description=f"Dano: base | Mana: 0 | {text_passive}",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "wizard":
            passive_name = CLS[self.data['class_now']]["passive"][f"{self.stack}"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"][f"{self.stack}"]['icon']
            if self.stack == 1:
                text_passive = "looping"
            elif self.stack == 2:
                text_passive = "looping"
            elif self.stack == 3:
                text_passive = "looping"
            else:
                text_passive = "looping"

            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | SF MODE",
                description=f"Dano: base | Mana: 0 | {text_passive}",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "warrior":
            passive_name = CLS[self.data['class_now']]["passive"][f"{self.passive_mode}"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"][f"{self.passive_mode}"]['icon']
            text_passive = "impulse" if self.passive_mode == 0 else "impulse"
            _mode = "IRON FISTS" if self.passive_mode == 0 else "TITAN WALL"
            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | {_mode} MODE",
                description=f"Dano: base | Mana: 0 | {text_passive}",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "necromancer":
            passive_name = CLS[self.data['class_now']]["passive"]["0"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"]["0"]['icon']
            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | SDM MODE",
                description=f"Dano: base | Mana: 0 | Efeito(s): detached",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        if self.is_passive and self.passive == "paladin":
            passive_name = CLS[self.data['class_now']]["passive"]["0"]['name']
            passive_icon = CLS[self.data['class_now']]["passive"]["0"]['icon']
            selection = disnake.SelectOption(
                emoji=passive_icon,
                label=f"0 - {passive_name.upper()} | RESPLENDENT MODE",
                description=f"Dano: base | Mana: 0 | Efeito(s): mirror",
                value=str(0)
            )
            self.OPTIONS.append(selection)

        tot, attacks = len(skills), dict()
        for _ in range(0, len(skills)):
            attacks[_ + 1], lvs, c2, _att = skills[_], self.level_skill[_], skills[_], self.status['atk']
            ls = self.data["skill_level"][_][0]
            damage = self.calc_skill_attack(_, _att, lvs, c2, skills_now)
            icon, skill_type = skills_now[c2]['icon'], skills_now[c2]['type']
            emojis.append(skills_now[c2]['icon'])

            if self.limit[skills_now[c2]['skill'] - 1] >= skills_now[attacks[_ + 1]]['limit'][ls]:
                icon = "<:skill_limit:912156419527172107>"

            try:
                effect_skill = ", ".join(list(skills_now[c2]['effs'][self.ls].keys()))
            except (KeyError, TypeError):
                effect_skill = "sem efeito"

            rm = int((self.tot_mp / 100) * 35)
            ru = int((self.tot_mp / 100) * 50)
            a_mana = skills_now[c2]['mana'][ls]
            _mana = a_mana if effect_skill != "cura" else rm
            _mana = ru if skills_now[c2]['type'] == "especial" else _mana
            lvn = ls + 1

            concentration, conjure = False, False

            if "conjure" in self.effects.keys():
                if self.effects["conjure"]['turns'] > 0:
                    conjure = True

            if "concentration" in self.effects.keys():
                if self.effects["concentration"]['turns'] > 0:
                    concentration = True

            if conjure or concentration:
                _mana = _mana // 2

            self.OPTIONS.append(
                disnake.SelectOption(
                    emoji=icon,
                    label=f"{_ + 1} - {c2.upper()} +{lvs} | {skill_type.lower()} Lv: {lvn}",
                    description=f"Dano: {damage} | Mana: {_mana} | Efeito(s): {effect_skill}",
                    value=str(_ + 1)
                    )
                )

        regen = int((self.tot_mp / 100) * 50)
        pl = 3 if not self.is_wave else 3 + (wave_now // 2)

        self.OPTIONS.append(
            disnake.SelectOption(
                emoji="<:MP:774699585620672534>",
                label=f'{tot + 1} - {"Pass turn MP".upper()}',
                description=f"MP Recovery: +{regen} de Mana",
                value=str(tot + 1)
                )
            )

        self.OPTIONS.append(
            disnake.SelectOption(
                emoji="<:HP:774699585070825503>",
                label=f'{tot + 2} - {"Pass turn hp".upper()}',
                description=f"HP Recovery: 25-35% de HP ({self.potion}/{pl})",
                value=str(tot + 2)
                )
            )

        self.OPTIONS.append(
            disnake.SelectOption(
                emoji="<:fechar:749090949413732352>",
                label=f'{tot + 3} - Finalizar batalha',
                value=str(tot + 3)
                )
            )

        if self.is_combo:
            if self.is_passive and self.data['class_now'] == "necromancer":
                passive_combo_name = CLS[self.data['class_now']]["passive"]['combo_name']
                passive_combo_icon = CLS[self.data['class_now']]["passive"]['combo_icon']
                self.OPTIONS.append(
                    disnake.SelectOption(
                        emoji=passive_combo_icon,
                        label=f'{tot + 4} - [{passive_combo_name}] | COMBO',
                        description=f"Dano: 75% | Mana: 100% | Efeito(s): fraquesa, silencio",
                        value=str(tot + 4)
                    )
                )
            else:
                self.OPTIONS.append(
                    disnake.SelectOption(
                        emoji="<a:combo:834236942295891969>",
                        label=f'{tot + 4} - [Combo] - Half Life | COMBO',
                        description=f"Dano: 50% | Mana: 100% | Efeito(s): Sem Efeito",
                        value=str(tot + 4)
                        )
                    )

        if self.soulshot[0]:
            soulshot = f"\n\n`Soulshot:` **{self.soulshot[1]}**"
            description += soulshot

        if self.passive == "warrior" and self.rage_damage > 0:
            description += f"\n`Rage:` **{self.rage_damage}**"

        if self.passive == "paladin" and self.devotion > 0:
            description += f"\n`Devotion:` **{self.devotion}**"

        embed = disnake.Embed(
            title=title,
            description=description,
            color=0x000000
        )
        view = self.View(user.id)
        select = self.SelectSkill(self.OPTIONS)
        view.add_item(select)
        embed.set_author(name=user.name, icon_url=user.display_avatar)
        return embed, view, attacks, hate_no_mana, hate_no_limit

    async def effects_resolve(self, ctx, effects, msg_return, entity):
        type_effects = ["cegueira", "strike", "reflect", "confusion", "hold", "bluff"]
        if effects is not None:
            ignition = True if "ignition" in self.effects.keys() else False
            for c in effects:
                if c in self.effects.keys():

                    if "type" in self.effects[c].keys():
                        if 'damage' in self.effects[c]['type']:
                            damage, burn, barrier_msg, detached, _red = self.effects[c]['damage'], "", "", False, None

                            if "detached" in self.effects.keys():
                                if self.effects["detached"]["turns"] > 0:
                                    detached = True

                            if "barrier" in self.effects.keys():
                                if self.effects["barrier"]['turns'] > 0:
                                    damage = 0
                                    barrier_msg += f" `por causa do efeito de` **barrier**"

                            if c == "confine" and self.is_confine:
                                self.confine = self.effects
                                self.is_confine = False

                            if c == "devotion" and self.passive == "paladin":
                                self.devotion += damage
                                _red = f"**{self.name.upper()}** `acumulou` **{damage}** `de devoção por causa do " \
                                       f"efeito de` **DEVOTION**"
                                damage = 0

                            if c == "blessing" and entity.passive == "paladin":
                                damage += entity.devotion
                                if entity.confine is not None:
                                    self.effects.update(entity.confine)
                                    entity.confine = None

                            if c in ["queimadura", "fireball"] and randint(1, 2) == 2:
                                bb = int(damage / 100 * randint(50 if not detached else 80, 100))
                                damage += bb
                                burn += f" `levou {bb}% a mais por queimadura profunda`"
                                _chance, percent = randint(1, 100), 15 if not detached else 25
                                if _chance <= percent:
                                    self.effects["curse"] = {"type": "manadrain", "turns": randint(2, 4), "damage": 10}
                                    burn += " `e ganhou o efeito de` **CURSE** `pelo alto dano da queimadura.`"

                            if c == "fireball" and ignition:
                                if "ignition" in self.effects.keys():
                                    if self.effects["ignition"]["turns"] > 0:  # bonus de ignition
                                        damage += damage * randint(3, 6)
                                        if entity.passive == "wizard" and entity.is_passive and randint(1, 100) <= 25:
                                            damage_ice = 50 * entity.stack
                                            self.effects["gelo"] = {"type": "damage", "turns": 2, "damage": damage_ice}
                                            burn += f" `e ganhou o efeito de` **GELO** `pela combinação do efeito` " \
                                                    f"**IGNITION** `com o modo` **SPELLCASTER FIRER** `de` " \
                                                    f"**{entity.name.upper()}**"

                            if c == "veneno" and randint(1, 2) == 2:
                                bb = int(damage / 100 * randint(50 if not detached else 80, 100))
                                damage += bb
                                burn += f" `levou {bb}% a mais por intoxicação aguda`"
                                _chance, percent = randint(1, 100), 15 if not detached else 50
                                if _chance <= percent:
                                    eff = {"type": "normal", "turns": randint(2, 4), "damage": None}
                                    self.effects["silencio"] = eff
                                    burn += " `e ganhou o efeito de` **SILENCIO** `pelo alto dano da intoxicação.`"

                            if c == "judgment":
                                etp1, etp2 = False, False

                                if "veneno" in self.effects.keys():
                                    if self.effects["veneno"]["turns"] > 0:
                                        etp1 = True

                                if "queimadura" in self.effects.keys():
                                    if self.effects["queimadura"]["turns"] > 0:
                                        etp2 = True

                                if etp1:
                                    damage += damage * 5

                                if etp2:
                                    damage += damage * 5

                            if c == "devotion" and self.passive != "paladin" and randint(1, 100) <= 25:
                                devotion = {
                                    "queimadura": {"type": "damage", "turns": randint(2, 7), "damage": 50},
                                    "veneno": {"type": "damage", "turns": randint(2, 7), "damage": 50},
                                    "gelo": {"type": "damage", "turns": 2, "damage": 50},
                                    "curse": {"type": "manadrain", "turns": randint(2, 4), "damage": 10}
                                }
                                key = choice(list(devotion.keys()))
                                self.effects[key] = devotion[key]
                                msg_return += f" `e ganhou o efeito de` **{key}** `pela alta devoção do seu inimigo.`"

                            self.status['hp'] -= damage
                            if self.status['hp'] < 0:
                                self.status['hp'] = 0

                            # novo sistema de reflect
                            if "reflect" in self.effects.keys() and c == "reflect":
                                if self.effects['reflect']['damage'] > 0:
                                    if self.effects['reflect']['damage'] > 0:
                                        self.effects['reflect']['damage'] = 0  # reseta o dano do reflect
                                    self.effects["reflect"]['turns'] -= 1
                                if self.effects["reflect"]['turns'] < 1:
                                    del self.effects["reflect"]
                                    reflect = f"❌ **{self.name.upper()}** `perdeu o efeito de` **reflect!**"
                                    msg_return += f"{reflect}\n\n"

                            if damage > 0:
                                _text5 = f"**{self.name.upper()}** `sofreu` **{damage}** `de dano " \
                                         f"por efeito de` **{c.upper()}!**{burn}"
                                msg_return += f"{_text5}\n\n"
                            else:
                                if c not in ["reflect"]:
                                    emoji = "<a:alert:919041626486218783>"
                                    _text5 = f"{emoji} **{self.name.upper()}** `evadiu ao dano de` **{c.upper()}!**"
                                    if _red is not None:
                                        _text5 = _red + barrier_msg
                                    else:
                                        _text5 += barrier_msg
                                    msg_return += f"{_text5}\n\n"

                        elif 'manadrain' in self.effects[c]['type']:

                            presas_active = False
                            if "presas" in self.effects.keys():
                                if self.effects["presas"]["turns"] >= 1:
                                    presas_active = True

                            if not presas_active:
                                damage = 0

                                if not self.is_player:
                                    damage += self.effects[c]['damage'] * 10  # se nao for player o dano é no hp
                                    self.status['hp'] -= damage
                                    if self.status['hp'] < 0:
                                        self.status['hp'] = 0

                                else:
                                    damage += int((self.tot_mp / 100) * self.effects[c]['damage'])
                                    self.status['mp'] -= damage
                                    if self.status['mp'] < 0:
                                        self.status['mp'] = 0

                                if damage > 0:
                                    _type = "mana" if self.is_player else "hp"
                                    _text6 = f"**{self.name.upper()}** `teve` **{damage}** `de {_type} " \
                                             f"drenada por efeito de` **{c.upper()}!**"
                                    msg_return += f"{_text6}\n\n"

                            else:
                                _text6 = f"**{self.name.upper()}** `não teve a mana removida " \
                                         f"pois seu oponente esta sob o efeito de` **presas**"
                                msg_return += f"{_text6}\n\n"

                        elif self.effects[c]['turns'] > 0 and c in type_effects:
                            _text7 = f"**{self.name.upper()}** `esta sobe o efeito de` **{c.upper()}!**"
                            msg_return += f"{_text7}\n\n"

                    elif self.effects[c]['turns'] > 0 and c in type_effects:
                        _text7 = f"**{self.name.upper()}** `esta sobe o efeito de` **{c.upper()}!**"
                        msg_return += f"{_text7}\n\n"

                    if c not in ["duelist", "reflect"]:  # efeitos eternos

                        if self.effects[c]['turns'] > 0:
                            self.effects[c]['turns'] -= 1

                        if self.effects[c]['turns'] < 1:
                            del self.effects[c]

                            if "self" in c:
                                c = "PASSIVA"

                            and_effect = f"❌ **{self.name.upper()}** `perdeu o efeito de` **{c.upper()}!**"
                            msg_return += f"{and_effect}\n\n"

                            if c.lower() == "smoke" and entity.smoke_now:
                                entity.smoke_now = False
                                entity.status["agi"] -= 60

                            if c == "confine" and not self.is_confine:
                                self.is_confine = True

        if self.passive == "paladin":
            if self.confine is not None:
                self.effects = None

        if not self.is_pvp and self.data["salvation"] and self.status['hp'] <= 0:
            self.data["salvation"] = False
            self.status['hp'] = self.tot_hp
            self.status['mp'] = self.tot_mp
            self.potion = 0
            self.limit = [0, 0, 0, 0, 0]
            await ctx.send(f'**{self.name.upper()}** `por esta equipado com` **SALVATION** `na hora da sua morte'
                           f' reviveu!`')

        return effects, msg_return

    def self_effect_resolve(self, msg_return, entity):
        if self.skill is not None and self.skill not in ["PASS-TURN-MP", "PASS-TURN-HP", "SKILL-COMBO"]:
            if self.skill['effs'] is not None:
                if self.is_player:
                    lvs = self.level_skill[self.skill['skill'] - 1]
                    self.ls = lvs if 0 <= lvs <= 9 else 9
                    _skill = self.skill['effs'][self.ls]
                else:
                    _skill = self.skill['effs']

                if "cura" in _skill.keys():

                    presas_active = False
                    if "presas" in self.effects.keys():
                        if self.effects["presas"]["turns"] >= 1:
                            presas_active = True

                    if not presas_active:
                        percent = _skill['cura']['damage']
                        regen = int((self.tot_hp / 100) * percent)
                        if (self.status['hp'] + regen) <= self.tot_hp:
                            self.status['hp'] += regen
                        else:
                            self.status['hp'] = self.tot_hp
                        _text3 = f'**{self.name.upper()}** `recuperou` **{regen}** `de HP`'
                        msg_return += f"{_text3}\n\n"
                        self.skill = None
                    else:
                        _text3 = f'**{self.name.upper()}** `não recuperou HP pois está sob o ' \
                                 f'efeito de` **presas**'
                        msg_return += f"{_text3}\n\n"
                        self.skill = None

                if "devotion" in _skill.keys():
                    min_turn, max_turn = 2, _skill["devotion"]['turns']
                    max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                    self.effects["devotion"] = _skill["devotion"]
                    self.effects["devotion"]['turns'] = randint(min_turn, max_turn)

                    _text3 = f'**{self.name.upper()}** `ativou o efeito` **devotion** `por` ' \
                             f'**{self.effects["devotion"]["turns"]}** `turnos.`'
                    msg_return += f"{_text3}\n\n"

                if "barrier" in _skill.keys() and self.passive == "paladin":
                    self.effects["barrier"] = _skill["barrier"]
                    min_turn, max_turn = 2, _skill["barrier"]['turns']
                    max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                    self.effects["barrier"]['turns'] = randint(min_turn, max_turn)

                    text_duelist = ""
                    if "duelist" in entity.effects.keys():
                        del entity.effects["duelist"]
                        text_duelist += f"`e por causa disso` **{entity.name.upper()}** `perdeu o efeito de` " \
                                        f"**duelist**"

                    _text3 = f'**{self.name.upper()}** `ativou o efeito` **barrier** `por` ' \
                             f'**{self.effects["barrier"]["turns"]}** `turnos.` {text_duelist}'
                    msg_return += f"{_text3}\n\n"

                if "conjure" in _skill.keys():
                    min_turn, max_turn, chance = 2, _skill["conjure"]['turns'], randint(1, 100)
                    max_turn = min_turn + 1 if min_turn > max_turn else max_turn

                    if chance <= 25:

                        self.effects["conjure"] = _skill["conjure"]
                        self.effects["conjure"]['turns'] = randint(min_turn, max_turn)

                        _text3 = f'**{self.name.upper()}** `ativou o efeito` **conjure** `por` ' \
                                 f'**{self.effects["conjure"]["turns"]}** `turnos.`'
                        msg_return += f"{_text3}\n\n"

                    else:

                        _text3 = f'**{self.name.upper()}** `NÃO ATIVOU o efeito` **conjure** `nesse turno`'
                        msg_return += f"{_text3}\n\n"

                if "concentration" in _skill.keys():
                    min_turn, max_turn = 2, _skill["concentration"]['turns']
                    max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                    self.effects["concentration"] = _skill["concentration"]
                    self.effects["concentration"]['turns'] = randint(min_turn, max_turn)

                    _text3 = f'**{self.name.upper()}** `ativou o efeito` **concentration** `por` ' \
                             f'**{self.effects["concentration"]["turns"]}** `turnos.`'
                    msg_return += f"{_text3}\n\n"

        return msg_return, entity

    def self_passive_effect_resolve(self, msg_return, entity):
        if self.skill is not None and self.skill not in ["PASS-TURN-MP", "PASS-TURN-HP", "SKILL-COMBO"]:
            if self.skill['effs'] is not None:
                if self.is_player and not self.is_passive and self.level > 25:
                    active_passive = True

                    if "self_passive" in self.effects.keys():
                        if self.effects["self_passive"]["turns"] >= 1:
                            active_passive = False  # nao ativa a passiva com ela ja ativa!

                    if active_passive:
                        lvs = self.level_skill[self.skill['skill'] - 1]
                        self.ls = lvs if 0 <= lvs <= 9 else 9

                        # habilita passiva do necromancer
                        if "drain" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"

                        # habilita passiva do priest
                        if "hold" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"

                        # habilita passiva do warlock
                        if "skull" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"

                        # habilita passiva do assassin
                        if "presas" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"

                        # habilita passiva do wizard
                        if "ignition" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"

                        # habilita passiva do paladin
                        if "devotion" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"

                        # habilita passiva do warrior (modo atk)
                        if "duelist" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva` **IRON FISTS** `por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"
                            self.passive_mode = 0

                        # habilita passiva do warrior (modo def)
                        if "barrier" in self.skill['effs'][self.ls].keys():
                            self.effects["self_passive"] = {"type": "normal", "turns": randint(1, 3), "damage": 0}
                            _text3 = f'**{self.name.upper()}** `habilitou a passiva` **TITAN WALL** `por` ' \
                                     f'**{self.effects["self_passive"]["turns"]}** `turno(s)`'
                            msg_return += f"{_text3}\n\n"
                            self.passive_mode = 1

        return msg_return, entity

    async def turn(self, ctx, user, entity, wave_now=0):
        msg_return, stun, ice, self.skill = "", False, False, None,
        skills, effects = list(self.skills.keys()), [eff.lower() for eff in self.effects.keys()]
        skills_verify, skills_now = [sk for sk in skills], self.skills

        if self.is_passive and self.passive == "necromancer":
            skills = list(self.skills_p.keys())  # altera as skills do necro
            skills_verify, skills_now = [sk for sk in skills], self.skills_p

        if "ignition" in entity.effects.keys():
            if entity.effects["ignition"]["turns"] > 0 and self.passive == "wizard":
                skills = list(self.skills_p.keys())  # altera a skill 5 do wizardp
                skills_verify, skills_now = [sk for sk in skills], self.skills_p

        if self.is_player:
            verify = await self.verify_equips(ctx)
            if verify is not None:
                return verify

        if effects is not None:
            if 'stun' in effects:
                if self.effects['stun']['turns'] > 0:
                    stun = True

            if 'gelo' in effects:
                if self.effects['gelo']['turns'] > 0:
                    ice = True

        presas_active = False
        if "presas" in self.effects.keys():
            if self.effects["presas"]["turns"] >= 1:
                presas_active = True

        # retirada as skills fisicas
        if "fraquesa" in effects:
            if self.effects["fraquesa"]['turns'] > 0:
                for sk in skills_verify:
                    try:
                        if skills_now[sk]['type'] == "fisico":
                            skills.remove(sk)
                    except KeyError:
                        pass

        # retirada as skills magicas
        if "silencio" in effects:
            if self.effects["silencio"]['turns'] > 0:
                for sk in skills_verify:
                    try:
                        if skills_now[sk]['type'] == "magico":
                            skills.remove(sk)
                    except KeyError:
                        pass

        if stun is False and ice is False:
            if self.is_player:

                # verificação da skill passiva das classes
                self_passive = False
                if effects is not None:
                    if 'self_passive' in effects:
                        if self.effects['self_passive']['turns'] > 0:
                            self_passive = True

                res = self.get_skill_menu(entity, user, skills, wave_now, self_passive, skills_now)
                embed, view, attacks, hate_no_mana, hate_no_limit = res[0], res[1], res[2], res[3], res[4]
                _OPTIONS_LAST = self.OPTIONS.copy()
                await ctx.send(embed=embed, view=view)

                while not ctx.bot.is_closed():
                    def check(m):
                        if m.user.id == user.id and m.channel.id == ctx.channel.id:
                            return True
                        return False

                    try:
                        answer = await ctx.bot.wait_for('interaction', check=check, timeout=120.0)
                    except TimeoutError:
                        if self.is_wave and wave_now > 1:
                            return "BATALHA-CANCELADA"
                        else:
                            return "COMANDO-CANCELADO"

                    # Apagar itens da lista
                    self.OPTIONS.clear()

                    # proteção contra interação vazia
                    if answer.values is None:
                        view, select = disnake.ui.View(), self.SelectSkill(_OPTIONS_LAST)
                        view.add_item(select)
                        await ctx.send(embed=embed, view=view)
                        continue
                    
                    # verificador de limit de skill
                    skill_now, limit_now = int(answer.values[0]), False
                    if skill_now in [n + 1 for n in range(len(skills))]:
                        skill_now_main = skills_now[attacks[skill_now]]["skill"]
                        ls = self.data["skill_level"][skill_now_main - 1][0]  # verificando o lvl atual da skill

                        if self.limit[skill_now_main - 1] < skills_now[attacks[skill_now]]['limit'][ls]:
                            ls = self.data["skill_level"][skill_now_main - 1][0]
                            remove = skills_now[attacks[skill_now]]['mana'][ls]
                            if self.status['mp'] >= remove:
                                self.limit[skill_now_main - 1] += 1
                        else:
                            limit_now = True

                    if int(answer.values[0]) == len(skills) + 1:

                        if not presas_active:
                            # regeneração de MP
                            regen = int((self.tot_mp / 100) * 50)
                            if (self.status['mp'] + regen) <= self.tot_mp:
                                self.status['mp'] += regen
                            else:
                                self.status['mp'] = self.tot_mp

                            self.skill = "PASS-TURN-MP"
                            break

                        else:
                            description = f"**{user.name.upper()}** `VOCÊ NAO PODE USAR POÇÕES, POIS ESTA SOB O " \
                                          f"EFEITO DE` **PRESAS**"
                            embedd = disnake.Embed(description=description, color=0x000000)
                            embedd.set_author(name=user.name, icon_url=user.display_avatar)
                            await ctx.send(embed=embedd)

                            view, select = disnake.ui.View(), self.SelectSkill(_OPTIONS_LAST)
                            view.add_item(select)
                            await ctx.send(embed=embed, view=view)

                            continue

                    potion_limit = 3 if not self.is_wave else 3 + (wave_now // 2)
                    if int(answer.values[0]) == len(skills) + 2 and self.potion < potion_limit:

                        if not presas_active:

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

                        else:
                            description = f"**{user.name.upper()}** `VOCÊ NAO PODE USAR POÇÕES, POIS ESTA SOB O " \
                                          f"EFEITO DE` **PRESAS**"
                            embedd = disnake.Embed(description=description, color=0x000000)
                            embedd.set_author(name=user.name, icon_url=user.display_avatar)
                            await ctx.send(embed=embedd)

                            view, select = disnake.ui.View(), self.SelectSkill(_OPTIONS_LAST)
                            view.add_item(select)
                            await ctx.send(embed=embed, view=view)

                            continue

                    if int(answer.values[0]) == len(skills) + 3:
                        # cancela ou foge da batalha
                        return "BATALHA-CANCELADA"

                    if int(answer.values[0]) == len(skills) + 4 and self.is_combo:
                        self.skill = "SKILL-COMBO"
                        self.is_combo = False
                        self.status['mp'] = 0
                        self.combo_cont = 0
                        if self.is_passive and self.passive == "necromancer":
                            self.is_combo_passive = True
                        break

                    if int(answer.values[0]) == 0:

                        # verificador se esta sendo feito o combo
                        if self.combo_cont >= 3:
                            self.is_combo = False
                            self.combo_cont = 0

                        self.verify_combo(0)

                        self.skill = CLS[self._class]['base_skill']
                        not_is_now = False  # nao deixa desativar a skill no turno em ativou a passiva

                        # ----------------------------------------------------------------------------------
                        if self.is_passive and self.passive == "paladin":
                            self.skill = CLS[self._class]['passive']["0"]

                        if self_passive and self.passive == "paladin":
                            _action = randint(15, 25)  # velocidade da progreção
                            self.progress += _action
                            if self.progress >= 100 and not self.is_passive:
                                self.progress = 100

                            if not self.is_passive:
                                especial = False
                                if self.progress < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ ELEVOU SUA DEVOÇÃO` **{_action}x**"
                                else:
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **RESPLENDENT!**"
                                    self.is_passive, especial, not_is_now = True, True, True
                                    if "self_passive" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_passive"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    _url = "https://c.tenor.com/Nx0mPkS00KcAAAAM/algoz.gif"
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "warrior":
                            self.skill = CLS[self._class]['passive'][f"{self.passive_mode}"]

                        if self_passive and self.passive == "warrior":
                            _action = randint(15, 25)  # velocidade da progreção

                            if "impulse" in entity.effects.keys():
                                if entity.effects["impulse"]["turns"] > 0:
                                    _action = randint(40, 80)  # bonus de impulse

                            self.passive_progress[self.passive_mode] += _action
                            if self.passive_progress[self.passive_mode] >= 100 and not self.is_passive:
                                self.passive_progress[self.passive_mode] = 100

                            if not self.is_passive:
                                especial = False
                                if self.passive_progress[self.passive_mode] < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ AUMENTOU SUA FURIA` **{_action}x**"
                                else:
                                    _MODE = "IRON FISTS" if self.passive_mode == 0 else "TITAN WALL"
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **{_MODE}**"
                                    self.is_passive, especial, not_is_now = True, True, True
                                    if "self_passive" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_passive"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    _url = CLS[self._class]['passive']["gif"]
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "assassin":
                            self.skill = CLS[self._class]['passive']["0"]

                        if self_passive and self.passive == "assassin":
                            _action = randint(25, 35)  # velocidade da progreção
                            self.progress += _action
                            if self.progress >= 100 and not self.is_passive:
                                self.progress = 100

                            if not self.is_passive:
                                especial = False
                                if self.progress < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ FINCOU SUAS GARRAS` **{_action}x**"
                                else:
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **CLAWS STUCK!**"
                                    self.is_passive, especial, not_is_now = True, True, True
                                    if "self_passive" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_passive"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    _url = CLS[self._class]['passive']["gif"]
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "wizard":
                            self.skill = CLS[self._class]['passive'][f"{self.stack}"]

                        if self_passive and self.passive == "wizard":
                            _action = randint(20, 30)  # velocidade da progreção
                            self.progress += _action
                            if self.progress >= 100 and not self.is_passive:
                                self.progress = 100

                            if not self.is_passive:
                                especial = False
                                if self.progress < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ STACOU` **{_action}** `DA SUA MAGIA!`"
                                else:
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **SPELLCASTER FIRER!**"
                                    self.is_passive, especial, not_is_now = True, True, True
                                    if "self_passive" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_passive"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    self.is_ignition = False
                                    _url = "https://c.tenor.com/ibnv8p1He_QAAAAM/crazywiz-crazywizzz.gif"
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "warlock":
                            self.skill = CLS[self._class]['passive'][f"{self.stack}"]

                        if self_passive and self.passive == "warlock":
                            _action = randint(20, 30)  # velocidade da progreção
                            self.progress += _action
                            if self.progress >= 100 and not self.is_passive:
                                self.progress = 100

                            if not self.is_passive:
                                especial = False
                                if self.progress < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ STACOU` **{_action}** `DA SUA LANÇA!`"
                                else:
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **SPEAR OF DESTINY!**"
                                    self.is_passive, especial, not_is_now = True, True, True
                                    if "self_passive" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_passive"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    _url = CLS[self._class]['passive']["gif"]
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "priest":
                            self.skill = CLS[self._class]['passive'][f"{self.type_skill_passive}"]

                        if self_passive and self.passive == "priest":
                            _action = randint(25, 35)  # velocidade da progreção
                            self.progress += _action
                            if self.progress >= 100 and not self.is_passive:
                                self.progress = 100

                            if not self.is_passive:
                                especial = False
                                if self.progress < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ SUBIU` **{_action}** `DA SUA FORÇA!`"
                                else:
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **DEMON HUNTER!**"
                                    self.is_passive, especial = True, True
                                    if "self_passive" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_passive"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    _url = "https://i.gifer.com/DRps.gif"
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "necromancer":
                            self.skill = CLS[self._class]['passive']["0"]

                        if self_passive and self.passive == "necromancer":
                            _action = randint(20, 30)  # velocidade da progreção
                            self.progress += _action
                            if self.progress >= 100 and not self.is_passive:
                                self.progress = 100

                            if not self.is_passive and self.passive == "necromancer":
                                especial = False
                                if self.progress < 100:
                                    description = f"**{user.name.upper()}** `VOCÊ ABSORVEU` **{_action}** `ALMAS!`"
                                else:
                                    description = f"**{user.name.upper()}** `VOCÊ ATIVOU O MODO` **SENHOR DA MORTE!**"
                                    self.is_passive, especial = True, True
                                    if "self_drain" in self.effects.keys():  # desabilita a passiva da skill 0
                                        del self.effects["self_drain"]
                                embeds = disnake.Embed(description=description, color=0x000000)
                                embeds.set_author(name=user.name, icon_url=user.display_avatar)
                                if self.is_passive and especial:
                                    _url = "https://c.tenor.com/77pxCbsNbKIAAAAC/necromancer-diablo-iii.gif"
                                    embeds.set_image(url=_url)
                                await ctx.send(embed=embeds)

                        # ----------------------------------------------------------------------------------

                        if self.is_passive and self.passive == "warrior" and not not_is_now:
                            self.is_passive, self.passive_progress[self.passive_mode] = False, 0
                            if self.passive_mode == 0:
                                self.IRON_FISTS = True
                            else:
                                self.TITAN_WALL = True
                            _MODE = "IRON FISTS" if self.passive_mode == 0 else "TITAN WALL"
                            description = f"**{user.name.upper()}** `VOCÊ USOU O MODO` **{_MODE}!**"
                            embeds = disnake.Embed(description=description, color=0x000000)
                            embeds.set_author(name=user.name, icon_url=user.display_avatar)
                            await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "assassin" and not not_is_now:
                            self.is_passive, self.progress = False, 0
                            self.CLAWS_STUCK = True
                            description = f"**{user.name.upper()}** `VOCÊ USOU O MODO` **CLAWS STUCK!**"
                            embeds = disnake.Embed(description=description, color=0x000000)
                            embeds.set_author(name=user.name, icon_url=user.display_avatar)
                            await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "warlock" and not not_is_now:
                            self.is_passive, self.progress, self.stack = False, 0, 1
                            self.SPEAR_OF_DESTINY = True
                            description = f"**{user.name.upper()}** `VOCÊ USOU O MODO` **SPEAR OF DESTINY!**"
                            embeds = disnake.Embed(description=description, color=0x000000)
                            embeds.set_author(name=user.name, icon_url=user.display_avatar)
                            await ctx.send(embed=embeds)

                        if self.is_passive and self.passive == "wizard" and not not_is_now:
                            self.is_passive, self.progress, self.stack = False, 0, 1
                            self.SPELLCASTER_FIRER = True
                            description = f"**{user.name.upper()}** `VOCÊ USOU O MODO` **SPELLCASTER FIRER!**"
                            embeds = disnake.Embed(description=description, color=0x000000)
                            embeds.set_author(name=user.name, icon_url=user.display_avatar)
                            await ctx.send(embed=embeds)

                        break

                    potion_msg = False
                    for c in attacks.keys():
                        if int(c) == int(answer.values[0]) or len(skills) + 2 == int(answer.values[0]):
                            if int(c) == int(answer.values[0]):

                                concentration, conjure = False, False

                                if "conjure" in self.effects.keys():
                                    if self.effects["conjure"]['turns'] > 0:
                                        conjure = True

                                if "concentration" in self.effects.keys():
                                    if self.effects["concentration"]['turns'] > 0:
                                        concentration = True

                                ls = self.data["skill_level"][skills_now[attacks[c]]['skill'] - 1][0]
                                remove = skills_now[attacks[c]]['mana'][ls]

                                if concentration or conjure:
                                    remove = remove // 2

                                try:
                                    skill_effs = [k for k, v in skills_now[attacks[c]]['effs'][self.ls].items()]
                                except TypeError:
                                    skill_effs = ['nenhum']

                                heal = False
                                for eff in skill_effs:
                                    if eff == "cura":
                                        heal = True

                                if heal:
                                    remove = int(self.tot_mp / 100 * 35)

                                if skills_now[attacks[c]]['type'] == "especial":
                                    remove = int(self.tot_mp / 100 * 50)

                                    if concentration or conjure:
                                        remove = remove // 2

                            else:
                                remove = self.tot_mp * 2  # limitador para uso de habilidade sem mana

                            potion_limit = 3 if not self.is_wave else 3 + (wave_now // 2)
                            if self.potion >= potion_limit and len(skills) + 2 == int(answer.values[0]):

                                if self.is_wave:
                                    msg = f"`MATE OUTRO MONSTRO PARA AUMENTAR O SEU LIMITE, ESCOLHA UMA SKILL OU " \
                                          f"PASSE A VEZ...`\n**Obs:** Passar a vez regenera a mana ou vida!"
                                else:
                                    msg = f"`ENTÃO ESCOLHA UMA SKILL OU PASSE A VEZ...`\n" \
                                          f"**Obs:** Passar a vez regenera a mana ou vida!"

                                description = f"**{user.name.upper()}** `VOCÊ JA ATINGIU O LIMITE DE POÇÃO DE VIDA!`" \
                                              f"\n{msg}"
                                embedhp = disnake.Embed(description=description, color=0x000000)
                                embedhp.set_author(name=user.name, icon_url=user.display_avatar)

                                if not potion_msg:
                                    await ctx.send(embed=embedhp)
                                    view, select = disnake.ui.View(), self.SelectSkill(_OPTIONS_LAST)
                                    view.add_item(select)
                                    await ctx.send(embed=embed, view=view)
                                    potion_msg = True
                                    hate_no_mana += 1
                                    if hate_no_mana > 5:
                                        await ctx.send(f"`Ficar repetindo esse tipo de msg no mesmo turno é "
                                                       f"considerado pratica` **ANTI-JOGO** `por isso a batalha foi"
                                                       f" cancelada e voce perdeu:` **{user.name.upper()}**")

                                        return "BATALHA-CANCELADA"

                            elif limit_now:
                                embedh = disnake.Embed(
                                    description=f"**{user.name.upper()}** `VOCÊ ATINGIU O LIMITE DESSA HABILDIADE!`\n"
                                                f"`ENTÃO ESCOLHA OUTRA SKILL OU PASSE A VEZ...`\n"
                                                f"**Obs:** Passar a vez regenera a mana ou vida!",
                                    color=0x000000
                                )
                                embedh.set_author(name=user.name, icon_url=user.display_avatar)
                                await ctx.send(embed=embedh)
                                view, select = disnake.ui.View(), self.SelectSkill(_OPTIONS_LAST)
                                view.add_item(select)
                                await ctx.send(embed=embed, view=view)
                                hate_no_limit += 1
                                if hate_no_limit > 5:
                                    await ctx.send(f"`Ficar repetindo esse tipo de msg no mesmo turno é "
                                                   f"considerado pratica` **ANTI-JOGO** `por isso a batalha foi"
                                                   f" cancelada e voce perdeu:` **{user.name.upper()}**")
                                    return "BATALHA-CANCELADA"

                            elif self.status['mp'] >= remove:
                                self.status['mp'] -= remove
                                self.skill = attacks[c]

                                if self.is_passive and self.passive == "warlock":
                                    if self.skill == "Tudo do Po":  # verificação da skill de (skull)
                                        if self.stack < 4:
                                            self.stack += 1
                                            await ctx.send(f"**{user.name.upper()}** `(SOD MODE) STACADO COM SUCESSO!`")

                                if self.is_passive and self.passive == "wizard":
                                    if self.skill == "Comando Criptico":  # verificação da skill de (looping)
                                        if self.stack < 4:
                                            self.stack += 1
                                            await ctx.send(f"**{user.name.upper()}** `(SF MODE) STACADO COM SUCESSO!`")

                                # troca da passiva do priest
                                if self.is_passive and self.passive == "priest":
                                    if self.skill == "Devocional":  # verificação da skill de (hold)
                                        skill_await = self.type_skill_passive
                                        self.type_skill_passive = self.type_skill_await
                                        self.type_skill_await = skill_await
                                        await ctx.send(f"**{user.name.upper()}** `(DH MODE) ALTERADO COM SUCESSO!`")

                                # verificador se esta sendo feito o combo
                                if self.combo_cont >= 3:
                                    self.is_combo = False
                                    self.combo_cont = 0

                                self.verify_combo(int(skills_now[self.skill]["skill"]))

                                # sistema de level up das skills
                                if skill_now in [n + 1 for n in range(len(skills))]:
                                    _skill_number = skills_now[self.skill]["skill"] - 1
                                    _skill_name = skills_now[self.skill]["name"]
                                    self.data["skill_level"][_skill_number][1] += 1
                                    if self.data["skill_level"][_skill_number][1] >= 100:
                                        self.data["skill_level"][_skill_number][1] = 0
                                        if self.data["skill_level"][_skill_number][0] < 9:
                                            self.data["skill_level"][_skill_number][0] += 1
                                            await ctx.send(f"**{user.name.upper()}** `Voce acabou de` **UPAR** "
                                                           f"`a skill` **{_skill_name.upper()}** `para o level` "
                                                           f"**{self.data['skill_level'][_skill_number][0] + 1}**")
                                break

                            else:
                                embedm = disnake.Embed(
                                    description=f"**{user.name.upper()}** `VOCÊ NÃO TEM MANA O SUFICIENTE!`\n"
                                                f"`ENTÃO ESCOLHA OUTRA SKILL OU PASSE A VEZ...`\n"
                                                f"**Obs:** Passar a vez regenera a mana ou vida!",
                                    color=0x000000
                                )
                                embedm.set_author(name=user.name, icon_url=user.display_avatar)
                                await ctx.send(embed=embedm)
                                view, select = disnake.ui.View(), self.SelectSkill(_OPTIONS_LAST)
                                view.add_item(select)
                                await ctx.send(embed=embed, view=view)
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
                        if not self.ultimate and self.is_boss or not self.ultimate and self.is_mini_boss:
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
                if not isinstance(self.skill, dict):
                    self.skill = skills_now[self.skill]

        else:
            _text2 = f'**{self.name.upper()}** `esta` **{"STUNADO" if stun else "CONGELADO"}**'
            msg_return += f"{_text2}\n\n"

        msg_return, entity = self.self_effect_resolve(msg_return, entity)

        if not self.is_passive:
            msg_return, entity = self.self_passive_effect_resolve(msg_return, entity)

        effects, msg_return = await self.effects_resolve(ctx, effects, msg_return, entity)
        hp_max, monster, img_ = self.tot_hp, not self.is_player, None
        embed_ = embed_creator(msg_return, img_, monster, hp_max, self.status['hp'], self.img, self.name)

        if msg_return != "":
            await ctx.send(embed=embed_)

        return self.skill

    def verify_effect(self):
        looping, ignition, drain, bluff, hit_kill, hold = False, False, False, False, False, False
        duelist, stk1, stk2, lethal, ds = False, False, False, False, False
        if self.effects is not None:
            if "dualshot" in self.effects.keys():
                if self.effects["dualshot"]['turns'] > 0:
                    ds = True
            if "target" in self.effects.keys():
                if self.effects["target"]['turns'] > 0:
                    stk1 = True
            if "headshot" in self.effects.keys():
                if self.effects["headshot"]['turns'] > 0:
                    stk2 = True
            if "duelist" in self.effects.keys():
                if self.effects["duelist"]["turns"] > 0:
                    duelist = True
            if "looping" in self.effects.keys():
                if self.effects["looping"]["turns"] > 0:
                    looping = True
            if "ignition" in self.effects.keys():
                if self.effects["ignition"]["turns"] > 0:
                    ignition = True
            if "drain" in self.effects.keys():
                if self.effects["drain"]["turns"] > 0:
                    drain = True
            if "bluff" in self.effects.keys():
                if self.effects["bluff"]["turns"] > 0:
                    bluff = True
            if "hold" in self.effects.keys():
                if self.effects["hold"]["turns"] > 0:
                    hold = True
            if "lethal" in self.effects.keys():
                if self.effects["lethal"]["turns"] > 0:
                    lethal = True
                    if "bluff" in self.effects.keys() and "cegueira" in self.effects.keys():
                        if self.effects["bluff"]["turns"] > 0 and self.effects["cegueira"]["turns"] > 0:
                            hit_kill = True
        return looping, ignition, drain, bluff, hit_kill, hold, duelist, stk1, stk2, lethal, ds

    def chance_effect_skill(self, entity, skill, msg_return, test, act_eff, bluff, confusion, lvs, _eff, chance):

        if entity.passive == "warlock":
            if entity.SPEAR_OF_DESTINY and skill["skill"] == 0:
                if skill["name"] == "SoD Stack [4]":
                    # se o stack da passiva do warlock for 4 (o efeito sobrepoe o strike)
                    act_eff = True

        if entity.passive == "wizard":
            if entity.SPELLCASTER_FIRER and skill["skill"] == 0:
                if skill["name"] == "SF Stack [4]":
                    # se o stack da passiva do wizard for 4 (o efeito sobrepoe o strike)
                    act_eff = True

        luck_skill, eff_now = 0, 0
        if entity.passive == "priest" and skill["skill"] == 0 and entity.is_passive:
            luck_skill = choice([0, 1])

        if skill['effs'] is not None and act_eff:

            key = [k for k in skill['effs'][self.ls].keys()] if test else [k for k in skill['effs'].keys()]
            for c in key:

                if c in ["barrier", "conjure", "concentration"]:  # skills self nao pegam no inimigo
                    continue

                _percent = (1, 100) if not bluff else (25, 100)  # aumenta 25% de chance de pegar efeito de skill
                chance_effect, rate_chance = randint(_percent[0], _percent[1]) + lvs, 96.0
                rate_chance -= entity.status['luk'] * 0.5 if entity.status['luk'] > 0 else 0

                chance = True if chance_effect > rate_chance else False

                # detached sempre vai funcionar
                if c == "detached":
                    chance = True

                # sistema de detached
                if c == "veneno" and "detached" in self.effects.keys():
                    if self.effects["detached"]["turns"] > 0:
                        chance = True

                target = False
                # sistema de target
                if "target" in self.effects.keys():
                    if self.effects["target"]["turns"] > 0:
                        target = True

                # sistema de mirror
                mirror_now = False
                if c == "mirror" and "mirror" in self.effects.keys():
                    if self.effects["mirror"]["turns"] > 0:
                        chance, mirror_now = True, True

                # o primeiro rage sempre vai funcionar
                if c == "rage" and not entity.is_rage:
                    entity.is_rage, chance = True, True

                # o primeiro bluff sempre vai funcionar (ou bluff fica 100% ou cegueira)
                if c == "bluff" and not entity.is_bluff and not entity.is_cegueira:
                    entity.is_bluff, entity.is_cegueira, chance = True, True, True

                # o primeiro cegueira sempre vai funcionar (ou bluff fica 100% ou cegueira)
                if c == "cegueira" and not entity.is_cegueira and not entity.is_bluff:
                    entity.is_cegueira, entity.is_bluff, chance = True, True, True

                # o primeiro target sempre vai funcionar
                if c == "target" and not entity.is_target:
                    entity.is_target, chance = True, True

                # se o inimigo estiver com target headshot sempre vai funcionar
                if c == "headshot" and target:
                    chance = True

                # o primeiro charge sempre vai funcionar
                if c == "charge" and not entity.is_charge:
                    entity.is_charge, chance = True, True

                # o primeiro duelist sempre vai funcionar
                if c == "duelist" and not entity.is_duelist:
                    entity.is_duelist, chance = True, True

                # o primeiro strike sempre vai funcionar
                if c == "strike" and not entity.is_strike:
                    entity.is_strike, chance = True, True

                # o primeiro ignition sempre vai funcionar
                if c == "ignition" and not entity.is_ignition:
                    entity.is_ignition, chance = True, True

                # o primeiro hold sempre vai funcionar
                if c == "hold" and not entity.is_hold:
                    entity.is_hold, chance = True, True

                # o primeiro bluff sempre vai funcionar
                if c == "bluff" and not entity.is_bluff:
                    entity.is_bluff, chance = True, True

                # sistema de ignition
                if c == "fireball" and "ignition" in self.effects.keys():
                    if self.effects["ignition"]["turns"] > 0:
                        chance = True

                if entity.passive == "warlock":
                    if entity.SPEAR_OF_DESTINY and skill["skill"] == 0:
                        chance = True

                if entity.passive == "wizard":
                    if entity.SPELLCASTER_FIRER and skill["skill"] == 0:
                        chance = True

                if entity.passive == "assassin":
                    if entity.CLAWS_STUCK and skill["skill"] == 0:
                        chance = True

                if entity.passive == "warrior":
                    if entity.IRON_FISTS and skill["skill"] == 0:
                        chance = True

                    if entity.TITAN_WALL and skill["skill"] == 0:
                        chance = True

                if entity.passive == "priest" and skill["skill"] == 0 and entity.is_passive:
                    if luck_skill == eff_now:
                        chance = True

                negate_fisico = False
                if "target" in entity.effects.keys():
                    if entity.effects["target"]['turns'] > 0:
                        if skill["type"] == "fisico":
                            negate_fisico = True

                if confusion or negate_fisico:
                    chance = False

                if chance:
                    if c in self.effects.keys() and c != "mirror":
                        if self.effects[c]['turns'] > 0:
                            # laranja
                            _text1 = f'🟠 **{self.name.upper()}** `ainda está sob o efeito de` **{c.upper()}**'
                            msg_return += f"{_text1}\n\n"
                    else:
                        if test:
                            if mirror_now:
                                _list_skills = list()
                                for _sk in self.skills.keys():
                                    if self.is_player:
                                        _effct = self.skills[_sk]['effs'][self.ls]
                                    else:
                                        _effct = self.skills[_sk]['effs']

                                    if _effct is not None:
                                        _list_skills.append(_sk)

                                _skills = choice(_list_skills)
                                _skills = self.skills[_skills]

                                if self.is_player:
                                    _effct = _skills['effs'][self.ls]
                                else:
                                    _effct = _skills['effs']

                                keys = list(_effct.keys())
                                for k in keys:

                                    self.effects[k] = _effct[k]
                                    min_turn, max_turn = 2, _effct[k]['turns']
                                    min_turn = 3 if k in _EFFECTS else min_turn

                                    if c == "looping":
                                        if "4" in skill["name"]:
                                            min_turn = 4
                                        elif "3" in skill["name"]:
                                            min_turn = 3
                                        elif "2" in skill["name"]:
                                            min_turn = 3

                                    max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                                    self.effects[k]['turns'] = randint(min_turn, max_turn)

                                    turns = self.effects[k]['turns']
                                    _eff += turns
                                    # verde
                                    _text2 = f'🟢 **{self.name.upper()}** `recebeu o efeito de` **{k.upper()}** ' \
                                             f'`por` **{turns}** `turno{"s" if turns > 1 else ""}`'

                                    if k.lower() == "smoke" and not entity.smoke_now:
                                        entity.smoke_now = True
                                        entity.status["agi"] += 60

                                    msg_return += f"{_text2}\n\n"

                            else:
                                self.effects[c] = skill['effs'][self.ls][c]
                                min_turn, max_turn = 2, skill['effs'][self.ls][c]['turns']
                                min_turn = 3 if c in _EFFECTS else min_turn

                                if c == "looping":
                                    if "4" in skill["name"]:
                                        min_turn = 4
                                    elif "3" in skill["name"]:
                                        min_turn = 3
                                    elif "2" in skill["name"]:
                                        min_turn = 3

                                max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                                self.effects[c]['turns'] = randint(min_turn, max_turn)
                        else:
                            if mirror_now:
                                _list_skills = list()
                                for _sk in self.skills.keys():
                                    if self.is_player:
                                        _effct = self.skills[_sk]['effs'][self.ls]
                                    else:
                                        _effct = self.skills[_sk]['effs']

                                    if _effct is not None:
                                        _list_skills.append(_sk)

                                _skills = choice(_list_skills)
                                _skills = self.skills[_skills]

                                if self.is_player:
                                    _effct = _skills['effs'][self.ls]
                                else:
                                    _effct = _skills['effs']

                                keys = list(_effct.keys())
                                for k in keys:
                                    self.effects[k] = _effct[k]
                                    min_turn, max_turn = 2, _effct[k]['turns']
                                    min_turn = 3 if k in _EFFECTS else min_turn
                                    max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                                    self.effects[k]['turns'] = randint(min_turn, max_turn)
                                    turns = self.effects[k]['turns']
                                    _eff += turns
                                    # verde
                                    _text2 = f'🟢 **{self.name.upper()}** `recebeu o efeito de` **{k.upper()}** ' \
                                             f'`por` **{turns}** `turno{"s" if turns > 1 else ""}`'

                                    if k.lower() == "smoke" and not entity.smoke_now:
                                        entity.smoke_now = True
                                        entity.status["agi"] += 60

                                    msg_return += f"{_text2}\n\n"

                            else:
                                self.effects[c] = skill['effs'][c]
                                min_turn, max_turn = 2, skill['effs'][c]['turns']
                                min_turn = 3 if c in _EFFECTS else min_turn
                                max_turn = min_turn + 1 if min_turn > max_turn else max_turn
                                self.effects[c]['turns'] = randint(min_turn, max_turn)

                        if not mirror_now:
                            turns = self.effects[c]['turns']
                            _eff += turns
                            # verde
                            _text2 = f'🟢 **{self.name.upper()}** `recebeu o efeito de` **{c.upper()}** `por` ' \
                                     f'**{turns}** `turno{"s" if turns > 1 else ""}`'

                            if c.lower() == "smoke" and not entity.smoke_now:
                                entity.smoke_now = True
                                entity.status["agi"] += 60

                            msg_return += f"{_text2}\n\n"
                else:
                    negate = ""
                    if negate_fisico:
                        negate += f" `por que` **{entity.name.upper()}** `está sob o feito de` **TARGET**"
                    # vermelho
                    _text3 = f'🔴 **{self.name.upper()}** `não recebeu o efeito de` **{c.upper()}**'
                    _text3 += negate
                    msg_return += f"{_text3}\n\n"

                eff_now += 1

        if skill['effs'] is not None and not act_eff:
            # branco
            _text_strike = f'⚪ **{self.name.upper()}** `não pode receber efeito dessa skill por que` ' \
                           f'**{entity.name}** `esta sob o efeito de` **STRIKE**'
            msg_return += f"{_text_strike}\n\n"

        return entity, msg_return, _eff, chance

    def calc_damage_skill(self, skill, test, lvs, enemy_cc, enemy_atk, half_life_priest, stack_2):
        damage_enchant = skill['damage'][self.ls] if test else skill['damage']
        d1 = int(damage_enchant[:damage_enchant.find('d')])
        d2 = int(damage_enchant[damage_enchant.find('d') + 1:])
        dd, d3 = [d2, d2 * d1] if d2 != d2 * d1 else [d2, d2], int((lvs - 10) * 10)
        dd = [d2 + d3, d2 * d1] if lvs >= 11 else dd
        dd[1] = dd[0] + 1 if dd[0] > dd[1] else dd[1]

        if stack_2 and int(skill["skill"]) in [1, 2, 3, 4, 5]:
            if dd[0] != dd[1]:
                dd[0] = dd[0] * 2
                if dd[0] > dd[1]:
                    dd[0] = dd[1] - 1

        bk = randint(dd[0], dd[1]) if dd[0] != dd[1] else dd[0]

        if test:
            if enemy_cc[1] in ['necromancer', 'wizard', 'warlock']:
                tot_enemy_atk = int(enemy_atk * 1.6)
            elif enemy_cc[1] in ['assassin', 'priest']:
                tot_enemy_atk = int(enemy_atk * 1.4)
            else:
                tot_enemy_atk = int(enemy_atk * 1.2)

            variacao = (50 + randint(skill['skill'], skill['skill'] * 10))
            if stack_2 and int(skill["skill"]) in [1, 2, 3, 4, 5]:
                variacao = (50 + randint(skill['skill'] * 5, skill['skill'] * 10))

            damage_skill = int(tot_enemy_atk / 100 * variacao)

            if skill["skill"] == 0:
                # nerf no dano da skill base
                damage_skill = int(tot_enemy_atk / 100 * randint(1 + lvs, 2 + (lvs * 2)))

            damage = damage_skill + bk

        else:
            damage = enemy_atk + bk

        if half_life_priest and int(skill["skill"]) in [1, 2, 3, 4, 5]:
            if not self.is_boss and not self.is_mini_boss:
                damage = (self.status['hp'] // 4) + damage  # 25% do HP atual + atak da skill

        return damage

    async def chance_critical(self, ctx, entity, test, skull, damage):
        enemy_cc, enemy_luk = entity.cc, entity.status['luk']
        critical, critical_chance, critical_damage, value_critical = False, randint(1, 30), enemy_cc[0], 29
        if enemy_cc[1] in ['necromancer', 'wizard', 'warlock']:
            value_critical = 27
        if enemy_cc[1] in ['assassin', 'priest']:
            value_critical = 25
        if test:
            value_critical -= int(enemy_luk / 5)

        if entity.passive == "warrior":
            if entity.IRON_FISTS:
                critical_chance += critical_chance // 10

            if entity.TITAN_WALL:
                critical_chance -= critical_chance // 10

        if "cegueira" in self.effects.keys():
            if self.effects["cegueira"]['turns'] > 0:
                critical_chance = value_critical + 1

        if critical_chance >= value_critical:
            critical = True

        if skull:
            critical = False

        if critical:
            _cd = randint(int(critical_damage / 2), critical_damage)
            damage = int(damage + (damage / 100 * _cd))  # adiciona a % do critical
            embed = disnake.Embed(title="CRITICAL", color=0x38105e)
            file = disnake.File("images/elements/critical.gif", filename="critical.gif")
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
            is_combo_passive = ""
            if entity.is_combo_passive:
                entity.is_combo_passive = False
                _damage = (self.status['hp'] // 4) * 3

                self.effects["silencio"] = {"type": "normal", "turns": randint(2, 5), "damage": None}
                self.effects["fraquesa"] = {"type": "normal", "turns": randint(2, 5), "damage": None}

                is_combo_passive = "\n\n"

                turns = self.effects["silencio"]["turns"]
                is_combo_passive += f'🟢 **{self.name.upper()}** `recebeu o efeito de` **SILENCIO** `por` ' \
                                    f'**{turns}** `turno{"s" if turns > 1 else ""}`\n\n'

                turns = self.effects["fraquesa"]["turns"]
                is_combo_passive += f'🟢 **{self.name.upper()}** `recebeu o efeito de` **FRAQUESA** `por` ' \
                                    f'**{turns}** `turno{"s" if turns > 1 else ""}`'

            _damage = _damage if not self.is_boss and not self.is_mini_boss else 0

            self.status['hp'] -= _damage
            if self.status['hp'] < 0:
                self.status['hp'] = 0

            monster = not self.is_player if self.is_pvp else self.is_player
            bmsg = "\n`boss e mini boss são imune a combo!`" if self.is_boss or self.is_mini_boss else ""
            type_combo = "combo" if not is_combo_passive else "combo especial"
            description = f'**{self.name.upper()}** `recebeu` **{_damage}** `de dano, por levar um ` **{type_combo}!**'
            description += bmsg
            description += is_combo_passive
            img = "https://media.giphy.com/media/INEBdVgN59AbWhyZCk/giphy.gif"
            embed_ = embed_creator(description, img, monster, self.tot_hp, self.status['hp'], self.img, self.name)
            await ctx.send(embed=embed_)

            if not self.is_pvp and self.data["salvation"] and self.status['hp'] <= 0:
                self.data["salvation"] = False
                self.status['hp'] = self.tot_hp
                self.status['mp'] = self.tot_mp
                self.potion = 0
                self.limit = [0, 0, 0, 0, 0]
                await ctx.send(f'**{self.name.upper()}** `por esta equipado com` **SALVATION** `na hora da sua morte'
                               f' reviveu!`')

            return entity

        msg_return, lethal, _eff, chance, msg_drain, test = "", False, 0, False, "", not self.is_player or self.is_pvp
        lp, ignition, drain, bluff, hit_kill, hold, duelist, stk1, stk2, lt, ds = self.verify_effect()
        half_life_priest, lvs_skill, barrier, rage, charge, skull = False, 1, False, False, False, False

        if "barrier" in self.effects.keys():
            if self.effects["barrier"]['turns'] > 0:
                barrier = True

        if "charge" in self.effects.keys():
            if self.effects["charge"]['turns'] > 0:
                charge = True

        if test:
            lvs_skill = int(skill['skill']) if int(skill['skill']) != 0 else int(skill['skill']) + 1
        lvs = entity.level_skill[lvs_skill - 1] if test else entity.level_skill[0]
        self.ls, confusion, act_eff, _soulshot, bda, reflect = lvs if 0 <= lvs <= 9 else 9, False, True, 0, 0, False

        if entity.effects is not None:

            if "rage" in entity.effects.keys():
                if entity.effects["rage"]["turns"] > 0:
                    rage = True

            if "confusion" in entity.effects.keys():
                if entity.effects["confusion"]["turns"] > 0:
                    confusion = True if randint(1, 2) == 1 else False

            if "strike" in entity.effects.keys():
                if entity.effects["strike"]['turns'] > 0:
                    act_eff = False

            if "skull" in entity.effects.keys():
                if entity.effects["skull"]["turns"] > 0:
                    skull = True

        if stk1 and stk2 and not self.is_boss and not self.is_mini_boss:
            half_life_priest = True

        resp = self.chance_effect_skill(entity, skill, msg_return, test, act_eff, bluff, confusion, lvs, _eff, chance)

        # desabilita a chance 100% do modo SPEAR_OF_DESTINY
        if entity.passive == "warlock":
            if entity.SPEAR_OF_DESTINY and skill["skill"] == 0:
                entity.SPEAR_OF_DESTINY = False

        # desabilita a chance 100% do modo CLAWS_STUCK
        if entity.passive == "assassin":
            if entity.CLAWS_STUCK and skill["skill"] == 0:
                entity.CLAWS_STUCK = False

        # desabilita a chance 100% do modo IRON_FISTS e TITAN_WALL
        if entity.passive == "warrior":
            if entity.IRON_FISTS and skill["skill"] == 0:
                entity.IRON_FISTS = False

            if entity.TITAN_WALL and skill["skill"] == 0:
                entity.TITAN_WALL = False

        entity, msg_return, _eff, chance = resp[0], resp[1], resp[2], resp[3]
        damage = self.calc_damage_skill(skill, test, lvs, entity.cc, entity.status['atk'], half_life_priest, stk2)

        if entity.passive == "warrior":
            if entity.IRON_FISTS:  # passiva de atk do warrior
                damage += int(damage / 100 * randint(60, 80))

            if entity.TITAN_WALL:  # passiva de def do warrior
                damage -= int(damage / 100 * randint(60, 80))

        duel, duel_msg = int(damage / 100 * randint(40, 80)), ""  # 40 a 80% de dano a mais
        damage = damage if not duelist else duel + duel
        if duelist:
            duel_msg += f'\n**{entity.name.upper()}** `adicinou` **{duel}** `de dano a mais, pelo ' \
                           f'efeito` **duelist** `nesse turno.`'

        # verificação especial para que o EFFECT nao perca o seu primeiro turno
        lp, ignition, drain, bluff, hit_kill, hold, duelist, stk1, stk2, lt, ds = self.verify_effect()

        msg_hl_priest, lethal = "", lt

        if stk1 and stk2 and not self.is_boss and not self.is_mini_boss:
            msg_hl_priest += f"**{self.name.upper()}** `levou o combo especial do` **{entity.name.upper()}**"

        if test:
            if entity.soulshot[0] and entity.soulshot[1] > 1:
                entity.soulshot[1] -= 1
                _soulshot = CLS[entity.data['class_now']]['soulshot']
                bda = int(damage / 100 * _soulshot) if int(damage / 100 * _soulshot) < 100 else 99
                # o limit de dano da soulshot é de 99 de damage
                if skull:
                    bda = 0  # o efeito de skull elimita o adicional da soulshot
                damage += bda

        res = await self.chance_critical(ctx, entity, test, skull, damage)
        defense, critical, damage = self.pdef if skill['type'] == "fisico" else self.mdef, res[0], res[1]

        if self.passive == "warrior":
            if self.TITAN_WALL:
                defense = self.ultimate_defense

        if self.passive == "warrior":
            if self.IRON_FISTS:
                defense -= defense // 2

        if barrier and skill['type'] == "magico":  # aumenta a defesa magica
            defense += defense // 100 * randint(40, 80)

        if skill['type'] == "especial":
            defense = choice([self.pdef, self.mdef])

            if self.passive == "warrior":
                if self.TITAN_WALL:
                    defense = self.ultimate_defense

        if stk2 or lethal:
            defense = defense // 2

        reflect_damage = 0
        if "reflect" in entity.effects.keys():
            reflect_damage += int(damage / 100 * randint(50, 75))  # reflete 50 a 75% do dano recebido
            reflect, damage = True, damage - reflect_damage
            entity.effects['reflect']['damage'] = reflect_damage

        looping_msg, total_bonus_dn = "\n", 0
        if lp:
            for _ in range(self.effects["looping"]["turns"]):
                total_bonus_dn += randint(int(damage * 0.40), int(damage * 0.80))
            looping_msg += f'\n**{entity.name.upper()}** `adicinou` **{total_bonus_dn}** `de dano a mais, pelo ' \
                           f'efeito` **looping** `ter pego` **{self.effects["looping"]["turns"]}x** ` nesse turno.`'

        dualshot_msg, total_bonus_ds = "\n", 0
        if ds:
            total_bonus_ds += randint(int(damage * 0.75), int(damage * 0.95))
            dualshot_msg += f'\n**{entity.name.upper()}** `adicinou` **{total_bonus_ds}** `de dano a mais, pelo ' \
                            f'efeito` **dualshot** `ter pego nesse turno.`'

        salvation = self.data["salvation"]
        if not self.is_boss and not self.is_mini_boss:
            if salvation:
                hold = False
                damage = damage // 2
                defense += defense // 4

        damage += total_bonus_dn  # adicionado antes da defesa / adição a loop

        # NOVO SISTEMA DE DEFESA
        armor_now, damage_now = defense // 50, damage // 100
        if self.is_player:  # sistema de proteção apenas para jogadores
            damage_now = damage_now if damage_now > 0 else 1  # o dano que que ser no minimo 1
        armor_now, total_percent = 64 if armor_now >= 65 else armor_now, 65

        if not self.is_boss and not self.is_mini_boss:
            if salvation:
                armor_now += 15
                total_percent += 15
                
        if self.is_player:
            if self.data["set_equip"]:
                armor_now += 10
                total_percent += 10

        if self.passive == "warrior":
            if self.TITAN_WALL:
                armor_now += 25
                total_percent += 25

        if self.passive == "warrior":
            if self.IRON_FISTS:
                armor_now -= 10
                total_percent -= 10

        defended = randint(armor_now * damage_now, total_percent * damage_now) if defense > 0 else 0

        defended, rage_msg = 0 if hold else defended, ""  # efeito da hold
        if rage and not hold:  # sistema de acumulação (RAGE)
            rage_damage_now = int(defended / 100 * randint(50, 75))
            self.rage_damage += rage_damage_now
            defended = defended - rage_damage_now
            rage_msg += f" `e` **{self.name.upper()}** `acumulou` **{defended}** `de dano, pelo efeito de` **rage**"

        # charge
        charge_msg = ""
        if charge and entity.rage_damage > 0:
            charge_damage = entity.rage_damage
            entity.rage_damage = 0
            damage += charge_damage
            charge_msg += f'\n**{entity.name.upper()}** `adicinou` **{charge_damage}** `de dano a mais, pelo ' \
                          f'efeito` **charge** `ter pego nesse turno.`'

        damage += total_bonus_ds  # adicional do dano de DUALSHOT
        dn = damage - defended  # dano verdadeiro.

        if reflect:
            _text4 = f'**{self.name.upper()}** `refletiu` **{reflect_damage}** `do dano que recebeu`'
            msg_return += f"{_text4}\n\n"

        if dn <= 0:
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

                presas_active = False
                if "presas" in entity.effects.keys():
                    if entity.effects["presas"]["turns"] >= 1:
                        presas_active = True

                if not presas_active:
                    dr = self.effects["drain"]["damage"]
                    _dr = dr if dr == 50 else randint(50, dr)
                    recovery = int(dn / 100 * _dr)
                    entity.status['hp'] += recovery
                    if entity.status['hp'] > entity.status['con'] * entity.rate[0]:
                        entity.status['hp'] = entity.status['con'] * entity.rate[0]
                    msg_drain += f'**{entity.name.upper()}** `recuperou` **{recovery}** `de HP pelo efeito` **drain**'
                else:
                    msg_drain += f'**{entity.name.upper()}** `não recuperou HP pois está sob o ' \
                                 f'efeito de` **presas**'

            if not confusion and not hit_kill:
                self.status['hp'] -= dn
                if self.status['hp'] < 0:
                    self.status['hp'] = 0
                bb = "" if bda == 0 else f"\n`e` **{_soulshot}%** `de dano a mais por causa da soulshot:` **{bda}**"
                if defended > 0:
                    descrip = f'**{self.name.upper()}** `absorveu` **{defended}** `de dano, recebendo` **{dn}** {bb}'
                else:
                    descrip = f'**{self.name.upper()}** `recebeu` **{damage}** `de dano` {bb}'

                descrip += rage_msg  # rage effect
                descrip += looping_msg  # looping effect
                descrip += charge_msg  # charge effect
                descrip += duel_msg  # duelist effect
                descrip += dualshot_msg  # dualshot effect

            elif hit_kill and not confusion:
                if not self.is_boss and not self.is_mini_boss:
                    _lethal = self.status['hp'] - 1
                    self.status['hp'] = 1
                else:
                    _lethal = self.status['hp'] // 20
                    self.status['hp'] -= _lethal
                descrip = f'**{self.name.upper()}** `recebeu` **{_lethal}** `de dano` **LETHAL!**'

            else:

                entity.status['hp'] -= damage
                if entity.status['hp'] < 0:
                    entity.status['hp'] = 0

                bb = "" if bda == 0 else f"\n`e` **{_soulshot}%** `de dano a mais por causa da soulshot:` **{bda}**"
                confusy = "`, por está confuso o golpe acertou a si mesmo!`"
                descrip = f'**{entity.name.upper()}** `recebeu` **{damage}** `de dano` {bb}{confusy}'

            descrip += msg_drain
            msg_return += f"{descrip}\n" + msg_hl_priest + "\n\n"

        monster = not self.is_player if self.is_pvp else self.is_player
        bed_ = embed_creator(msg_return, skill['img'], monster, self.tot_hp, self.status['hp'], self.img, self.name)
        if msg_return != "":
            await ctx.send(embed=bed_)

        if not self.is_pvp and self.data["salvation"] and self.status['hp'] <= 0:
            self.data["salvation"] = False
            self.status['hp'] = self.tot_hp
            self.status['mp'] = self.tot_mp
            self.potion = 0
            self.limit = [0, 0, 0, 0, 0]
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
        self.champions = all_data['battle']['champions']

    def set_monster(self, db_player, mini_boss=False, min_max=None, champion=False):
        lvl = db_player['level']
        dif = 2 if lvl < 2 else 3 if 2 <= lvl <= 9 else 4 if 10 <= lvl <= 30 else 5 if 31 <= lvl <= 50 else 6
        min_, max_ = lvl - 5 if lvl - 5 > 1 else 1, lvl + dif if lvl + dif <= 99 else 99
        min_, moon_data = min_ if min_ <= 55 else 55, get_moon()
        mini_boss_monster = self.mb[self.mini_boss[moon_data[0]]]

        if lvl <= 10 and max_ > 10:
            max_ = 10

        if lvl <= 20 and max_ > 20:
            max_ = 20

        if lvl <= 40 and max_ > 40:
            max_ = 40

        if lvl <= 60 and max_ > 60:
            max_ = 60

        if lvl <= 80 and max_ > 80:
            max_ = 80

        if lvl <= 99 and max_ > 99:
            max_ = 99

        if min_max is not None:
            min_, max_ = min_max[0], min_max[1]

        _monster = choice([m for m in self.m if min_ < self.m[self.m.index(m)]['level'] < max_])

        if champion:
            _monster = choice(self.champions)

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
        _min, _max = 25 + rr if rr + 20 < 95 else 95, 30 + rr if rr + 30 < 99 else 99
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
        db_player["img"] = user.display_avatar.with_format("png")
        db_player["pdef"], db_player["mdef"] = 0, 0
        _db_class = data["rpg"]["sub_class"][_class]

        # novidades da atualização
        db_player["mana_bonus"] = int(_db_class["status"]["con"])
        db_player["atk_bonus"] = int(_db_class["status"]["atk"])
        db_player["status"] = _db_class["status"]
        db_player["skills"] = _db_class["skills"]
        db_player["skill_level"] = _db_class["skill_level"]
        db_player["set_equip"] = False

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

                if c == "sword":
                    weapon_name = all_data['equips']["weapons"][db_player["equipped_items"][c]]["name"]
                    weapon_class = weapon_name.split()[0]

                    if "silver" in weapon_name:

                        atk_weapon_bonus = 0
                        if weapon_class in ['assassin', 'priest']:
                            atk_weapon_bonus += 40

                        if weapon_class in ['paladin', 'warrior']:
                            atk_weapon_bonus += 20

                        if weapon_class in ['necromancer', 'wizard', 'warlock']:
                            atk_weapon_bonus += 30

                        db_player["status"]["atk"] += db_player["atk_bonus"] + atk_weapon_bonus

                    if "mystic" in weapon_name:

                        atk_weapon_bonus = 0
                        if weapon_class in ['assassin', 'priest']:
                            atk_weapon_bonus += 60

                        if weapon_class in ['paladin', 'warrior']:
                            atk_weapon_bonus += 30

                        if weapon_class in ['necromancer', 'wizard', 'warlock']:
                            atk_weapon_bonus += 45

                        db_player["status"]["atk"] += db_player["atk_bonus"] + atk_weapon_bonus

                    if"inspiron" in weapon_name:

                        atk_weapon_bonus = 0
                        if weapon_class in ['assassin', 'priest']:
                            atk_weapon_bonus += 80

                        if weapon_class in ['paladin', 'warrior']:
                            atk_weapon_bonus += 40

                        if weapon_class in ['necromancer', 'wizard', 'warlock']:
                            atk_weapon_bonus += 60

                        db_player["status"]["atk"] += db_player["atk_bonus"] + atk_weapon_bonus

                    if "violet" in weapon_name:

                        atk_weapon_bonus = 0
                        if weapon_class in ['assassin', 'priest']:
                            atk_weapon_bonus += 100

                        if weapon_class in ['paladin', 'warrior']:
                            atk_weapon_bonus += 50

                        if weapon_class in ['necromancer', 'wizard', 'warlock']:
                            atk_weapon_bonus += 75

                        db_player["status"]["atk"] += db_player["atk_bonus"] + atk_weapon_bonus

                    if "hero" in weapon_name:

                        atk_weapon_bonus = 0
                        if weapon_class in ['assassin', 'priest']:
                            atk_weapon_bonus += 120

                        if weapon_class in ['paladin', 'warrior']:
                            atk_weapon_bonus += 60

                        if weapon_class in ['necromancer', 'wizard', 'warlock']:
                            atk_weapon_bonus += 90

                        db_player["status"]["atk"] += db_player["atk_bonus"] + atk_weapon_bonus

                    if "divine" in weapon_name:

                        atk_weapon_bonus = 0
                        if weapon_class in ['assassin', 'priest']:
                            atk_weapon_bonus += 300

                        if weapon_class in ['paladin', 'warrior']:
                            atk_weapon_bonus += 200

                        if weapon_class in ['necromancer', 'wizard', 'warlock']:
                            atk_weapon_bonus += 250

                        db_player["status"]["atk"] += db_player["atk_bonus"] + atk_weapon_bonus

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
                db_player["set_equip"] = True
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
