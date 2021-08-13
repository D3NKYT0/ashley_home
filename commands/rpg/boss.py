import discord

from asyncio import sleep
from discord.ext import commands
from random import randint, choice
from resources.entidade import Entity
from resources.check import check_it
from resources.db import Database
from resources.img_edit import calc_xp
from datetime import datetime

evasion = {}
player = {}
monster = {}


class BossSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=60))
    @commands.command(name='boss', aliases=['chefe', 'b', 'raid', 'rd'])
    async def boss(self, ctx):
        """Comando usado pra batalhar no rpg da ashley
        Use ash boss"""
        global player, monster, evasion
        evasion[ctx.author.id] = [[0, False], [0, False]]

        _anti_game = False

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

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

        if not self.bot.boss_live:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`ATUALMENTE NAO TEM BOSS VIVO!`')
            return await ctx.send(embed=embed)

        update['inventory']['coins'] -= ct
        self.bot.batalhando.append(ctx.author.id)

        if ctx.author.id not in self.bot.boss_players.keys():
            self.bot.boss_players[ctx.author.id] = {"hpt": 0, "hit": 0, "crit": 0, "score": 0, "dano": 0, "eff": 0}

        await self.bot.db.update_data(data, update, 'users')

        # configuração do player
        set_value = ["shoulder", "breastplate", "gloves", "leggings", "boots"]
        db_player = data['rpg']
        db_player["img"] = ctx.author.avatar_url_as(format="png")
        db_player['name'] = ctx.author.name
        db_player["pdef"] = 0
        db_player["mdef"] = 0
        db_player["_id"] = ctx.author.id

        _class = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_class]
        db_player["xp"] = _db_class["xp"]
        db_player["level"] = _db_class["level"]

        soul, amount = False, 0
        if data['rpg']["equipped_items"]['consumable'] is not None:
            if 'soushot' in data['rpg']["equipped_items"]['consumable']:
                soul = True
                amount += 1
                if data['rpg']["equipped_items"]['consumable'] in data['rpg']['items'].keys():
                    amount += data['rpg']['items'][data['rpg']["equipped_items"]['consumable']]
        db_player["soulshot"] = [soul, amount]

        set_e = list()

        # bonus status player
        eq = dict()
        for ky in self.bot.config["equips"].keys():
            for kk, vv in self.bot.config["equips"][ky].items():
                eq[kk] = vv

        for k in db_player["status"].keys():
            try:
                db_player["status"][k] += self.bot.config["skills"][db_player['class']]['modifier'][k]
                if db_player['level'] > 25:
                    db_player["status"][k] += self.bot.config["skills"][db_player['class_now']]['modifier'][k]
                if db_player['level'] > 49:
                    db_player["status"][k] += self.bot.config["skills"][db_player['class_now']]['modifier_50'][k]
                if db_player['level'] > 79:
                    db_player["status"][k] += self.bot.config["skills"][db_player['class_now']]['modifier_80'][k]
            except KeyError:
                pass

        for c in db_player['equipped_items'].keys():
            if db_player['equipped_items'][c] is None:
                continue

            if c in set_value:
                set_e.append(str(c))

            db_player["pdef"] += eq[db_player['equipped_items'][c]]['pdef']
            db_player["mdef"] += eq[db_player['equipped_items'][c]]['mdef']
            for name in db_player["status"].keys():
                try:
                    db_player["status"][name] += eq[db_player['equipped_items'][c]]['modifier'][name]
                except KeyError:
                    pass

        for kkk in self.bot.config["set_equips"].values():
            if kkk['set'] == set_e:
                for name in db_player["status"].keys():
                    try:
                        db_player["status"][name] += kkk['modifier'][name]
                    except KeyError:
                        pass
                db_player["pdef"] += kkk["pdef"]
                db_player["mdef"] += kkk["mdef"]

        # criando as entidades...

        if ctx.author.id in player.keys():
            del player[ctx.author.id]

        player[ctx.author.id] = Entity(db_player, True)
        monster[ctx.author.id] = self.bot.boss_now
        if monster[ctx.author.id].status['hp'] <= 0:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`O BOSS JÁ ESTA MORTO!`')
            if ctx.author.id in self.bot.batalhando:
                self.bot.batalhando.remove(ctx.author.id)
            return await ctx.send(embed=embed)

        # durante a batalha
        while not self.bot.is_closed():

            # -----------------------------------------------------------------------------
            if player[ctx.author.id].status['hp'] <= 0 or monster[ctx.author.id].status['hp'] <= 0:
                break

            skill = await player[ctx.author.id].turn([monster[ctx.author.id].status, monster[ctx.author.id].rate,
                                                      monster[ctx.author.id].name, monster[ctx.author.id].lvl],
                                                     self.bot, ctx)

            if skill == "BATALHA-CANCELADA":
                _anti_game = True
                player[ctx.author.id].status['hp'] = 0

            if player[ctx.author.id].status['hp'] <= 0 or monster[ctx.author.id].status['hp'] <= 0:
                break
            # -----------------------------------------------------------------------------

            if skill == "COMANDO-CANCELADO":
                if ctx.author.id in self.bot.batalhando:
                    self.bot.batalhando.remove(ctx.author.id)
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito` '
                                      '**COMANDO CANCELADO**')

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            atk = int(player[ctx.author.id].status['atk'])

            # player chance
            d20 = randint(1, 20)
            lvlp = int(player[ctx.author.id].lvl / 10)
            prec = int(player[ctx.author.id].status['prec'] / 2)
            chance_player = d20 + lvlp + prec

            # monster chance
            d16 = randint(1, 16)
            lvlm = int(monster[ctx.author.id].lvl / 10)
            agi = int(monster[ctx.author.id].status['agi'] / 3)
            chance_monster = d16 + lvlm + agi

            if monster[ctx.author.id].effects is not None:
                if "gelo" in monster[ctx.author.id].effects.keys():
                    if monster[ctx.author.id].effects["gelo"]["turns"] > 0:
                        if player[ctx.author.id].soulshot[0] and player[ctx.author.id].soulshot[1] > 1:
                            chance_monster = 0
                if "stun" in monster[ctx.author.id].effects.keys():
                    if monster[ctx.author.id].effects["stun"]["turns"] > 0:
                        if player[ctx.author.id].soulshot[0] and player[ctx.author.id].soulshot[1] > 1:
                            chance_monster = 0
                if "hold" in monster[ctx.author.id].effects.keys():
                    if monster[ctx.author.id].effects["hold"]["turns"] > 0:
                        chance_monster = 0

            evasion[ctx.author.id][0][1] = False if chance_player > chance_monster else True
            if evasion[ctx.author.id][0][1] and evasion[ctx.author.id][0][0] > 1:
                chance_monster, evasion[ctx.author.id][0][1] = 0, False
            if not evasion[ctx.author.id][0][1]:
                evasion[ctx.author.id][0][0] = 0

            _SK = True if type(skill) is str else False
            skill_name = skill if _SK else skill['name']

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill_name == "CURA":
                chance_player, chance_monster = True, False

            if chance_player > chance_monster:
                player[ctx.author.id] = await monster[ctx.author.id].damage(ctx, player[ctx.author.id], skill, atk)
            else:

                if evasion[ctx.author.id][0][1]:
                    evasion[ctx.author.id][0][0] += 1

                embed = discord.Embed(
                    description=f"`{monster[ctx.author.id].name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=f"{self.bot.boss_now.name}", icon_url=f"{self.bot.boss_now.img}")
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            # -----------------------------------------------------------------------------
            if player[ctx.author.id].status['hp'] <= 0 or monster[ctx.author.id].status['hp'] <= 0:
                break

            skill = await monster[ctx.author.id].turn(monster[ctx.author.id].status['hp'], self.bot, ctx)

            if skill == "BATALHA-CANCELADA":
                _anti_game = True
                player[ctx.author.id].status['hp'] = 0

            if player[ctx.author.id].status['hp'] <= 0 or monster[ctx.author.id].status['hp'] <= 0:
                break
            # -----------------------------------------------------------------------------

            if skill == "COMANDO-CANCELADO":
                if ctx.author.id in self.bot.batalhando:
                    self.bot.batalhando.remove(ctx.author.id)
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito` '
                                      '**COMANDO CANCELADO**')

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            atk_bonus = monster[ctx.author.id].status['atk'] * 0.5 if player[ctx.author.id].lvl > 25 else \
                monster[ctx.author.id].status['atk'] * 0.25
            atk = int(monster[ctx.author.id].status['atk'] + atk_bonus)

            # monster chance
            d20 = randint(1, 20)
            lvlm = int(monster[ctx.author.id].lvl / 10)
            prec = int(monster[ctx.author.id].status['prec'] / 2)
            chance_monster = d20 + lvlm + prec

            # player chance
            d16 = randint(1, 16)
            lvlp = int(player[ctx.author.id].lvl / 10)
            agi = int(player[ctx.author.id].status['agi'] / 3)
            chance_player = d16 + lvlp + agi

            if player[ctx.author.id].effects is not None:
                if "gelo" in player[ctx.author.id].effects.keys():
                    if player[ctx.author.id].effects["gelo"]["turns"] > 0:
                        chance_player = 0
                if "stun" in player[ctx.author.id].effects.keys():
                    if player[ctx.author.id].effects["stun"]["turns"] > 0:
                        chance_player = 0
                if "hold" in player[ctx.author.id].effects.keys():
                    if player[ctx.author.id].effects["hold"]["turns"] > 0:
                        chance_player = 0

            evasion[ctx.author.id][1][1] = False if chance_monster > chance_player else True
            if evasion[ctx.author.id][1][1] and evasion[ctx.author.id][1][0] > 1:
                chance_player, evasion[ctx.author.id][1][1] = 0, False
            if not evasion[ctx.author.id][1][1]:
                evasion[ctx.author.id][1][0] = 0

            _SK = True if type(skill) is str else False
            skill_name = skill if _SK else skill['name']

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill_name == "CURA":
                chance_monster, chance_player = True, False

            if chance_monster > chance_player:
                monster[ctx.author.id] = await player[ctx.author.id].damage(ctx, monster[ctx.author.id], skill, atk)
            else:

                if evasion[ctx.author.id][1][1]:
                    evasion[ctx.author.id][1][0] += 1

                embed = discord.Embed(
                    description=f"`{ctx.author.name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=db_player['name'], icon_url=db_player['img'])
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

        # depois da batalha
        if monster[ctx.author.id].status['hp'] > 0:
            embed = discord.Embed(
                description=f"`{ctx.author.name.upper()} PERDEU!`",
                color=0x000000
            )
            img = "https://media1.tenor.com/images/09b085a6b0b33a9a9c8529a3d2ee1914/tenor.gif?itemid=5648908"
            embed.set_thumbnail(url=f"{img}")
            embed.set_author(name=db_player['name'], icon_url=db_player['img'])
            await ctx.send(embed=embed)
        else:
            db_monster = monster[ctx.author.id].db
            _din = await self.bot.db.add_money(ctx, randint(db_monster['ethernya'] // 4, db_monster['ethernya']), True)
            embed = discord.Embed(description=f"`{ctx.author.name.upper()} GANHOU!` {_din}", color=0x000000)
            img = "https://media1.tenor.com/images/a39aa52e78dfdc01934dd2b00c1b2a6e/tenor.gif?itemid=12772532"
            embed.set_thumbnail(url=f"{img}")
            embed.set_author(name=db_player['name'], icon_url=db_player['img'])

            # --------======== TEMPO DE ESPERA ========--------
            #             CALCULO DE XP - DO BOSS
            # --------======== ............... ========--------

            xp, lp, lm = db_monster['xp'], db_player['level'], db_monster['level']
            perc = xp if lp - lm <= 0 else xp + abs(0.15 * (db_player['level'] - db_monster['level']))
            data_xp = calc_xp(db_player['xp'], db_player['level'])
            if db_player['xp'] < 32:
                xpm = data_xp[2]
                xpr = xpm
            else:
                if db_player['level'] > 40:
                    xpm = data_xp[1] - data_xp[2]
                    xpr = (xpm // 100) * (perc // 4)
                else:
                    xpm = data_xp[1] - data_xp[2]
                    xpr = (xpm // 100) * perc
            if xpr < xpm / 100 * 1:
                xpr = int(xpm / 100 * 1)
            xp_reward = [int(xpr + xpr * 0.15), int(xpr), int(xpr * 0.15)]
            _xp = choice([0, 1, 2])
            await self.bot.data.add_xp(ctx, xp_reward[_xp])
            await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            self.bot.batalhando.remove(ctx.author.id)

        if player[ctx.author.id].soulshot[0]:
            query = {"_id": 0, "user_id": 1, "rpg": 1}
            data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
            query_user, cc = {"$set": {}}, str(data_user['rpg']["equipped_items"]['consumable'])
            if cc is not None:
                if cc in data_user['rpg']['items'].keys():
                    if (player[ctx.author.id].soulshot[1] - 1) < 1:
                        query_user["$unset"] = dict()
                        query_user["$unset"][f"rpg.items.{cc}"] = ""
                        query_user["$set"]["rpg.equipped_items.consumable"] = None
                    else:
                        _amount = player[ctx.author.id].soulshot[1]
                        query_user["$set"][f"rpg.items.{cc}"] = _amount if _amount == 0 else _amount - 1
                else:
                    query_user["$set"]["rpg.equipped_items.consumable"] = None
                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

        if not _anti_game:
            _data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            try:
                del _data['cooldown'][str(ctx.command)]
            except KeyError:
                pass
            await self.bot.db.update_data(_data, _data, 'users')


def setup(bot):
    bot.add_cog(BossSystem(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mBOSS_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
