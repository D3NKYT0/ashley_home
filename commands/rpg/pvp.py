import discord

from asyncio import sleep, TimeoutError
from discord.ext import commands
from random import randint
from resources.entidade import Entity
from resources.check import check_it
from resources.db import Database

player_1 = {}
player_2 = {}
evasion = {}


class PVP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def config_player(self, user, data, lower_net):
        # configuração do player
        set_value = ["shoulder", "breastplate", "gloves", "leggings", "boots"]
        db_player = data['rpg']
        db_player["img"] = user.avatar_url_as(format="png")
        db_player['name'] = user.name
        db_player["pdef"] = 0
        db_player["mdef"] = 0
        db_player["_id"] = user.id

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

        db_player["lower_net"] = lower_net
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

        return db_player

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='pvp')
    async def pvp(self, ctx, member: discord.Member = None):
        """Comando usado pra ir PVP no rpg da ashley
        Use ash pvp"""
        global player_1, player_2, evasion
        evasion[ctx.author.id] = [[0, False], [0, False]]

        def check(m):
            return m.author.id == member.id and m.content.upper() in ['SIM', 'NÃO', 'S', 'N', 'NAO', 'CLARO']

        if member is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa mencionar alguem!`")
        if member.id == ctx.author.id:
            return await ctx.send("<:alert:739251822920728708>│`Você não pode ir PVP consigo mesmo!`")

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if member.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`O usuario está jogando, aguarde para quando"
                                  " ele estiver livre!`")

        if member.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`O USUARIO ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if member.id in self.bot.desafiado:
            return await ctx.send("<:alert:739251822920728708>│`O membro está sendo desafiado/desafiando para um PVP!`")

        if randint(1, 100) <= 50:
            _idp1 = ctx.author.id
            _idp2 = member.id
        else:
            _idp1 = member.id
            _idp2 = ctx.author.id

        data_idp1 = await self.bot.db.get_data("user_id", _idp1, "users")
        data_idp2 = await self.bot.db.get_data("user_id", _idp2, "users")

        if not data_idp1['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        _class1 = data_idp1["rpg"]["class_now"]
        _db_class1 = data_idp1["rpg"]["sub_class"][_class1]
        if _db_class1['level'] < 26:
            msg = '<:negate:721581573396496464>│`VOCE PRECISA ESTA NO NIVEL 26 OU MAIOR PARA IR PVP!\n' \
                  'OLHE O SEU NIVEL NO COMANDO:` **ASH SKILL**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if data_idp2 is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        if not data_idp2['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`O USUARIO DEVE USAR O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        _class2 = data_idp2["rpg"]["class_now"]
        _db_class2 = data_idp2["rpg"]["sub_class"][_class2]
        if _db_class2['level'] < 26:
            msg = '<:negate:721581573396496464>│`O USUARIO PRECISA ESTA NO NIVEL 26 OU MAIOR PARA  IR PVP!\n' \
                  'PEÇA PARA ELE OLHAR O NIVEL NO COMANDO:` **ASH SKILL**'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.desafiado.append(ctx.author.id)
        self.bot.desafiado.append(member.id)

        await ctx.send(f'<a:ash:525105075446743041>│{member.mention}, `VOCÊ RECEBEU UM DESAFIO PARA IR PVP '
                       f'COM` {ctx.author.mention} `DIGITE` **SIM** `OU` **NÃO** `PARA ACEITAR OU REGEITAR!`')
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            self.bot.desafiado.remove(ctx.author.id)
            self.bot.desafiado.remove(member.id)
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, ele(a) demorou muito pra responder:` '
                                  '**COMANDO CANCELADO**')

        if answer.content.upper() not in ['SIM', 'S', 'CLARO']:
            self.bot.desafiado.remove(ctx.author.id)
            self.bot.desafiado.remove(member.id)
            return await ctx.send(f'<:negate:721581573396496464>│{ctx.author.mention} `SEU PEDIDO FOI REJEITADO...`')

        self.bot.batalhando.append(ctx.author.id)
        self.bot.batalhando.append(member.id)
        # tirando os jogadores da lista de desafiantes
        self.bot.desafiado.remove(ctx.author.id)
        self.bot.desafiado.remove(member.id)

        if data_idp1['rpg']['lower_net'] and data_idp2['rpg']['lower_net']:
            lower_net = True
        else:
            lower_net = False

        player_1_data = self.config_player(ctx.guild.get_member(_idp1), data_idp1, lower_net)
        player_2_data = self.config_player(ctx.guild.get_member(_idp2), data_idp2, lower_net)

        # criando as entidades...
        if _idp1 in player_1.keys():
            del player_1[_idp1]
        if _idp2 in player_2.keys():
            del player_2[_idp2]

        player_1[_idp1] = Entity(player_1_data, True, True)
        player_2[_idp2] = Entity(player_2_data, True, True)

        # durante a batalha
        while not self.bot.is_closed():

            # -----------------------------------------------------------------------------
            if player_1[_idp1].status['hp'] <= 0 or player_2[_idp2].status['hp'] <= 0:
                break

            skill = await player_1[_idp1].turn([player_2[_idp2].status, player_2[_idp2].rate,
                                                player_2[_idp2].name, player_2[_idp2].lvl],
                                               self.bot, ctx, ctx.guild.get_member(_idp1))

            if skill == "BATALHA-CANCELADA":
                player_1[_idp1].status['hp'] = 0

            if player_1[_idp1].status['hp'] <= 0 or player_2[_idp2].status['hp'] <= 0:
                break
            # -----------------------------------------------------------------------------

            if skill == "COMANDO-CANCELADO":
                player_1[_idp1].status['hp'] = 0
                await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito` **COMANDO CANCELADO**')
                break

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------
            lvlp1 = int(player_1[_idp1].lvl / 10)
            lvlp2 = int(player_2[_idp2].lvl / 10)
            atk = int(player_1[_idp1].status['atk'])
            d20, d16 = randint(1, 20), randint(1, 16)
            acc = int(player_1[_idp1].status['prec'] / 2)
            dex = int(player_2[_idp2].status['agi'] / 3)
            p1_chance = d20 + lvlp1 + acc
            p2_chance = d16 + lvlp2 + dex

            if player_2[_idp2].effects is not None:
                if "gelo" in player_2[_idp2].effects.keys():
                    if player_2[_idp2].effects["gelo"]["turns"] > 0:
                        if player_1[_idp1].soulshot[0] and player_1[_idp1].soulshot[1] > 1:
                            p2_chance = 0
                if "stun" in player_2[_idp2].effects.keys():
                    if player_2[_idp2].effects["stun"]["turns"] > 0:
                        if player_1[_idp1].soulshot[0] and player_1[_idp1].soulshot[1] > 1:
                            p2_chance = 0
                if "hold" in player_2[_idp2].effects.keys():
                    if player_2[_idp2].effects["hold"]["turns"] > 0:
                        p2_chance = 0

            evasion[ctx.author.id][0][1] = False if p1_chance > p2_chance else True
            if evasion[ctx.author.id][0][1] and evasion[ctx.author.id][0][0] > 1:
                p2_chance, evasion[ctx.author.id][0][1] = 0, False
            if not evasion[ctx.author.id][0][1]:
                evasion[ctx.author.id][0][0] = 0

            _SK = True if type(skill) is str else False
            skill_name = skill if _SK else skill['name']

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill_name == "CURA":
                p1_chance, p2_chance = True, False

            if p1_chance > p2_chance:
                player_1[_idp1] = await player_2[_idp2].damage(ctx, player_1[_idp1], skill, atk)
            else:

                if evasion[ctx.author.id][0][1]:
                    evasion[ctx.author.id][0][0] += 1

                embed = discord.Embed(
                    description=f"`{player_2[_idp2].name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=player_2_data['name'], icon_url=player_2_data['img'])
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

            # -----------------------------------------------------------------------------
            if player_1[_idp1].status['hp'] <= 0 or player_2[_idp2].status['hp'] <= 0:
                break

            skill = await player_2[_idp2].turn([player_1[_idp1].status, player_1[_idp1].rate,
                                                player_1[_idp1].name, player_1[_idp1].lvl],
                                               self.bot, ctx, ctx.guild.get_member(_idp2))

            if skill == "BATALHA-CANCELADA":
                player_2[_idp2].status['hp'] = 0

            if player_1[_idp1].status['hp'] <= 0 or player_2[_idp2].status['hp'] <= 0:
                break
            # -----------------------------------------------------------------------------

            if skill == "COMANDO-CANCELADO":
                player_2[_idp2].status['hp'] = 0
                await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito` **COMANDO CANCELADO**')
                break

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------
            lvlp2 = int(player_2[_idp2].lvl / 10)
            lvlp1 = int(player_1[_idp1].lvl / 10)
            atk = int(player_2[_idp2].status['atk'])
            d20, d16 = randint(1, 20), randint(1, 16)
            acc = int(player_2[_idp2].status['prec'] / 2)
            dex = int(player_1[_idp1].status['agi'] / 3)
            p2_chance = d20 + lvlp2 + acc
            p1_chance = d16 + lvlp1 + dex

            if player_1[_idp1].effects is not None:
                if "gelo" in player_1[_idp1].effects.keys():
                    if player_1[_idp1].effects["gelo"]["turns"] > 0:
                        if player_2[_idp2].soulshot[0] and player_2[_idp2].soulshot[1] > 1:
                            p1_chance = 0
                if "stun" in player_1[_idp1].effects.keys():
                    if player_1[_idp1].effects["stun"]["turns"] > 0:
                        if player_2[_idp2].soulshot[0] and player_2[_idp2].soulshot[1] > 1:
                            p1_chance = 0
                if "hold" in player_1[_idp1].effects.keys():
                    if player_1[_idp1].effects["hold"]["turns"] > 0:
                        p1_chance = 0

            evasion[ctx.author.id][1][1] = False if p2_chance > p1_chance else True
            if evasion[ctx.author.id][1][1] and evasion[ctx.author.id][1][0] > 1:
                p1_chance, evasion[ctx.author.id][1][1] = 0, False
            if not evasion[ctx.author.id][1][1]:
                evasion[ctx.author.id][1][0] = 0

            _SK = True if type(skill) is str else False
            skill_name = skill if _SK else skill['name']

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill_name == "CURA":
                p2_chance, p1_chance = True, False

            if p2_chance > p1_chance:
                player_2[_idp2] = await player_1[_idp1].damage(ctx, player_2[_idp2], skill, atk)
            else:

                if evasion[ctx.author.id][1][1]:
                    evasion[ctx.author.id][1][0] += 1

                embed = discord.Embed(
                    description=f"`{player_1[_idp1].name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=player_1_data['name'], icon_url=player_1_data['img'])
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

        if player_1[_idp1].soulshot[0]:
            query = {"_id": 0, "user_id": 1, "rpg": 1}
            data_user = await (await self.bot.db.cd("users")).find_one({"user_id": _idp1}, query)
            query_user = {"$set": {}}
            cc = str(data_user['rpg']["equipped_items"]['consumable'])
            if cc is not None:
                if cc in data_user['rpg']['items'].keys():
                    if (player_1[_idp1].soulshot[1] - 1) < 1:
                        query_user["$unset"] = dict()
                        query_user["$unset"][f"rpg.items.{cc}"] = ""
                        query_user["$set"]["rpg.equipped_items.consumable"] = None
                    else:
                        _amount = player_1[_idp1].soulshot[1]
                        query_user["$set"][f"rpg.items.{cc}"] = _amount if _amount == 0 else _amount - 1
                else:
                    query_user["$set"]["rpg.equipped_items.consumable"] = None
                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

        if player_2[_idp2].soulshot[0]:
            query = {"_id": 0, "user_id": 1, "rpg": 1}
            data_user = await (await self.bot.db.cd("users")).find_one({"user_id": _idp2}, query)
            query_user = {"$set": {}}
            cc = str(data_user['rpg']["equipped_items"]['consumable'])
            if cc is not None:
                if cc in data_user['rpg']['items'].keys():
                    if (player_2[_idp2].soulshot[1] - 1) < 1:
                        query_user["$unset"] = dict()
                        query_user["$unset"][f"rpg.items.{cc}"] = ""
                        query_user["$set"]["rpg.equipped_items.consumable"] = None
                    else:
                        _amount = player_2[_idp2].soulshot[1]
                        query_user["$set"][f"rpg.items.{cc}"] = _amount if _amount == 0 else _amount - 1
                else:
                    query_user["$set"]["rpg.equipped_items.consumable"] = None
                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

        if player_1[_idp1].status['hp'] <= 0:
            _user = ctx.guild.get_member(_idp2)
            _user2 = ctx.guild.get_member(_idp1)
            await ctx.send(f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {_user.mention} `VOCE GANHOU!`")
            await self.bot.data.add_sts(_user2, ['pvp_lose', 'pvp_total'])
            await self.bot.data.add_sts(_user, ['pvp_win', 'pvp_total'])

        if player_2[_idp2].status['hp'] <= 0:
            _user = ctx.guild.get_member(_idp1)
            _user2 = ctx.guild.get_member(_idp2)
            await ctx.send(f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {_user.mention} `VOCE GANHOU!`")
            await self.bot.data.add_sts(_user2, ['pvp_lose', 'pvp_total'])
            await self.bot.data.add_sts(_user, ['pvp_win', 'pvp_total'])

        if ctx.author.id in self.bot.batalhando:
            self.bot.batalhando.remove(ctx.author.id)
        if member.id in self.bot.batalhando:
            self.bot.batalhando.remove(member.id)


def setup(bot):
    bot.add_cog(PVP(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mPVP\033[1;32m foi carregado com sucesso!\33[m')
