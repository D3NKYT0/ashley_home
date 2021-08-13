import discord
import copy

import time as date
from asyncio import sleep
from discord.ext import commands
from random import randint, choice
from resources.entidade import Entity
from resources.check import check_it
from resources.db import Database
from resources.img_edit import calc_xp
from datetime import datetime

evasion = {}
raid_rank = {}
p_raid = {}
m_raid = {}
money = {}
xp_tot = {}
xp_off = {}
git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class Raid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.m = self.bot.config['battle']['monsters']
        self.w_s = self.bot.config['attribute']['chance_weapon']
        self.db_monster = {}
        self.db_player = {}

    def choice_monster(self, data, db_player, rr):
        # configuração do monstro
        _min, _max = 25 + rr if rr < 31 else 59, 30 + rr if rr < 31 else 60
        _monster = choice([m for m in self.m if _min < self.m[self.m.index(m)]['level'] < _max])
        _monster_now = copy.deepcopy(_monster)
        _monster_now['lower_net'] = True if data['rpg']['lower_net'] else False
        _monster_now['enemy'] = db_player
        _monster_now["pdef"] = rr * 20
        _monster_now["mdef"] = rr * 20
        _monster_now["status"]["con"] += rr * 10

        # bonus status monster
        for k in _monster_now["status"].keys():
            if db_player['level'] > 25:
                _monster_now["status"][k] += randint(2, 4)

        for sts in db_player['equipped_items'].keys():
            if db_player['equipped_items'][sts] is not None:
                _monster_now["status"]["atk"] += randint(0, 2)
                _monster_now["status"]["con"] += randint(0, 2)
                _monster_now["status"]["luk"] += randint(0, 2)
        return _monster_now

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='wave', aliases=['onda', 'orda', 'w'])
    async def wave(self, ctx):
        """Comando usado pra batalhar no rpg da ashley
        Use ash raid"""
        global raid_rank, m_raid, p_raid, money, xp_tot, xp_off, evasion
        xp_off[ctx.author.id] = False
        evasion[ctx.author.id] = [[0, False], [0, False]]

        raid_rank[ctx.author.id] = 0
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.desafiado:
            return await ctx.send("<:alert:739251822920728708>│`Você está sendo desafiado/desafiando para um PVP!`")

        if ctx.author.id in self.bot.batalhando:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`VOCE JÁ ESTÁ BATALHANDO!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if not data['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        _class = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_class]
        if _db_class['level'] < 26:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA ESTA NO NIVEL 26 OU MAIOR PARA IR UMA RAID!\n' \
                  'OLHE O SEU NIVEL NO COMANDO:` **ASH SKILL**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        ct = 50
        if data['rpg']['active']:
            date_old = data['rpg']['activated_at']
            date_now = datetime.today()
            days = abs((date_old - date_now).days)
            if days <= 10:
                ct = 5

        try:
            if data['inventory']['coins'] < ct:
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f'<:negate:721581573396496464>│`VOCE PRECISA DE + DE {ct} FICHAS PARA BATALHAR!`\n'
                                f'**OBS:** `USE O COMANDO` **ASH SHOP** `PARA COMPRAR FICHAS!`')
                return await ctx.send(embed=embed)
        except KeyError:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`VOCE NÃO TEM FICHA!`')
            return await ctx.send(embed=embed)

        update['inventory']['coins'] -= ct
        self.bot.batalhando.append(ctx.author.id)
        await self.bot.db.update_data(data, update, 'users')

        # configuração do player
        set_value = ["shoulder", "breastplate", "gloves", "leggings", "boots"]
        self.db_player[ctx.author.id] = data['rpg']
        self.db_player[ctx.author.id]["img"] = ctx.author.avatar_url_as(format="png")
        self.db_player[ctx.author.id]['name'] = ctx.author.name
        self.db_player[ctx.author.id]["pdef"] = 0
        self.db_player[ctx.author.id]["mdef"] = 0
        self.db_player[ctx.author.id]["_id"] = ctx.author.id

        _class = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_class]
        self.db_player[ctx.author.id]["xp"] = _db_class["xp"]
        self.db_player[ctx.author.id]["level"] = _db_class["level"]

        soul, amount = False, 0
        if data['rpg']["equipped_items"]['consumable'] is not None:
            if 'soushot' in data['rpg']["equipped_items"]['consumable']:
                soul = True
                amount += 1
                if data['rpg']["equipped_items"]['consumable'] in data['rpg']['items'].keys():
                    amount += data['rpg']['items'][data['rpg']["equipped_items"]['consumable']]
        self.db_player[ctx.author.id]["soulshot"] = [soul, amount]

        set_e = list()

        # bonus status player
        eq = dict()
        for ky in self.bot.config["equips"].keys():
            for kk, vv in self.bot.config["equips"][ky].items():
                eq[kk] = vv

        for k in self.db_player[ctx.author.id]["status"].keys():
            try:
                temp_1 = self.bot.config["skills"][self.db_player[ctx.author.id]['class']]['modifier'][k]
                self.db_player[ctx.author.id]["status"][k] += temp_1

                if self.db_player[ctx.author.id]['level'] > 25:
                    temp_2 = self.bot.config["skills"][self.db_player[ctx.author.id]['class_now']]['modifier'][k]
                    self.db_player[ctx.author.id]["status"][k] += temp_2

                if self.db_player[ctx.author.id]['level'] > 49:
                    temp_3 = self.bot.config["skills"][self.db_player[ctx.author.id]['class_now']]['modifier_50'][k]
                    self.db_player[ctx.author.id]["status"][k] += temp_3

                if self.db_player[ctx.author.id]['level'] > 79:
                    temp_4 = self.bot.config["skills"][self.db_player[ctx.author.id]['class_now']]['modifier_80'][k]
                    self.db_player[ctx.author.id]["status"][k] += temp_4

            except KeyError:
                pass

        for c in self.db_player[ctx.author.id]['equipped_items'].keys():
            if self.db_player[ctx.author.id]['equipped_items'][c] is None:
                continue

            if c in set_value:
                set_e.append(str(c))

            self.db_player[ctx.author.id]["pdef"] += eq[self.db_player[ctx.author.id]['equipped_items'][c]]['pdef']
            self.db_player[ctx.author.id]["mdef"] += eq[self.db_player[ctx.author.id]['equipped_items'][c]]['mdef']
            for name in self.db_player[ctx.author.id]["status"].keys():
                try:
                    temp_3 = eq[self.db_player[ctx.author.id]['equipped_items'][c]]['modifier'][name]
                    self.db_player[ctx.author.id]["status"][name] += temp_3
                except KeyError:
                    pass

        for kkk in self.bot.config["set_equips"].values():
            if kkk['set'] == set_e:
                for name in self.db_player[ctx.author.id]["status"].keys():
                    try:
                        self.db_player[ctx.author.id]["status"][name] += kkk['modifier'][name]
                    except KeyError:
                        pass
                self.db_player[ctx.author.id]["pdef"] += kkk["pdef"]
                self.db_player[ctx.author.id]["mdef"] += kkk["mdef"]

        # criando as entidade do jogador...
        _db_player = self.db_player[ctx.author.id]
        if ctx.author.id in p_raid.keys():
            del p_raid[ctx.author.id]
        p_raid[ctx.author.id] = Entity(_db_player, True, raid=True)

        # ======================================================================================================
        # ----------------------------------- SYSTEM RAID MONSTERS / BOSS --------------------------------------
        # ======================================================================================================

        _mon = self.choice_monster(data, self.db_player[ctx.author.id], raid_rank[ctx.author.id])
        self.db_monster[ctx.author.id] = _mon
        # criando as entidade do monstro...
        _db_monster = self.db_monster[ctx.author.id]
        if ctx.author.id in m_raid.keys():
            del m_raid[ctx.author.id]
        m_raid[ctx.author.id] = Entity(_db_monster, False, raid=True)
        money[ctx.author.id] = self.db_monster[ctx.author.id]['ethernya']
        xp_tot[ctx.author.id] = [(self.db_monster[ctx.author.id]['xp'], self.db_monster[ctx.author.id]['level'])]

        # durante a batalha
        while not self.bot.is_closed():

            # -----------------------------------------------------------------------------
            if p_raid[ctx.author.id].status['hp'] <= 0:
                break
            if m_raid[ctx.author.id].status['hp'] <= 0:
                raid_rank[ctx.author.id] += 1
                _mon = self.choice_monster(data, self.db_player[ctx.author.id], raid_rank[ctx.author.id])
                self.db_monster[ctx.author.id] = _mon
                msg = f"Voce derrotou o {raid_rank[ctx.author.id]}° monstro, proximo..."
                embed = discord.Embed(color=self.bot.color, title=msg)
                embed.set_image(url=self.db_monster[ctx.author.id]['img'])
                await ctx.send(embed=embed)
                # criando as entidade do monstro...
                _db_monster = self.db_monster[ctx.author.id]
                if ctx.author.id in m_raid.keys():
                    del m_raid[ctx.author.id]
                m_raid[ctx.author.id] = Entity(_db_monster, False, raid=True)
                p_raid[ctx.author.id].next = 0
                money[ctx.author.id] += self.db_monster[ctx.author.id]['ethernya']
                xp_tot[ctx.author.id].append((self.db_monster[ctx.author.id]['xp'],
                                              self.db_monster[ctx.author.id]['level']))

            skill = await p_raid[ctx.author.id].turn([m_raid[ctx.author.id].status, m_raid[ctx.author.id].rate,
                                                      m_raid[ctx.author.id].name, m_raid[ctx.author.id].lvl],
                                                     self.bot, ctx, raid_num=raid_rank[ctx.author.id])

            if skill == "BATALHA-CANCELADA":
                p_raid[ctx.author.id].status['hp'] = 0
                xp_off[ctx.author.id] = True

            if p_raid[ctx.author.id].status['hp'] <= 0:
                break
            if m_raid[ctx.author.id].status['hp'] <= 0:
                raid_rank[ctx.author.id] += 1
                _mon = self.choice_monster(data, self.db_player[ctx.author.id], raid_rank[ctx.author.id])
                self.db_monster[ctx.author.id] = _mon
                msg = f"Voce derrotou o {raid_rank[ctx.author.id]}° monstro, proximo..."
                embed = discord.Embed(color=self.bot.color, title=msg)
                embed.set_image(url=self.db_monster[ctx.author.id]['img'])
                await ctx.send(embed=embed)
                # criando as entidade do monstro...
                _db_monster = self.db_monster[ctx.author.id]
                if ctx.author.id in m_raid.keys():
                    del m_raid[ctx.author.id]
                m_raid[ctx.author.id] = Entity(_db_monster, False, raid=True)
                p_raid[ctx.author.id].next = 0
                money[ctx.author.id] += self.db_monster[ctx.author.id]['ethernya']
                xp_tot[ctx.author.id].append((self.db_monster[ctx.author.id]['xp'],
                                              self.db_monster[ctx.author.id]['level']))
            # -----------------------------------------------------------------------------

            if skill == "COMANDO-CANCELADO":
                if ctx.author.id in self.bot.batalhando:
                    self.bot.batalhando.remove(ctx.author.id)
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito` '
                                      '**COMANDO CANCELADO**')

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            atk = int(p_raid[ctx.author.id].status['atk'])

            # player chance
            d20 = randint(1, 20)
            lvlp = int(p_raid[ctx.author.id].lvl / 10)
            prec = int(p_raid[ctx.author.id].status['prec'] / 2)
            chance_player = d20 + lvlp + prec

            # monster chance
            d16 = randint(1, 16)
            lvlm = int(m_raid[ctx.author.id].lvl / 10)
            agi = int(m_raid[ctx.author.id].status['agi'] / 3)
            chance_monster = d16 + lvlm + agi

            if m_raid[ctx.author.id].effects is not None:
                if "gelo" in m_raid[ctx.author.id].effects.keys():
                    if m_raid[ctx.author.id].effects["gelo"]["turns"] > 0:
                        if p_raid[ctx.author.id].soulshot[0] and p_raid[ctx.author.id].soulshot[1] > 1:
                            chance_monster = 0
                if "stun" in m_raid[ctx.author.id].effects.keys():
                    if m_raid[ctx.author.id].effects["stun"]["turns"] > 0:
                        if p_raid[ctx.author.id].soulshot[0] and p_raid[ctx.author.id].soulshot[1] > 1:
                            chance_monster = 0
                if "hold" in m_raid[ctx.author.id].effects.keys():
                    if m_raid[ctx.author.id].effects["hold"]["turns"] > 0:
                        chance_monster = 0

            evasion[ctx.author.id][0][1] = False if chance_player > chance_monster else True
            if evasion[ctx.author.id][0][1] and evasion[ctx.author.id][0][0] > 1:
                chance_monster, evasion[ctx.author.id][0][1] = 0, False
            if not evasion[ctx.author.id][0][1]:
                evasion[ctx.author.id][0][0] = 0

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill is None:
                chance_player, chance_monster = True, False

            if chance_player > chance_monster:
                p_raid[ctx.author.id] = await m_raid[ctx.author.id].damage(ctx, p_raid[ctx.author.id], skill, atk)
            else:

                if evasion[ctx.author.id][0][1]:
                    evasion[ctx.author.id][0][0] += 1

                embed = discord.Embed(
                    description=f"`{m_raid[ctx.author.id].name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=f"{self.db_monster[ctx.author.id]['name']}",
                                 icon_url=f"{self.db_monster[ctx.author.id]['img']}")
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            # -----------------------------------------------------------------------------
            if p_raid[ctx.author.id].status['hp'] <= 0:
                break
            if m_raid[ctx.author.id].status['hp'] <= 0:
                raid_rank[ctx.author.id] += 1
                _mon = self.choice_monster(data, self.db_player[ctx.author.id], raid_rank[ctx.author.id])
                self.db_monster[ctx.author.id] = _mon
                msg = f"Voce derrotou o {raid_rank[ctx.author.id]}° monstro, proximo..."
                embed = discord.Embed(color=self.bot.color, title=msg)
                embed.set_image(url=self.db_monster[ctx.author.id]['img'])
                await ctx.send(embed=embed)
                # criando as entidade do monstro...
                _db_monster = self.db_monster[ctx.author.id]
                if ctx.author.id in m_raid.keys():
                    del m_raid[ctx.author.id]
                m_raid[ctx.author.id] = Entity(_db_monster, False, raid=True)
                p_raid[ctx.author.id].next = 0
                money[ctx.author.id] += self.db_monster[ctx.author.id]['ethernya']
                xp_tot[ctx.author.id].append((self.db_monster[ctx.author.id]['xp'],
                                              self.db_monster[ctx.author.id]['level']))

            skill = await m_raid[ctx.author.id].turn(m_raid[ctx.author.id].status['hp'], self.bot, ctx)

            if skill == "BATALHA-CANCELADA":
                p_raid[ctx.author.id].status['hp'] = 0
                xp_off[ctx.author.id] = True

            if p_raid[ctx.author.id].status['hp'] <= 0:
                break
            if m_raid[ctx.author.id].status['hp'] <= 0:
                raid_rank[ctx.author.id] += 1
                _mon = self.choice_monster(data, self.db_player[ctx.author.id], raid_rank[ctx.author.id])
                self.db_monster[ctx.author.id] = _mon
                msg = f"Voce derrotou o {raid_rank[ctx.author.id]}° monstro, proximo..."
                embed = discord.Embed(color=self.bot.color, title=msg)
                embed.set_image(url=self.db_monster[ctx.author.id]['img'])
                await ctx.send(embed=embed)
                # criando as entidade do monstro...
                _db_monster = self.db_monster[ctx.author.id]
                if ctx.author.id in m_raid.keys():
                    del m_raid[ctx.author.id]
                m_raid[ctx.author.id] = Entity(_db_monster, False, raid=True)
                p_raid[ctx.author.id].next = 0
                money[ctx.author.id] += self.db_monster[ctx.author.id]['ethernya']
                xp_tot[ctx.author.id].append((self.db_monster[ctx.author.id]['xp'],
                                              self.db_monster[ctx.author.id]['level']))
            # -----------------------------------------------------------------------------

            if skill == "COMANDO-CANCELADO":
                if ctx.author.id in self.bot.batalhando:
                    self.bot.batalhando.remove(ctx.author.id)
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito` '
                                      '**COMANDO CANCELADO**')

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            bonus_raid = int(5 * raid_rank[ctx.author.id])
            raid_info = m_raid[ctx.author.id].cc
            raid_info[0] = bonus_raid

            atk_bonus = m_raid[ctx.author.id].status['atk'] * 0.5 if p_raid[ctx.author.id].lvl > 25 else \
                m_raid[ctx.author.id].status['atk'] * 0.25
            atk = int(m_raid[ctx.author.id].status['atk'] + atk_bonus)

            # monster chance
            d20 = randint(1, 20)
            lvlm = int(m_raid[ctx.author.id].lvl / 10)
            prec = int(m_raid[ctx.author.id].status['prec'] / 2)
            chance_monster = d20 + lvlm + prec

            # player chance
            d16 = randint(1, 16)
            lvlp = int(p_raid[ctx.author.id].lvl / 10)
            agi = int(p_raid[ctx.author.id].status['agi'] / 3)
            chance_player = d16 + lvlp + agi

            if p_raid[ctx.author.id].effects is not None:
                if "hold" in p_raid[ctx.author.id].effects.keys():
                    if p_raid[ctx.author.id].effects["hold"]["turns"] > 0:
                        chance_player = 0
                if "stun" in p_raid[ctx.author.id].effects.keys():
                    if p_raid[ctx.author.id].effects["stun"]["turns"] > 0:
                        chance_player = 0
                if "gelo" in p_raid[ctx.author.id].effects.keys():
                    if p_raid[ctx.author.id].effects["gelo"]["turns"] > 0:
                        chance_player = 0

            evasion[ctx.author.id][1][1] = False if chance_monster > chance_player else True
            if evasion[ctx.author.id][1][1] and evasion[ctx.author.id][1][0] > 1:
                chance_player, evasion[ctx.author.id][1][1] = 0, False
            if not evasion[ctx.author.id][1][1]:
                evasion[ctx.author.id][1][0] = 0

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill is None:
                chance_monster, chance_player = True, False

            if chance_monster > chance_player:
                m_raid[ctx.author.id] = await p_raid[ctx.author.id].damage(ctx, m_raid[ctx.author.id], skill, atk)
            else:

                if evasion[ctx.author.id][1][1]:
                    evasion[ctx.author.id][1][0] += 1

                embed = discord.Embed(
                    description=f"`{ctx.author.name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=f"{self.db_monster[ctx.author.id]['name']}",
                                 icon_url=f"{self.db_monster[ctx.author.id]['img']}")
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

        # calculo de xp
        perc = 0

        for xp_now in xp_tot[ctx.author.id]:
            test = xp_now[1] - 5 < self.db_player[ctx.author.id]['level'] < xp_now[1] + 5
            xpn = xp_now[0] if test else 1
            xp, lp, lm = xpn, self.db_player[ctx.author.id]['level'], xp_now[1]
            bonus = abs(0.5 * (self.db_player[ctx.author.id]['level'] - xp_now[1]))
            perc += xp if lp - lm <= 0 else xp + bonus if test else xp

        data_xp = calc_xp(self.db_player[ctx.author.id]['xp'], self.db_player[ctx.author.id]['level'])

        if self.db_player[ctx.author.id]['xp'] < 32:
            xpm = data_xp[2]
            xpr = xpm
        else:
            if 1 < self.db_player[ctx.author.id]['level'] < 7:
                percent = [randint(50, 75), randint(40, 60), randint(30, 55), randint(25, 45), randint(20, 40)]
                xpm = data_xp[1] - data_xp[2]
                xpr = int(xpm / 100 * percent[self.db_player[ctx.author.id]['level'] - 2])
            else:
                xpm = data_xp[1] - data_xp[2]
                xpr = int(xpm / 100 * perc)
        if xpr < xpm / 100 * 1:
            xpr = int(xpm / 100 * 1)

        xp_reward = [int(xpr + xpr * 0.5), int(xpr), int(xpr * 0.5)]

        # chance de drop
        change = randint(1, 100) + raid_rank[ctx.author.id]

        # depois da raid
        if raid_rank[ctx.author.id] <= 0:
            if not xp_off[ctx.author.id]:
                await self.bot.data.add_xp(ctx, xp_reward[2])
            embed = discord.Embed(
                description=f"`{ctx.author.name.upper()} PERDEU!`",
                color=0x000000
            )
            img = "https://media1.tenor.com/images/09b085a6b0b33a9a9c8529a3d2ee1914/tenor.gif?itemid=5648908"
            embed.set_thumbnail(url=f"{img}")
            embed.set_author(name=f"{self.db_monster[ctx.author.id]['name']}",
                             icon_url=f"{self.db_monster[ctx.author.id]['img']}")
            await ctx.send(embed=embed)

        else:
            # premiação
            if data['rpg']['vip']:
                await self.bot.data.add_xp(ctx, xp_reward[0])
            else:
                await self.bot.data.add_xp(ctx, xp_reward[1])
            answer_ = await self.bot.db.add_money(ctx, money[ctx.author.id], True)
            msg = f"`{ctx.author.name.upper()} GANHOU!` {answer_}"
            embed = discord.Embed(description=msg, color=0x000000)
            img = "https://media1.tenor.com/images/a39aa52e78dfdc01934dd2b00c1b2a6e/tenor.gif?itemid=12772532"
            embed.set_thumbnail(url=f"{img}")
            embed.set_author(name=f"{self.db_monster[ctx.author.id]['name']}",
                             icon_url=f"{self.db_monster[ctx.author.id]['img']}")
            await ctx.send(embed=embed)

            if change < 75:
                if data['rpg']['vip']:
                    reward = [choice(self.db_monster[ctx.author.id]['reward']) for _ in range(8)]
                else:
                    reward = [choice(self.db_monster[ctx.author.id]['reward']) for _ in range(4)]

                raid_reward = ["soul_crystal_of_love", "soul_crystal_of_love", "soul_crystal_of_love",
                               "soul_crystal_of_hope", "soul_crystal_of_hope", "soul_crystal_of_hope",
                               "soul_crystal_of_hate", "soul_crystal_of_hate", "soul_crystal_of_hate",
                               "fused_diamond", "fused_diamond", "fused_ruby", "fused_ruby",
                               "fused_sapphire", "fused_sapphire", "fused_emerald", "fused_emerald",
                               "unsealed_stone", "melted_artifact"]

                msg = "\n"

                if raid_rank[ctx.author.id] >= 5:
                    reward.append(choice(raid_reward))
                    msg += "🎊 **PARABENS** 🎉│`Ganhou` **+1** `item especial por matar` **5** `monstros`\n"

                if raid_rank[ctx.author.id] >= 10:
                    reward.append(choice(raid_reward))
                    msg += "🎊 **PARABENS** 🎉│`Ganhou` **+1** `item especial por matar` **10** `monstros`\n"

                if raid_rank[ctx.author.id] >= 15:
                    reward.append(choice(raid_reward))
                    msg += "🎊 **PARABENS** 🎉│`Ganhou` **+1** `item especial por matar` **15** `monstros`\n"

                if raid_rank[ctx.author.id] >= 20:
                    reward.append(choice(raid_reward))
                    msg += "🎊 **PARABENS** 🎉│`Ganhou` **+1** `item especial por matar` **20** `monstros`\n"

                if raid_rank[ctx.author.id] >= 25:
                    reward.append(choice(raid_reward))
                    msg += "🎊 **PARABENS** 🎉│`Ganhou` **+1** `item especial por matar` **25** `monstros`\n"

                if raid_rank[ctx.author.id] >= 30:
                    reward.append(choice(raid_reward))
                    msg += "🎊 **PARABENS** 🎉│`Ganhou` **+1** `item especial por matar` **30** `monstros`\n"

                if self.db_player[ctx.author.id]['level'] > 25:
                    bonus = ['stone_crystal_white', 'stone_crystal_red', 'stone_crystal_green',
                             'stone_crystal_blue', 'stone_crystal_yellow']

                    if data['rpg']['vip']:
                        reward[0] = choice(bonus)
                        reward[1] = choice(bonus)
                        reward[2] = choice(bonus)
                        reward[3] = choice(bonus)

                    else:
                        reward[0] = choice(bonus)
                        reward[1] = choice(bonus)

                if change < 50:
                    if data['rpg']['vip']:
                        reward.append(choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal']))
                        reward.append(choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal']))
                    else:
                        reward.append(choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal']))

                response = await self.bot.db.add_reward(ctx, reward, True)
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                               f'{response}\n{msg}')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if change < 10 and raid_rank[ctx.author.id] > 0 and self.db_player[ctx.author.id]['level'] > 25:

            equips_list = list()
            for ky in self.bot.config['equips'].keys():
                for k, v in self.bot.config['equips'][ky].items():
                    equips_list.append((k, v))

            list_items = []
            for i_, amount in self.w_s.items():
                list_items += [i_] * amount
            armor_or_shield = choice(list_items)

            try:
                update['rpg']['items'][armor_or_shield] += 1
            except KeyError:
                update['rpg']['items'][armor_or_shield] = 1

            rew = None
            for i in equips_list:
                if i[0] == armor_or_shield:
                    rew = i[1]

            if rew is not None:
                img = choice(git)
                embed = discord.Embed(color=self.bot.color)
                embed.set_image(url=img)
                await ctx.send(embed=embed)
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ESPADA/ESCUDO** ✨\n'
                               f'{rew["icon"]} `1 {rew["name"]}` **{rew["rarity"]}**')

        if raid_rank[ctx.author.id] > 0:
            if raid_rank[ctx.author.id] > update['user']['raid']:
                update['user']['raid'] = raid_rank[ctx.author.id]
                await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 `VOCÊ CONSEGUIU MATAR:` "
                               f"**{raid_rank[ctx.author.id]}** `MONSTROS!`\n **ESSE É SEU NOVO RECORD!** "
                               f"`APROVEITE E OLHE O COMANDO:` **ASH TOP RAID**")
            else:
                await ctx.send(f"<:confirmed:721581574461587496>│`VOCÊ CONSEGUIU MATAR:` "
                               f"**{raid_rank[ctx.author.id]}** `MONSTROS!`")

        if raid_rank[ctx.author.id] >= 10:
            try:
                update['inventory']['boss_key'] += 1
            except KeyError:
                update['inventory']['boss_key'] = 1
            await ctx.send(f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Por matar` **10+** `monstros,"
                           f" voce dropou` ✨ <:bosskey:766048658470600714> ✨ `1` **Boss Key** "
                           f"`adicionando ao seu inventario o item com sucesso...`")

        if ctx.author.id in self.bot.batalhando:
            self.bot.batalhando.remove(ctx.author.id)
        await self.bot.db.update_data(data, update, 'users')

        if p_raid[ctx.author.id].soulshot[0]:
            query = {"_id": 0, "user_id": 1, "rpg": 1}
            data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
            query_user = {"$set": {}}
            cc = str(data_user['rpg']["equipped_items"]['consumable'])
            if cc is not None:
                if cc in data_user['rpg']['items'].keys():
                    if (p_raid[ctx.author.id].soulshot[1] - 1) < 1:
                        query_user["$unset"] = dict()
                        query_user["$unset"][f"rpg.items.{cc}"] = ""
                        query_user["$set"]["rpg.equipped_items.consumable"] = None
                    else:
                        _amount = p_raid[ctx.author.id].soulshot[1]
                        query_user["$set"][f"rpg.items.{cc}"] = _amount if _amount == 0 else _amount - 1
                else:
                    query_user["$set"]["rpg.equipped_items.consumable"] = None
                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

        _class = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_class]
        percent = calc_xp(int(_db_class['xp']), int(_db_class['level']))  # XP / LEVEL
        if _db_class['xp'] < 32:
            new_xp = f"{_db_class['xp']} / {percent[2]} | {percent[0] * 2} / 100%"
        else:
            new_xp = f"{_db_class['xp'] - percent[2]} / {percent[1] - percent[2]} | {percent[0] * 2} / 100%"
        text = f"**XP:** {new_xp}\n`{'█' * percent[0]}{'-' * (50 - percent[0])}`"
        embed = discord.Embed(color=self.bot.color, description=text)
        await ctx.send(embed=embed, delete_after=5.0)

        if p_raid[ctx.author.id].status['hp'] <= 0:  # jogador 1 ganhou
            await self.bot.data.add_sts(ctx.author, ['raid_total', 'raid_max'])
        else:  # ia ganhou
            await self.bot.data.add_sts(ctx.author, ['raid_total', 'raid_lose'])


def setup(bot):
    bot.add_cog(Raid(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mRAID\033[1;32m foi carregado com sucesso!\33[m')
