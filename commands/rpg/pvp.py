import disnake

from asyncio import sleep, TimeoutError
from disnake.ext import commands
from random import randint
from resources.fight import Entity, Ext
from resources.check import check_it
from resources.db import Database
player_1, player_2, extension = {}, {}, Ext()


class PVP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='pvp')
    async def pvp(self, ctx, member: disnake.Member = None):
        """Comando usado pra ir PVP no rpg da ashley
        Use ash pvp"""
        global player_1, player_2

        def check(m):
            return m.author.id == member.id and m.content.upper() in ['SIM', 'NÃO', 'S', 'N', 'NAO', 'CLARO']

        if member is None:
            msg = "<:alert:739251822920728708>│`Você precisa mencionar alguem!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if member.id == ctx.author.id:
            msg = "<:alert:739251822920728708>│`Você não pode ir PVP consigo mesmo!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.jogando:
            msg = "<:alert:739251822920728708>│`Você está jogando, aguarde para quando você estiver livre!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if member.id in self.bot.jogando:
            msg = "<:alert:739251822920728708>│`O usuario está jogando, aguarde para quando ele estiver livre!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if member.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`O USUARIO ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if member.id in self.bot.desafiado:
            msg = "<:alert:739251822920728708>│`O membro está sendo desafiado/desafiando para um PVP!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if randint(1, 100) <= 50:
            _idp1, _name_p1 = ctx.author.id, ctx.author.name
            _idp2, _name_p2 = member.id, member.name

        else:
            _idp1, _name_p1 = member.id, member.name
            _idp2, _name_p2 = ctx.author.id, ctx.author.name

        data_idp1 = await self.bot.db.get_data("user_id", _idp1, "users")
        data_idp2 = await self.bot.db.get_data("user_id", _idp2, "users")

        if data_idp1 is None or data_idp2 is None:
            _NOME = _name_p1 if data_idp1 is None else _name_p2
            msg = f'<:alert:739251822920728708>│**ATENÇÃO** : `{_NOME} não está cadastrado!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if not data_idp1['rpg']['active'] or not data_idp2['rpg']['active']:
            _NOME = _name_p1 if data_idp1 is None else _name_p2
            msg = f'<:negate:721581573396496464>│`{_NOME} USE O COMANDO` **ASH RPG** `ANTES!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _class1 = data_idp1["rpg"]["class_now"]
        _db_class1 = data_idp1["rpg"]["sub_class"][_class1]
        if _db_class1['level'] < 26:
            msg = f'<:negate:721581573396496464>│`{_name_p1} PRECISA ESTA NO NIVEL 26 OU MAIOR PARA IR PVP!\n' \
                  f'OLHE O SEU NIVEL NO COMANDO:` **ASH SKILL**'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _class2 = data_idp2["rpg"]["class_now"]
        _db_class2 = data_idp2["rpg"]["sub_class"][_class2]
        if _db_class2['level'] < 26:
            msg = f'<:negate:721581573396496464>│`{_name_p2} PRECISA ESTA NO NIVEL 26 OU MAIOR PARA  IR PVP!\n' \
                  f'PEÇA PARA ELE OLHAR O NIVEL NO COMANDO:` **ASH SKILL**'
            embed = disnake.Embed(color=self.bot.color, description=msg)
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

        player_1_data = extension.set_player(ctx.guild.get_member(_idp1), data_idp1)
        player_2_data = extension.set_player(ctx.guild.get_member(_idp2), data_idp2)

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

            skill = await player_1[_idp1].turn(ctx, ctx.guild.get_member(_idp1), player_2[_idp2])

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

            lvl_p1 = int(player_1[_idp1].level / 10)
            lvl_p2 = int(player_2[_idp2].level / 10)
            d20, d16 = randint(1, 20), randint(1, 16)
            acc = int(player_1[_idp1].status['prec'] / 2)
            dex = int(player_2[_idp2].status['agi'] / 3)
            p1_chance = d20 + lvl_p1 + acc
            p2_chance = d16 + lvl_p2 + dex

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

            if player_2[_idp2].evasion >= 3:
                p2_chance, player_2[_idp2].evasion = 0, 0

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill is None:
                p1_chance, p2_chance = 100, 0

            if p1_chance > p2_chance:
                player_1[_idp1] = await player_2[_idp2].damage(ctx, player_1[_idp1], skill)
                if skill != "PASS-TURN-MP" or skill != "PASS-TURN-HP" or skill is not None:
                    player_2[_idp2].evasion = 0
            else:
                player_2[_idp2].evasion += 1

                embed = disnake.Embed(
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

            skill = await player_2[_idp2].turn(ctx, ctx.guild.get_member(_idp2), player_1[_idp1])

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

            lvl_p2 = int(player_2[_idp2].level / 10)
            lvl_p1 = int(player_1[_idp1].level / 10)
            d20, d16 = randint(1, 20), randint(1, 16)
            acc = int(player_2[_idp2].status['prec'] / 2)
            dex = int(player_1[_idp1].status['agi'] / 3)
            p2_chance = d20 + lvl_p2 + acc
            p1_chance = d16 + lvl_p1 + dex

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

            if player_1[_idp1].evasion >= 3:
                p1_chance, player_1[_idp1].evasion = 0, 0

            if skill == "PASS-TURN-MP" or skill == "PASS-TURN-HP" or skill is None:
                p2_chance, p1_chance = 100, 0

            if p2_chance > p1_chance:
                player_2[_idp2] = await player_1[_idp1].damage(ctx, player_2[_idp2], skill)
                if skill != "PASS-TURN-MP" or skill != "PASS-TURN-HP" or skill is not None:
                    player_1[_idp1].evasion = 0
            else:
                player_1[_idp1].evasion += 1

                embed = disnake.Embed(
                    description=f"`{player_1[_idp1].name.upper()} EVADIU`",
                    color=0x000000
                )
                embed.set_thumbnail(url=f"https://storage.googleapis.com/ygoprodeck.com/pics_artgame/47529357.jpg")
                embed.set_author(name=player_1_data['name'], icon_url=player_1_data['img'])
                await ctx.send(embed=embed)

            # --------======== TEMPO DE ESPERA ========--------
            await sleep(0.5)
            # --------======== ............... ========--------

        # sistema de level up das skills PLAYER 1
        query, query_user, cl = {"_id": 0, "user_id": 1, "rpg": 1}, {"$set": {}}, await self.bot.db.cd("users")
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": _idp1}, query)
        _class = player_1[_idp1].data['class_now']
        if player_1[_idp1].level >= 26:
            query_user["$set"][f"rpg.sub_class.{_class}.skill_level"] = player_1[_idp1].data["skill_level"]
            await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

        # sistema de level up das skills PLAYER 2
        query, query_user, cl = {"_id": 0, "user_id": 1, "rpg": 1}, {"$set": {}}, await self.bot.db.cd("users")
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": _idp2}, query)
        _class = player_2[_idp2].data['class_now']
        if player_2[_idp2].level >= 26:
            query_user["$set"][f"rpg.sub_class.{_class}.skill_level"] = player_2[_idp2].data["skill_level"]
            await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

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
