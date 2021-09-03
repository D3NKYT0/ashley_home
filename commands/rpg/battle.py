import discord

import time as date
from asyncio import sleep
from discord.ext import commands
from random import randint, choice
from resources.fight import Entity, Ext
from resources.check import check_it
from resources.db import Database
from resources.img_edit import calc_xp
from resources.utility import include
from datetime import datetime
player, monster, extension = {}, {}, Ext()
git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.w_s = self.bot.config['attribute']['chance_weapon']
        self.e = self.bot.d_event
        self.xp_off = {}

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='battle', aliases=['batalha', 'batalhar', 'bt'])
    async def battle(self, ctx, moon=None):
        """Comando usado pra batalhar no rpg da ashley
        Use ash battle"""
        global player, monster

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        mini_boss = False if moon is False or moon != "moon" else True

        if ctx.author.id in self.bot.desafiado:
            msg = "<:alert:739251822920728708>│`Você está sendo desafiado/desafiando para um PVP!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.jogando:
            msg = "<:alert:739251822920728708>│`Você está jogando, aguarde para quando você estiver livre!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if not data['rpg']['active']:
            msg = '<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`'
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
                msg = f'<:negate:721581573396496464>│`VOCE PRECISA DE + DE {ct} FICHAS PARA BATALHAR!`\n' \
                      f'**OBS:** `USE O COMANDO` **ASH SHOP** `PARA COMPRAR FICHAS!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        except KeyError:
            msg = '<:negate:721581573396496464>│`VOCE NÃO TEM FICHA!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        update['inventory']['coins'] -= ct
        if update['inventory']['coins'] < 1:
            del update['inventory']['coins']

        if mini_boss:
            if "stone_of_moon" not in update['inventory'].keys():
                msg = '<:negate:721581573396496464>│`VOCE NÃO TEM STONE OF MOON NO SEU INVENTARIO!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            update['inventory']['stone_of_moon'] -= 1
            if update['inventory']['stone_of_moon'] < 1:
                del update['inventory']['stone_of_moon']

        self.bot.batalhando.append(ctx.author.id)
        self.xp_off[ctx.author.id] = False
        await self.bot.db.update_data(data, update, 'users')

        # configuração do player e monster
        db_player = extension.set_player(ctx.author, data)
        db_monster = extension.set_monster(db_player, mini_boss)

        # criando as entidades...
        if ctx.author.id in player.keys():
            del player[ctx.author.id]
        if ctx.author.id in monster.keys():
            del monster[ctx.author.id]

        player[ctx.author.id] = Entity(db_player, True)
        monster[ctx.author.id] = Entity(db_monster, False, is_mini_boss=mini_boss)

        # durante a batalha
        while not self.bot.is_closed():

            # -----------------------------------------------------------------------------
            if player[ctx.author.id].status['hp'] <= 0 or monster[ctx.author.id].status['hp'] <= 0:
                break

            skill = await player[ctx.author.id].turn(ctx, ctx.author, monster[ctx.author.id])

            if skill == "BATALHA-CANCELADA":
                self.xp_off[ctx.author.id] = True
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

            # player chance
            d20 = randint(1, 20)
            lvlp = int(player[ctx.author.id].level / 10)
            prec = int(player[ctx.author.id].status['prec'] / 2)
            chance_player = d20 + lvlp + prec

            # monster chance
            d16 = randint(1, 16)
            lvlm = int(monster[ctx.author.id].level / 10)
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

            if monster[ctx.author.id].evasion >= 3:
                chance_monster, monster[ctx.author.id].evasion = 0, 0

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill is None:
                chance_player, chance_monster = 100, 0

            if chance_player > chance_monster:
                player[ctx.author.id] = await monster[ctx.author.id].damage(ctx, player[ctx.author.id], skill)
                if skill != "PASS-TURN-MP" or skill != "PASS-TURN-HP" or skill is not None:
                    monster[ctx.author.id].evasion = 0
            else:
                monster[ctx.author.id].evasion += 1

                embed = discord.Embed(
                    description=f"`{monster[ctx.author.id].name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url="https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=db_monster['name'], icon_url=db_monster['img'])
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            # -----------------------------------------------------------------------------
            if player[ctx.author.id].status['hp'] <= 0 or monster[ctx.author.id].status['hp'] <= 0:
                break

            skill = await monster[ctx.author.id].turn(ctx, ctx.author, player[ctx.author.id])

            if skill == "BATALHA-CANCELADA":
                player[ctx.author.id].status['hp'] = 0
                self.xp_off[ctx.author.id] = True

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

            # monster chance
            d20 = randint(1, 20)
            lvlm = int(monster[ctx.author.id].level / 10)
            prec = int(monster[ctx.author.id].status['prec'] / 2)
            chance_monster = d20 + lvlm + prec

            # player chance
            d16 = randint(1, 16)
            lvlp = int(player[ctx.author.id].level / 10)
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

            if player[ctx.author.id].evasion >= 3:
                chance_player, player[ctx.author.id].evasion = 0, 0

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill is None:
                chance_monster, chance_player = 100, 0

            if chance_monster > chance_player:
                monster[ctx.author.id] = await player[ctx.author.id].damage(ctx, monster[ctx.author.id], skill)
                if skill != "PASS-TURN-MP" or skill != "PASS-TURN-HP" or skill is not None:
                    player[ctx.author.id].evasion = 0
            else:
                player[ctx.author.id].evasion += 1

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

        # calculo de xp
        xp, lp = db_monster['xp'], db_player['level']
        lm = db_monster['level']
        perc = xp if lp - lm <= 0 else xp + abs(0.15 * (db_player['level'] - db_monster['level']))
        data_xp = calc_xp(db_player['xp'], db_player['level'])

        # bonus de XP durante evento!
        if self.bot.event_special and perc < 10:
            perc = 10

        # bonus de XP por estar em provincia
        if data['config']['provinces'] is not None:
            perc += 10

        if db_player['xp'] < 32:
            xpm = data_xp[2]
            xpr = xpm

        else:
            if 1 < db_player['level'] < 7:
                percent = [randint(50, 75), randint(40, 60), randint(30, 55), randint(25, 45), randint(20, 40)]
                xpm = data_xp[1] - data_xp[2]
                xpr = int(xpm / 100 * percent[db_player['level'] - 2])

            else:
                xpm = data_xp[1] - data_xp[2]
                xpr = int(xpm / 100 * perc)

        if xpr < xpm / 100 * 1:
            xpr = int(xpm / 100 * 1)

        xp_reward = [int(xpr + xpr * 0.5), int(xpr), int(xpr * 0.5)]

        # chance de drop
        change = randint(1, 100)

        # depois da batalha
        if monster[ctx.author.id].status['hp'] > 0:
            if not self.xp_off[ctx.author.id]:
                await self.bot.data.add_xp(ctx, xp_reward[2])
            embed = discord.Embed(
                description=f"`{ctx.author.name.upper()} PERDEU!`",
                color=0x000000
            )
            img = "https://media1.tenor.com/images/09b085a6b0b33a9a9c8529a3d2ee1914/tenor.gif?itemid=5648908"
            embed.set_thumbnail(url=f"{img}")
            embed.set_author(name=db_player['name'], icon_url=db_player['img'])
            await ctx.send(embed=embed, delete_after=5.0)
        else:
            # premiação
            if data['rpg']['vip']:
                await self.bot.data.add_xp(ctx, xp_reward[0])
            else:
                await self.bot.data.add_xp(ctx, xp_reward[1])
            answer_ = await self.bot.db.add_money(ctx, db_monster['ethernya'], True)
            embed = discord.Embed(
                description=f"`{ctx.author.name.upper()} GANHOU!` {answer_}",
                color=0x000000)
            img = "https://media1.tenor.com/images/a39aa52e78dfdc01934dd2b00c1b2a6e/tenor.gif?itemid=12772532"
            embed.set_thumbnail(url=f"{img}")
            embed.set_author(name=db_player['name'], icon_url=db_player['img'])
            await ctx.send(embed=embed, delete_after=5.0)

            if change < 60 or mini_boss:
                if data['rpg']['vip']:
                    reward = [choice(db_monster['reward']) for _ in range(8)]
                else:
                    reward = [choice(db_monster['reward']) for _ in range(4)]

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

                if change < 40:
                    if data['rpg']['vip']:
                        reward.append(choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal']))
                        reward.append(choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal']))
                    else:
                        reward.append(choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal']))

                    if mini_boss:
                        reward.append(choice(['herb_red', 'herb_green', 'herb_blue']))

                if change < 15:
                    date_ = date.localtime()
                    item_event = choice(["soul_crystal_of_love", "soul_crystal_of_love", "soul_crystal_of_love",
                                         "soul_crystal_of_hope", "soul_crystal_of_hope", "soul_crystal_of_hope",
                                         "soul_crystal_of_hate", "soul_crystal_of_hate", "soul_crystal_of_hate",
                                         "fused_diamond", "fused_diamond", "fused_ruby", "fused_ruby",
                                         "fused_sapphire", "fused_sapphire", "fused_emerald", "fused_emerald",
                                         "unsealed_stone", "melted_artifact"])

                    icon, name = self.bot.items[item_event][0], self.bot.items[item_event][1]
                    awards = choice(['images/elements/medallion.gif', 'images/elements/trophy.gif'])
                    msg = f"`VOCÊ GANHOU` {icon} `{name.upper()}` ✨ **DO EVENTO DE: {self.bot.event_now}!** ✨"
                    file = discord.File(awards, filename="reward.gif")
                    embed = discord.Embed(title=msg, color=self.bot.color)
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    embed.set_thumbnail(url="attachment://reward.gif")

                    # config do evento atual.
                    if date_[0] == self.e[0] and date_[1] == self.e[1] and self.e[2][0] < date_[2] < self.e[2][1]:
                        if self.bot.event_special:
                            reward.append(item_event)
                            await ctx.send(file=file, embed=embed)

                    if mini_boss:
                        reward.append(choice(['armor_divine', 'enchant_divine', 'feather_white',
                                              'feather_gold', 'feather_black']))

                response = await self.bot.db.add_reward(ctx, reward)
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                               f'{response}', delete_after=5.0)

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if change <= 10 and player[ctx.author.id].status['hp'] > 0:

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
                msg = f'<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU` ✨ **ESPADA/ESCUDO** ✨\n' \
                      f'{rew["icon"]} `1 {rew["name"]}` **{rew["rarity"]}**'
                embed = discord.Embed(color=self.bot.color, description=msg)
                embed.set_thumbnail(url=img)
                await ctx.send(embed=embed, delete_after=30.0)

                if "the_seven_lost_souls" in update['rpg']['quests'].keys():
                    _QUEST = update['rpg']['quests']["the_seven_lost_souls"]
                    souls = {
                        "assassin": 1,
                        "necromancer": 2,
                        "paladin": 3,
                        "priest": 4,
                        "warlock": 5,
                        "warrior": 6,
                        "wizard": 7
                    }
                    if _QUEST["status"] == "in progress" and change <= 50 and data['config']['provinces'] is not None:
                        if include(rew["name"], souls.keys()):
                            quest_item = souls[rew["name"].split()[0]]
                            if quest_item not in update['rpg']['quests']["the_seven_lost_souls"]["souls"]:
                                update['rpg']['quests']["the_seven_lost_souls"]["souls"].append(quest_item)
                                await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                               f'✨ **[The 7 Lost Souls]** ✨')
                    elif _QUEST["status"] == "completed" and change <= 50 and data['config']['provinces'] is not None:
                        quest_item = choice(["assassin_gem", "necromancer_gem", "paladin_gem", "priest_gem",
                                             "warlock_gem", "warrior_gem", "wizard_gem"])
                        try:
                            update['inventory'][quest_item] += 1
                        except KeyError:
                            update['inventory'][quest_item] = 1
                        icon, name = self.bot.items[quest_item][0], self.bot.items[quest_item][1]
                        await ctx.send(
                            f'<a:fofo:524950742487007233>│`POR COMPLETAR A QUEST` ✨ **[The 3 Holy Scrolls]** ✨\n'
                            f'`POR BATALHAR VOCE GANHOU:` {icon} **1** `{name.UPPER()}`')

        if change <= 25 and player[ctx.author.id].status['hp'] > 0:

            equips_list = list()
            for ky in self.bot.config['equips'].keys():
                for k, v in self.bot.config['equips'][ky].items():
                    equips_list.append((k, v))

            sb = choice(['summon_box_sr', 'summon_box_sr', 'summon_box_sr', 'summon_box_sr', 'summon_box_sr',
                         'summon_box_ur', 'summon_box_ur', 'summon_box_ur', 'summon_box_secret'])

            try:
                update['rpg']['items'][sb] += 1
            except KeyError:
                update['rpg']['items'][sb] = 1

            rew = None
            for i in equips_list:
                if i[0] == sb:
                    rew = i[1]

            if rew is not None:
                await ctx.send(f'<a:fofo:524950742487007233>│`VOCÊ TAMBEM GANHOU UM` ✨ **CONSUMABLE** ✨\n'
                               f'{rew["icon"]} `1 {rew["name"]}` **{rew["rarity"]}**', delete_after=5.0)

        player_life = player[ctx.author.id].status['hp'] > 0
        if mini_boss and "the_eight_evils_of_the_moon" in update['rpg']['quests'].keys() and player_life:
            _QUEST = update['rpg']['quests']["the_eight_evils_of_the_moon"]
            if _QUEST["status"] == "in progress":
                if db_monster["name"] not in update['rpg']['quests']["the_eight_evils_of_the_moon"]["mini-boss"]:
                    update['rpg']['quests']["the_eight_evils_of_the_moon"]["mini-boss"].append(db_monster["name"])
                    await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                   f'✨ **[The 8 Evils of the Moon]** ✨')

        if "the_three_sacred_scrolls" in update['rpg']['quests'].keys() and player_life:
            _QUEST = update['rpg']['quests']["the_three_sacred_scrolls"]
            quest_item = choice(["lost_parchment", "royal_parchment", "sages_scroll"])
            if _QUEST["status"] == "in progress" and change <= 15 and data['config']['provinces'] is not None:
                if quest_item not in update['rpg']['quests']["the_three_sacred_scrolls"]["scroll"]:
                    update['rpg']['quests']["the_three_sacred_scrolls"]["scroll"].append(quest_item)
                    await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                   f'✨ **[The 3 Holy Scrolls]** ✨')
            elif _QUEST["status"] == "completed" and change <= 15 and data['config']['provinces'] is not None:
                try:
                    update['inventory'][quest_item] += 1
                except KeyError:
                    update['inventory'][quest_item] = 1
                icon, name = self.bot.items[quest_item][0], self.bot.items[quest_item][1]
                await ctx.send(f'<a:fofo:524950742487007233>│`POR COMPLETAR A QUEST` ✨ **[The 3 Holy Scrolls]** ✨\n'
                               f'`POR BATALHAR VOCE GANHOU:` {icon} **1** `{name.UPPER()}`')

        if change <= 25 and player[ctx.author.id].status['hp'] > 0 and mini_boss:
            msg_return = False
            craft = choice(["assassin_celestial_slayer_divine", "necromancer_celestial_staff_divine",
                            "paladin_celestial_hammer_divine", "priest_celestial_bow_divine",
                            "warlock_celestial_saint_divine", "warrior_celestial_tallum_divine",
                            "wizard_celestial_mace_divine"])

            if craft not in update["recipes"]:
                msg_return = True
                update["recipes"].append(craft)

            if msg_return:
                craft = craft.replace("_", " ").upper()
                text = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Voce liberou o craft:`\n**{craft}**"
                file = discord.File('images/elements/success.jpg', filename="success.jpg")
                embed = discord.Embed(title=text, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_image(url="attachment://success.jpg")
                await ctx.send(file=file, embed=embed)

        if change <= 25 and player[ctx.author.id].status['hp'] > 0 and mini_boss:

            try:
                update['inventory'][db_monster['quest']] += 1
            except KeyError:
                update['inventory'][db_monster['quest']] = 1

            icon, name = self.bot.items[db_monster['quest']][0], self.bot.items[db_monster['quest']][1]
            await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR GANHAR O` ✨ **QUEST ITEM** ✨\n'
                           f'{icon} **1** `{name}`')

        if ctx.author.id in self.bot.batalhando:
            self.bot.batalhando.remove(ctx.author.id)
        await self.bot.db.update_data(data, update, 'users')

        if player[ctx.author.id].soulshot[0]:
            query, query_user, cl = {"_id": 0, "user_id": 1, "rpg": 1}, {"$set": {}}, await self.bot.db.cd("users")
            data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
            cc = data_user['rpg']["equipped_items"]['consumable']
            if cc in data_user['rpg']['items'].keys():
                if (player[ctx.author.id].soulshot[1] - 1) < 1:
                    query_user["$unset"] = dict()
                    query_user["$unset"][f"rpg.items.{cc}"] = ""
                    query_user["$set"]["rpg.equipped_items.consumable"] = None
                else:
                    query_user["$set"][f"rpg.items.{cc}"] = player[ctx.author.id].soulshot[1] - 1
            else:
                query_user["$set"]["rpg.equipped_items.consumable"] = None
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

        if player[ctx.author.id].status['hp'] <= 0:  # jogador 1 ganhou
            await self.bot.data.add_sts(ctx.author, ['battle_total', 'battle_win'])
        else:  # ia ganhou
            await self.bot.data.add_sts(ctx.author, ['battle_total', 'battle_lose'])


def setup(bot):
    bot.add_cog(Battle(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mBATTLE\033[1;32m foi carregado com sucesso!\33[m')
