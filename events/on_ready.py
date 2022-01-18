import disnake
import asyncio
import copy
import json

import time as date
from disnake.ext import commands
from random import choice, randint, shuffle
from datetime import datetime as dt, timedelta
from resources.verify_cooldown import verify_cooldown
from resources.structure import user_data_structure, guild_data_structure
from resources.fight import Entity
from operator import itemgetter
from resources.lotash import Lottery, create
from resources.utility import miner_bitash, miner_partner

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())

cor = {
    'clear': '\033[m',
    'cian': '\033[1;36m',
    'roxo': '\033[1;35m',
    'azul': '\033[1;34m',
    'amar': '\033[1;33m',
    'verd': '\033[1;32m',
    'verm': '\033[1;31m',
    'pers': '\033[1;35;47m'
}
loot_mvp = dict()


def last_day_of_month(date_now):
    if date_now.month == 12:
        return date_now.replace(day=31)
    return date_now.replace(month=date_now.month + 1, day=1) - timedelta(days=1)


class OnReady(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.time_ready = None
        self.color = self.bot.color
        self.m = list()
        for m in self.bot.config['battle']['bosses']:
            self.m += [m] * m['amount']
        self.url = 'https://www.twitch.tv/d3nkyt0'
        self.i = self.bot.items
        self.relics = ["WrathofNatureCapsule", "UltimateSpiritCapsule", "SuddenDeathCapsule", "InnerPeacesCapsule",
                       "EternalWinterCapsule", "EssenceofAsuraCapsule", "DivineCalderaCapsule",
                       "DemoniacEssenceCapsule"]
        self.loot_fixo = {
            "boss_key": 3,
            "angel_stone": 1,
            "enchant_silver": 1,
            "Energy": 150,
            "armor_silver": 1,
            "coins": 50
        }
        self.loot_mvp = {
            "angel_stone": 2,
            "boss_key": 15,
            "fragment_of_crystal_wind": 35,
            "fragment_of_crystal_water": 35,
            "fragment_of_crystal_fire": 35,
            "blessed_fragment_of_crystal_wind": 5,
            "blessed_fragment_of_crystal_water": 5,
            "blessed_fragment_of_crystal_fire": 5,
            "blessed_armor_mystic": 2,
            "armor_mystic": 2
        }
        self._emojis = ["<a:_y:774697621997486090>", "<a:_x:774697621867724862>",
                        "<a:_b:774697621683044392>", "<a:_a:774697620500906005>"]

    @staticmethod
    def verify_time(date_old):
        s, t, f = date_old.strftime('%Y/%m/%d %H:%M:%S'), dt.today().strftime('%Y/%m/%d %H:%M:%S'), '%Y/%m/%d %H:%M:%S'
        dif = (dt.strptime(t, f) - dt.strptime(s, f)).total_seconds()
        return True if dif < 86400 else False

    async def verify_winner(self, raw_data, raw_bets):
        _RAWRES, cl = list(), await self.bot.db.cd("lottery")
        for rd in [d async for d in raw_data if self.verify_time(d["date"]) and d["active"]]:
            _RD = ' '.join('%02d' % n for n in rd["bet"])
            for bt in raw_bets:
                _bet, _WIN, _ACERTOS = ' '.join('%02d' % n for n in bt), 0, list()
                for N in _RD.split():
                    if N in _bet.split():
                        _WIN += 1
                        _ACERTOS.append(int(N))
                if _WIN > 3:
                    rd["CONCURSO"] = _bet
                    rd["ACERTOS"] = _ACERTOS
                    rd["ACC"] = _WIN
                    _RAWRES.append(rd)
            await cl.update_one({"_id": rd["_id"]}, {"$set": {"active": False}})
        return _RAWRES

    async def treasure_hunt(self, guild):
        while not self.bot.is_closed():

            # ESCOLHENDO O CANAL QUE VAI APARECER
            guild = self.bot.get_guild(guild.id)
            user = guild.get_member(478977311266570242)

            if guild.id != 519894833783898112:
                channels = [channel for channel in guild.channels if channel.permissions_for(user).send_messages
                            and str(channel.type) == "text"]
            else:
                _CHANNELS = [847250560067436545, 847250993983782912, 847251016628961310, 847251053485490206,
                             847251104927318016, 847251147202887680, 847251267638001724, 847251338723065886,
                             847255755052285962, 847255816415084546, 847256035944038420]
                channels = [channel for channel in guild.channels if channel.permissions_for(user).send_messages
                            and str(channel.type) == "text" and channel.id in _CHANNELS]
            channel = choice(channels)

            # APARECEU!
            msg = await channel.send("<:game:519896830230790157>│**TENTEM ME PEGAR ACERTANDO A REAÇÃO QUE EU "
                                     "ESCOLHI!**")

            for emo in self._emojis:
                if channel.permissions_for(user).external_emojis and channel.permissions_for(user).add_reactions:
                    try:
                        await msg.add_reaction(emo)
                    except disnake.errors.Forbidden:
                        try:
                            await msg.delete()
                            continue
                        except disnake.errors.NotFound:
                            continue
                    except disnake.errors.NotFound:
                        try:
                            await msg.delete()
                            continue
                        except disnake.errors.NotFound:
                            continue

            # ESCOLHENDO EMOJI DE CAPTURA
            _EMOJI = choice(self._emojis)
            emoji = _EMOJI.replace('<a:', '').replace(_EMOJI[_EMOJI.rfind(':'):], '')

            def check_reaction(react, member):
                try:
                    if react.message.id == msg.id:
                        if not member.bot:
                            return True
                    return False
                except AttributeError:
                    return False

            try:
                reaction = await self.bot.wait_for('reaction_add', timeout=120.0, check=check_reaction)
            except asyncio.TimeoutError:
                # FUGIU
                try:
                    await msg.delete()
                except disnake.errors.NotFound:
                    pass
                except disnake.errors.Forbidden:
                    pass
                try:
                    await channel.send("<a:fofo:524950742487007233>│**HA! HA! HA! ESCAPEI!**", delete_after=60.0)
                except disnake.errors.Forbidden:
                    pass
                await asyncio.sleep(1800)
                continue

            try:
                _reaction = reaction[0].emoji.name
            except AttributeError:
                _reaction = reaction[0].emoji

            if _reaction == emoji and reaction[0].message.id == msg.id:
                # CAPTUROU
                try:
                    await msg.delete()
                except disnake.errors.NotFound:
                    pass
                await channel.send("🎊 **PARABENS** 🎉 **ME PEGOU! AFF!**", delete_after=60.0)
                cl = await self.bot.db.cd("users")
                data = await cl.find_one({"user_id": reaction[1].id}, {"_id": 0, "user_id": 1})
                if data is not None:
                    await cl.update_one({"user_id": data["user_id"]}, {"$inc": {"inventory.boss_key": 10}})
                    await channel.send("🎊 **PARABENS** 🎉 **POR SER REGISTRADO VOCE TAMBEM GANHOU** `10` **BOSS KEY**",
                                       delete_after=30.0)
            else:
                # ERROU
                try:
                    await msg.delete()
                except disnake.errors.NotFound:
                    pass
                await channel.send("<a:fofo:524950742487007233>│**HA! HA! HA! ERROU!**", delete_after=60.0)

            # tempo de espera (de uma caçada pra outra)
            await asyncio.sleep(1800)

    async def reset_pick(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            _DATE = date.localtime()
            if _DATE[4] == 0:

                guild = self.bot.get_guild(519894833783898112)
                for member in guild.members:
                    query = {"_id": 0, "user_id": 1, "config": 1}
                    record = await (await self.bot.db.cd("users")).find_one({"user_id": member.id}, query)
                    if record is not None:
                        roles, cargos = record['config']['roles'], member.roles
                        roles = list() if roles is None else roles
                        if len(roles) > 0:

                            for c in range(0, len(cargos)):
                                if cargos[c].name not in ["@everyone", "Server Booster", "</Ash_Lovers>"]:
                                    await member.remove_roles(cargos[c])

                            for c in range(0, len(roles)):
                                if roles[c] not in ["@everyone", "Server Booster", "</Ash_Lovers>"]:
                                    role = disnake.utils.find(lambda r: r.name == roles[c], guild.roles)
                                    await member.add_roles(role)

                cd = await self.bot.db.cd("users")
                query = {"$unset": {"cooldown.pick": ""},
                         "$set": {"user.stickers": 0, "config.provinces": None, "config.roles": list()}}
                await cd.update_many({}, query)

            await asyncio.sleep(60)

    async def merchant_system(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            query = {"_id": 0, "guild_id": 1, "data": 1, "bot_config": 1}
            g_data = await (await self.bot.db.cd("guilds")).find_one({"guild_id": guild.id}, query)
            if g_data is None:
                continue

            if len([m for m in guild.members if not m.bot]) >= 50 and g_data['data']['accounts'] >= 10:
                if g_data['bot_config']['ash_draw']:
                    channel__ = self.bot.get_channel(g_data['bot_config']['ash_draw_id'])
                    if channel__ is None:
                        continue

                    # verificando as permissões da ashley
                    user = guild.get_member(478977311266570242)
                    if user.guild_permissions.external_emojis and user.guild_permissions.add_reactions:
                        # cria um loop pra cada guilda separadamente
                        self.bot.loop.create_task(self.treasure_hunt(guild))

    async def lottery_system(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            _DATE, _CHANNEL, _USERS = date.localtime(), self.bot.get_channel(847578751117295639), list()
            _RAW = (await self.bot.db.cd("lottery")).find()
            _DN = last_day_of_month(dt.today())
            if _DATE[3] in self.bot.lt:
                if not self.bot.lt_per_day[str(_DATE[3])]:
                    amount, numbers, msg = 2 if _DATE[2] != _DN.day else 10, 6, "**NUMEROS SORTEADOS**\n"
                    bets = create(Lottery("megasena"), amount, numbers)

                    for bet in bets:
                        _bet = ' '.join('%02d' % n for n in bet)
                        msg += f"<:confirmed:721581574461587496>│`{_bet}`\n"

                    ashley_guild = self.bot.get_guild(519894833783898112)
                    lovers = disnake.utils.find(lambda r: r.name == "</Ash_Lovers>", ashley_guild.roles)
                    embed = disnake.Embed(color=self.bot.color, description=msg)
                    await _CHANNEL.send(f"{lovers.mention} **SAIU O RESULTADO DA LOTERIA!**", embed=embed)

                    _espera = await _CHANNEL.send("<a:loading:520418506567843860>│ `AGUARDEM, ESTOU PROCESSANDO O(S) "
                                                  "VENCERDOR(ES)...`")

                    self.bot.lt_per_day[str(_DATE[3])] = True
                    _USERS = await self.verify_winner(_RAW, bets)
                    _SENA = [U for U in _USERS if U["ACC"] == 6]
                    cl = await (await self.bot.db.cd("miscellaneous")).find_one({"_id": "lottery"})

                    if len(_USERS) > 0 and _DATE[2] != _DN.day or _DATE[2] == _DN.day and len(_SENA) > 0:
                        await _espera.delete()
                        for _USER in _USERS:
                            winner = self.bot.get_user(_USER["user_id"])
                            _ACC, msg = ' '.join('%02d' % n for n in _USER['ACERTOS']), ""

                            if _USER["ACC"] == 3:
                                reward = cl["terno"]
                                msg = await self.bot.db.give_money(None, reward, _USER["user_id"], 519894833783898112)

                            if _USER["ACC"] == 4:
                                reward = cl["quadra"]
                                msg = await self.bot.db.give_money(None, reward, _USER["user_id"], 519894833783898112)

                            if _USER["ACC"] == 5:
                                reward = cl["quina"]
                                msg = await self.bot.db.give_money(None, reward, _USER["user_id"], 519894833783898112)

                            if _USER["ACC"] == 6:
                                reward, query = cl["sena"] + cl["accumulated"], {"$set": {"accumulated": 0}}
                                await (await self.bot.db.cd("miscellaneous")).update_one({"_id": "lottery"}, query)
                                msg = await self.bot.db.give_money(None, reward, _USER["user_id"], 519894833783898112)

                            _winner = f"{winner.mention}" if winner in ashley_guild.members else f"**{winner}**"
                            await _CHANNEL.send(f"🎊 **PARABENS** 🎉 - `O membro` {_winner} `ganhou na loteria com:`"
                                                f" **{_USER['ACC']}** `acertos` **{_ACC}** `no concurso:` "
                                                f"**{_USER['CONCURSO']}**\n{msg}")

                    elif _DATE[2] == _DN.day:
                        _RAW = (await self.bot.db.cd("lottery")).find()
                        _BETS = [d async for d in _RAW if d['date'].month == _DATE[1]]
                        _BET, query = choice(_BETS), {"$set": {"accumulated": 0}}
                        winner, reward = self.bot.get_user(_BET["user_id"]), cl["accumulated"]
                        msg = await self.bot.db.give_money(None, reward, _BET["user_id"], 519894833783898112)
                        await (await self.bot.db.cd("miscellaneous")).update_one({"_id": "lottery"}, query)
                        await _espera.delete()
                        _winner = f"{winner.mention}" if winner in ashley_guild.members else f"**{winner}**"
                        _txt = f"`Como ninguem ganhou no sorteio da sena e esse é o ultimo dia do mês, foi sorteado" \
                               f" um dos bilhetes comprados nesse mês para que o total acumulado seja esvaziado!`\n" \
                               f"🎊 **PARABENS** 🎉 - `O membro` {_winner} `ganhou na loteria, com o " \
                               f"bilhete:` **{_BET['bet']}**\n{msg}"
                        await _CHANNEL.send(_txt)

                    else:
                        await _espera.delete()
                        await _CHANNEL.send("**NINGUEM GANHOU!**")

            await asyncio.sleep(60)

    async def boss_system(self):
        global loot_mvp
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            date_ = date.localtime()

            # reseta os horarios dos boss
            if date_[3] not in self.bot.bh:
                if len([st for st in self.bot.boss_per_day.values() if st]) == len(self.bot.boss_per_day.keys()):
                    for stt in self.bot.boss_per_day.keys():
                        self.bot.boss_per_day[stt] = False

            # existe uma diferença de hora de +3 para o servidor da ashley
            if date_[3] in self.bot.bh and not self.bot.boss_live:  # cria o boss
                if not self.bot.boss_per_day[str(date_[3])]:
                    _boss = choice(self.m)
                    db_boss = copy.deepcopy(_boss)
                    db_boss['enemy'] = None
                    db_boss["pdef"] += randint(75, 150)
                    db_boss["mdef"] += randint(75, 150)
                    db_boss["salvation"] = False
                    self.bot.boss_now = Entity(db_boss, False, is_boss=True)
                    self.bot.boss_per_day[str(date_[3])] = True
                    self.bot.boss_live = True
                    self.bot.boss_msg = False
                    self.bot.boss_players = dict()

            # envia a msg que o boss foi criado
            if self.bot.boss_live and not self.bot.boss_msg:
                channel = self.bot.get_channel(837777587064930316)
                ashley_guild = self.bot.get_guild(519894833783898112)
                lovers = disnake.utils.find(lambda r: r.name == "</Ash_Lovers>", ashley_guild.roles)
                msg = f"<:confirmed:721581574461587496>│**PARA BATALHAR USE: ASH BOSS**"
                embed = disnake.Embed(color=self.bot.color, description=msg)
                await channel.send(f"{lovers.mention} **APARECEU UM BOSS!**", embed=embed)
                self.bot.boss_msg = True

            # relata os ganhadores da batalha
            if self.bot.boss_live:
                if self.bot.boss_now.status["hp"] <= 0:
                    self.bot.boss_live = False

                    _mvp = [(k, self.bot.boss_players[k]["score"]) for k in self.bot.boss_players.keys()]
                    mvp = sorted(_mvp, key=itemgetter(1), reverse=True)
                    bpk = len(self.bot.boss_players.keys())
                    _lw = 3 if bpk >= 15 else 2 if bpk >= 10 else 1 if bpk >= 5 else 0
                    winners = [mvp[i] for i in range(_lw)] if _lw > 0 else list()

                    channel = self.bot.get_channel(837777587064930316)
                    players = [p for p in self.bot.boss_players.keys() if
                               self.bot.boss_players[p]["hpt"] >= 400 and self.bot.boss_players[p]["hit"] >= 4]

                    p_chance = []
                    for p in players:
                        p_chance += [p] * self.bot.boss_players[p]["hit"]

                    pl = f"\n".join([f"**{self.bot.get_user(p)}** - [`Score:` **{self.bot.boss_players[p]['score']}**]"
                                     f"{' **{MPV}**' if p in [n[0] for n in winners] else ''}" for p in players])

                    msg = f"<:confirmed:721581574461587496>│`O BOSS MORREU!` - **LISTA DOS GANHADORES:**\n\n{pl}"
                    embed = disnake.Embed(color=self.bot.color, description=msg)
                    await channel.send(embed=embed)

                    # sistema de loot
                    reward = self.bot.boss_now.data["reward"]

                    if len(players) >= 1:
                        list_items = []
                        for _, amount in reward.items():
                            for _ in range(amount[1]):
                                list_items += [choice(amount[0])]
                        shuffle(list_items)

                        _l = dict()
                        for play in players:
                            _l[play] = dict()

                        for item in list_items:
                            try:
                                _l[choice(p_chance)][item[0]] += item[1]
                            except KeyError:
                                _l[choice(p_chance)][item[0]] = item[1]

                        for p in players:
                            # salvamento dos itens no iventario
                            query_user = {"$inc": {}}

                            for it in _l[p].keys():
                                if f"inventory.{it}" in query_user["$inc"].keys():
                                    query_user["$inc"][f"inventory.{it}"] += _l[p][it]
                                else:
                                    query_user["$inc"][f"inventory.{it}"] = _l[p][it]

                            for ti in self.loot_fixo.keys():
                                if f"inventory.{ti}" in query_user["$inc"].keys():
                                    query_user["$inc"][f"inventory.{ti}"] += self.loot_fixo[ti]
                                else:
                                    query_user["$inc"][f"inventory.{ti}"] = self.loot_fixo[ti]

                            loot_random, cont = list(), 0
                            loot_random_f = [f"{self.i[i][0]} `{self.i[i][1]}:` **{_l[p][i]}**" for i in _l[p].keys()]
                            if len(loot_random_f) > 0:
                                for text in loot_random_f:
                                    if len(loot_random) == 0:
                                        loot_random.append(f"\n{text}")
                                    else:
                                        if len(loot_random[cont]) + len(text) < 1000:
                                            loot_random[cont] += f"\n{text}"
                                        else:
                                            cont += 1
                                            loot_random.append(f"\n{text}")

                            loot_fixo = "\n".join([f"{self.i[i][0]} `{self.i[i][1]}:` **{self.loot_fixo[i]}**"
                                                   for i in self.loot_fixo.keys()])
                            loot_mvp[p] = "Você nao foi MPV..."
                            if len(winners) > 0:
                                if p in [n[0] for n in winners]:
                                    tot = dict()
                                    for mv in self.loot_mvp.keys():
                                        value = randint(1, self.loot_mvp[mv])
                                        tot[mv] = value
                                        if f"inventory.{mv}" in query_user["$inc"].keys():
                                            query_user["$inc"][f"inventory.{mv}"] += value
                                        else:
                                            query_user["$inc"][f"inventory.{mv}"] = value
                                    loot_mvp[p] = "\n".join([f"{self.i[i][0]} `{self.i[i][1]}:` **{tot[i]}**"
                                                             for i in tot.keys()])

                            cl = await self.bot.db.cd("users")
                            await cl.update_one({"user_id": p}, query_user, upsert=False)

                            user = self.bot.get_user(p)
                            _tt = "**Loot do** - `" + str(user) + "`"
                            desc = f"```py\n" \
                                   f"Total de Hits: {self.bot.boss_players[user.id]['hit']}\n" \
                                   f"Total de Critical: {self.bot.boss_players[user.id]['crit']}\n" \
                                   f"Total de Effects: {self.bot.boss_players[user.id]['eff']}\n" \
                                   f"Damage Recebido: {self.bot.boss_players[user.id]['dano']}\n" \
                                   f"Damage no Boss: {self.bot.boss_players[user.id]['dano_boss']}```"
                            embed = disnake.Embed(color=self.bot.color, title=_tt, description=desc)
                            title_1 = "**Loot Aleatorio**"
                            if len(loot_random) == 0:
                                loot_random = "Você nao teve loot aleatorio..."
                                embed.add_field(name=title_1, value=loot_random, inline=False)
                            else:
                                for texts in loot_random:
                                    embed.add_field(name=title_1, value=texts, inline=False)
                            title_2 = "**Loot Fixo**"
                            embed.add_field(name=title_2, value=loot_fixo, inline=False)
                            title_3 = "**Bonus de  Loot pelo MPV**"
                            embed.add_field(name=title_3, value=loot_mvp[p], inline=False)
                            embed.set_thumbnail(url=user.display_avatar)
                            embed.set_footer(text="Ashley ® Todos os direitos reservados.")

                            try:
                                await user.send(embed=embed)
                            except disnake.errors.Forbidden:
                                await channel.send(embed=embed)

                    else:
                        await channel.send(f"<:negate:721581573396496464>│`Sem jogadores que atingiram o minimo de"
                                           f" 4 Hits e 400 de HP retirado do BOSS`")
            await asyncio.sleep(60)

    async def security_macro(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            date_ = date.localtime()
            # existe uma diferença de hora de +3 para o servidor da ashley
            if date_[3] == 3 and date_[4] <= 15:
                all_data = (await self.bot.db.cd("users")).find({}, {"_id": 0, "user_id": 1, "security": 1})
                for data in [d async for d in all_data]:

                    if data['security']['last_verify'] is not None:
                        if data['security']['last_blocked'] is not None:
                            last_verify = date.mktime(data['security']['last_verify'].timetuple())
                            last_blocked = date.mktime(data['security']['last_blocked'].timetuple())
                            minutes = int(int(last_verify - last_blocked) / 60)
                            if minutes > 4320:
                                data['security']['blocked'] = False

                    if not data['security']['blocked']:
                        data['security']['commands'] = 0
                        data['security']['commands_today'] = 0
                        data['security']['strikes_today'] = 0
                        data['security']['strikes'] = 0
                        data['security']['last_verify'] = dt.today()
                        data['security']['status'] = True
                        data['security']['warns'] = {"80": False, "85": False, "90": False, "95": False, "100": False}
                    else:
                        data['security']['commands'] = 0
                        data['security']['commands_today'] = 0
                        data['security']['strikes_today'] = 0
                        data['security']['strikes'] = 0
                        data['security']['last_verify'] = dt.today()
                    cl = await self.bot.db.cd("users")
                    query = {"$set": {"security": data["security"]}}
                    await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)
            await asyncio.sleep(300)

    async def draw_member(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if await verify_cooldown(self.bot, "draw_member", 3600):
                query = {"_id": 0, "user_id": 1, "guild_id": 1}
                all_data = [d async for d in (await self.bot.db.cd("users")).find({}, query)]
                for guild in self.bot.guilds:

                    query = {"_id": 0, "guild_id": 1, "data": 1, "bot_config": 1}
                    g_data = await (await self.bot.db.cd("guilds")).find_one({"guild_id": guild.id}, query)
                    if g_data is None:
                        continue

                    if len([m for m in guild.members if not m.bot]) >= 50 and g_data['data']['accounts'] >= 10:
                        if g_data['bot_config']['ash_draw']:
                            channel__ = self.bot.get_channel(g_data['bot_config']['ash_draw_id'])
                            if channel__ is None:
                                continue

                            members = list()
                            for data in all_data:
                                if data['guild_id'] == guild.id:
                                    members.append(data['user_id'])

                            if len(members) < 1:
                                continue

                            member = choice(members)
                            _member = self.bot.get_user(member)
                            while _member is None:
                                member = choice(members)
                                _member = self.bot.get_user(member)

                            query_user = {"$inc": {}}

                            rewards = {'coins': randint(50, 150), 'Energy': randint(25, 75)}
                            item_plus = choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal'])
                            rewards[item_plus] = randint(1, 5)

                            chance = randint(1, 100)
                            if chance <= 75:
                                item_plus = choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal'])
                                rewards[item_plus] = randint(1, 5)

                            if chance <= 60:
                                item_plus = choice(['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal'])
                                rewards[item_plus] = randint(1, 5)

                            if chance <= 45:
                                item_bonus = choice(['ttbag', 'ttbag', 'ttbag'])
                                rewards[item_bonus] = randint(5, 15)

                            if chance <= 30:
                                item_bonus = choice(['ttbag', 'ttbag', 'ttbag'])
                                rewards[item_bonus] = randint(5, 15)

                            if chance <= 15:
                                item_bonus = choice(['solution_agent_green', 'solution_agent_blue', 'enchanted_stone'])
                                rewards[item_bonus] = randint(1, 3)

                            ext = ''.join([f"{self.bot.items[k][0]} **{v}** `{self.bot.items[k][1]}`\n"
                                           for k, v in rewards.items()])

                            embed = disnake.Embed(title="`Fiz o sorteio de um membro`", colour=self.color,
                                                  description=f"Membro sorteado foi **{str(_member)}**\n "
                                                              f"<a:palmas:520418512011788309>│"
                                                              f"`Parabens você acaba de ganhar:`\n{ext}")

                            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar)
                            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                            embed.set_thumbnail(url=_member.display_avatar)

                            ash_member = channel__.guild.get_member(self.bot.user.id)
                            perms = channel__.permissions_for(ash_member)
                            if perms.send_messages and perms.read_messages:
                                if not perms.embed_links or not perms.attach_files:
                                    await channel__.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` "
                                                         "**ADICIONAR LINKS E DE ADICIONAR IMAGENS, PARA PODER "
                                                         "FUNCIONAR CORRETAMENTE!**")
                                else:
                                    await channel__.send(embed=embed)

                            for k, v in rewards.items():
                                query_user["$inc"][f"inventory.{k}"] = v

                            cl = await self.bot.db.cd("users")
                            await cl.update_one({"user_id": member}, query_user, upsert=False)
            await asyncio.sleep(300)

    async def draw_gift(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if await verify_cooldown(self.bot, "draw_gift", 17280):
                for guild in self.bot.guilds:
                    query = {"_id": 0, "guild_id": 1, "data": 1, "bot_config": 1}
                    data = await (await self.bot.db.cd("guilds")).find_one({"guild_id": guild.id}, query)
                    if data is None:
                        continue
                    if len([m for m in guild.members if not m.bot]) >= 50 and data['data']['accounts'] >= 10:
                        if data['bot_config']['ash_draw']:
                            channel__ = self.bot.get_channel(data['bot_config']['ash_draw_id'])
                            if channel__ is None:
                                continue

                            list_boxes = []
                            for k, v in self.bot.boxes.items():
                                list_boxes += [k] * v

                            _BOX = choice(list_boxes)
                            box_type = [k for k in self.bot.boxes.keys()].index(_BOX)
                            for _ in range(box_type + 1):
                                if guild.id not in self.bot.box:
                                    self.bot.box[guild.id] = {"quant": 1, "boxes": [box_type]}
                                else:
                                    self.bot.box[guild.id]['quant'] += 1
                                    self.bot.box[guild.id]['boxes'].append(box_type)

                            embed = disnake.Embed(
                                title="**Presente Liberado**",
                                colour=self.color,
                                description=f"Esse servidor foi gratificado com {box_type + 1} presente(s) "
                                            f"**{self.bot.boxes_l[str(box_type)]}**!\n"
                                            f"Para abri-lo é so usar o comando `ash open`\n"
                                            f"**qualquer membro pode abrir um presente**\n"
                                            f"**Obs:** Essa guilda tem {self.bot.box[guild.id]['quant']} presente(s)"
                                            f"disponiveis!")
                            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar)
                            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                            embed.set_thumbnail(url=_BOX)
                            ash_member = channel__.guild.get_member(self.bot.user.id)
                            perms = channel__.permissions_for(ash_member)
                            if perms.send_messages and perms.read_messages:
                                if not perms.embed_links or not perms.attach_files:
                                    await channel__.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` "
                                                         "**ADICIONAR LINKS E DE ADICIONAR IMAGENS, PARA PODER "
                                                         "FUNCIONAR CORRETAMENTE!**")
                                else:
                                    await channel__.send(embed=embed)

                            guild__ = self.bot.get_guild(data['guild_id'])
                            role = disnake.utils.find(lambda r: r.name == "</Ash_Lovers>", guild__.roles)
                            msg = "<:alert:739251822920728708>│`CRIE UM CARGO CHAMADO` **</Ash_Lovers>** `PARA SER" \
                                  " PINGADO QUANDO UM PRESENTE DROPAR.`"
                            if role is not None:
                                msg = f"<:confirmed:721581574461587496>│`Olha só gente, dropou um presente...` " \
                                      f"{role.mention}\n **Obs:** `se voce tambem quiser ser pingado use o comando`" \
                                      f" **ASH LOVER** `ou se vc nao quiser mais ser pingado, use o comando` " \
                                      f"**ASH UNLOVER**."
                            ash_member = channel__.guild.get_member(self.bot.user.id)
                            perms = channel__.permissions_for(ash_member)
                            if perms.send_messages and perms.read_messages:
                                await channel__.send(msg)

            await asyncio.sleep(300)

    async def change_status(self):
        await self.bot.wait_until_ready()
        status, details = "GitHub - Ashley Lab", "Artigo de Ajuda do RPG"
        activity = disnake.Streaming(name=status, url=self.url, details=details)
        await self.bot.change_presence(activity=activity)

    async def create_miner(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for miner in self.bot.minelist:
                if not self.bot.minelist[miner]["active"]:
                    self.bot.minelist[miner]["active"] = True
                    miner_now = self.bot.minelist[miner]
                    self.bot.loop.create_task(miner_bitash(self.bot, miner_now))
                    channel, user = self.bot.get_channel(932446926471852083), self.bot.get_user(int(miner))
                    await channel.send(f"🟢 >>> MINERADOR CRIADO PARA [{user.mention}] <<<")
            await asyncio.sleep(60)

    async def create_miner_partner(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for miner in self.bot.minelist_partner:
                if not self.bot.minelist_partner[miner]["active"]:
                    self.bot.minelist_partner[miner]["active"] = True
                    miner_now = self.bot.minelist_partner[miner]
                    self.bot.loop.create_task(miner_partner(self.bot, miner_now))
                    channel, user = self.bot.get_channel(932446926471852083), self.bot.get_user(int(miner))
                    await channel.send(f"🟢 >>> MINERADOR **PARTNER** CRIADO PARA [{user.mention}] <<<")
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):

        owner = str(self.bot.get_user(self.bot.owner_ids[0]))
        ver_ = self.bot.version
        id_bot = str(self.bot.user.id)
        name = str(self.bot.user)
        shards = self.bot.shard_count
        log = 'LOGADO COM SUCESSO'
        servs = str(len(self.bot.guilds))
        late = int(self.bot.latency * 1000)
        emoji = len(self.bot.emojis)
        users = len(self.bot.users)
        self.time_ready = dt.utcnow()
        time = self.time_ready - self.bot.start_time

        # inicializar os atributos awaits
        print("\n\033[1;35m( >> ) | Iniciando atributos assincronos...\033[m")
        await self.bot.atr_initialize()
        print("\033[1;35m( ✔ ) | Atributos assincronos inicializados com sucesso!\033[m\n")

        if not self.bot.fastboot:
            print("\n\033[1;35m( >> ) | Iniciando exclusão dos gifts sem validade...\033[m")
            all_data = await self.bot.db.get_all_data("gift")
            cont = 0
            for data in all_data:
                if not await verify_cooldown(self.bot, data['_id'], data['validity'], True):
                    await self.bot.db.delete_data({"_id": data['_id']}, "gift")
                    cont += 1
            print(f'\033[1;32m( 🔶 ) | Exclusão de \033[1;34m{cont} Gifts\033[1;32m foi feita com sucesso!\33[m')
            print("\033[1;35m( ✔ ) | Exclusão dos gifts sem validade finalizados!\033[m\n")

            print("\n\033[1;35m( >> ) | Redefinindo itens de evento...\033[m")

            # linha para retirar os itens de evento das guildas
            await (await self.bot.db.cd("guilds")).update_many({}, {"$set": {"event": guild_data_structure["event"]}})

            all_data = (await self.bot.db.cd("users")).find({}, {"_id": 0, "user_id": 1, "inventory": 1})
            for data in [d async for d in all_data]:

                if not self.bot.event_special:
                    items = list(data['inventory'].keys())
                    for item in items:
                        if item in self.relics:
                            del data['inventory'][item]

                cl = await self.bot.db.cd("users")
                query = {"$set": {"inventory": data["inventory"]}}
                await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)
            print('\033[1;32m( 🔶 ) | Exclusão dos \033[1;34mITENS DE EVENTO\033[1;32m foi feita com sucesso!\33[m')
            print("\033[1;35m( ✔ ) |Redefinição dos itens de evento finalizadas!\033[m\n")

        if self.bot.db_struct:
            print("\n\033[1;35m( >> ) | Iniciando reestruturação do banco de dados...\033[m")
            all_data = await self.bot.db.get_all_data("users")
            for data in all_data:
                update = data
                for key in user_data_structure.keys():
                    if key in data:
                        try:
                            for k in user_data_structure[key].keys():
                                if k not in data[key]:
                                    update[key][k] = user_data_structure[key][k]
                        except AttributeError:
                            pass
                    else:
                        update[key] = user_data_structure[key]
                await self.bot.db.update_data(data, update, "users")
            print('\033[1;32m( 🔶 ) | Reestruturação dos \033[1;34mUSUARIOS\033[1;32m foi feita com sucesso!\33[m')

            all_data = await self.bot.db.get_all_data("guilds")
            for data in all_data:
                update = data
                for key in guild_data_structure.keys():
                    if key in data:
                        try:
                            for k in guild_data_structure[key].keys():
                                if k not in data[key]:
                                    update[key][k] = guild_data_structure[key][k]
                        except AttributeError:
                            pass
                    else:
                        update[key] = guild_data_structure[key]
                await self.bot.db.update_data(data, update, "guilds")
            print('\033[1;32m( 🔶 ) | Reestruturação dos \033[1;34mSERVIDORES\033[1;32m foi feita com sucesso!\33[m')
            print("\033[1;35m( ✔ ) | Reestruturação do banco de dados finalizada!\033[m\n")

        print("\n\033[1;35m( >> ) | Iniciando carregamento dos loops internos...\033[m")
        if _auth["change_status"]:
            self.bot.loop.create_task(self.change_status())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mSTATUS_DA_ASHLEY\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["draw_member"]:
            self.bot.loop.create_task(self.draw_member())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mDRAW_MEMBERS\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["draw_gift"]:
            self.bot.loop.create_task(self.draw_gift())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mDRAW_GIFT\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["security_macro"]:
            self.bot.loop.create_task(self.security_macro())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mSECURITY_MACRO\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["boss_system"]:
            self.bot.loop.create_task(self.boss_system())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mBOSS_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["lottery_system"]:
            self.bot.loop.create_task(self.lottery_system())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mLOTTERY_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["merchant_system"]:
            await self.merchant_system()
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mMERCHANT_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["reset_pick"]:
            self.bot.loop.create_task(self.reset_pick())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mRESET_PICK\033[1;32m foi carregado com sucesso!\33[m')
        if _auth["miner"]:
            self.bot.loop.create_task(self.create_miner())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mCREATE_MINER\033[1;32m foi carregado com sucesso!\33[m')
            self.bot.loop.create_task(self.create_miner_partner())
            print('\033[1;32m( 🔶 ) | O loop \033[1;34mCREATE_MINER_PARTNER\033[1;32m foi carregado com sucesso!\33[m')
        print("\033[1;35m( ✔ ) | Loops internos carregados com sucesso!\033[m\n")

        print(cor['cian'], '▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', cor['clear'])
        print(cor['roxo'], log.center(70), cor['clear'])
        print(cor['azul'], '▍ Owner    ⠿', cor['clear'], cor['verd'], '{}'.format(str(owner).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ Versão   ⠿', cor['clear'], cor['amar'], '{}'.format(str(ver_).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ App      ⠿', cor['clear'], cor['amar'], '{}'.format(str(name).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ ID       ⠿', cor['clear'], cor['amar'], '{}'.format(str(id_bot).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ Shards   ⠿', cor['clear'], cor['amar'], '{}'.format(str(shards).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ Servers  ⠿', cor['clear'], cor['amar'], '{}'.format(str(servs).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ Latência ⠿', cor['clear'], cor['verm'], '{}ms'.format(str(late).rjust(48)), cor['clear'])
        print(cor['azul'], '▍ Emojis   ⠿', cor['clear'], cor['amar'], '{}'.format(str(emoji).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ Users    ⠿', cor['clear'], cor['amar'], '{}'.format(str(users).rjust(50)), cor['clear'])
        print(cor['azul'], '▍ Uptime   ⠿', cor['clear'], cor['amar'], '{}s'.format(str(time).rjust(49)), cor['clear'])
        print(cor['cian'], '▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', cor['clear'])
        self.bot.is_ashley = True


def setup(bot):
    bot.add_cog(OnReady(bot))
    print('\033[1;33m( 🔶 ) | O evento \033[1;34mON_READY\033[1;33m foi carregado com sucesso!\33[m')
