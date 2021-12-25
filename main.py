# ARQUIVO PRINCIPAL DE INICIALIZAÇÃO DO BOT: ASHLEY PARA DISCORD.
# CRIADO POR: DANIEL AMARAL -> Denky#5960
# SEGUE ABAIXO OS IMPORTS COMPLETOS
import disnake
import aiohttp
import psutil
import json
import copy
import sys
import traceback
import humanize
import platform
# SEGUE ABAIXO OS IMPORTS PARCIAIS
import time as date
from random import choice, randint
from datetime import datetime as dt
from collections import Counter
from disnake.ext import commands
from resources.color import random_color
from bson.json_util import dumps
from resources.utility import date_format, patent_calculator, guild_info, rank_definition, CreateCaptcha
from resources.utility import include
from resources.db import Database, DataInteraction
from resources.verify_cooldown import verify_cooldown
from resources.boosters import Booster
from resources.push import OneSignal
from config import data as config
from adlink.adfly_api_instance import api as api_adfly
from disnake import Webhook
from resources.check import validate_url

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())


# CLASSE PRINCIPAL SENDO SUBCLASSE DA BIBLIOTECA DISNAKE
class Ashley(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, shard_count=_auth["shard"], **kwargs)
        self.owner_ids = [300592580381376513, 416606375498481686]
        self.msg_cont = 0
        self.start_time = dt.utcnow()
        self.commands_used = Counter()
        self.guilds_commands = Counter()
        self.guilds_messages = Counter()
        self.commands_user = Counter()
        self.data_cog = dict()
        self.box = dict()
        self.ash_sticker = dict()
        self.moon_bag = dict()
        self.chests_users = dict()
        self.chests_marry = dict()
        self.help_emoji = dict()
        self.cmd_event = dict()
        self.cmd_marry = dict()
        self.blacklist = list()
        self.shutdowns = list()
        self.guilds_vips = list()
        # -----------================------------
        self.batalhando = list()  # status de um jogador (OK)
        self.jogando = list()  # status de um jogador (OK)
        self.casando = list()  # status de um jogador (OK)
        self.comprando = list()  # status de um jogador (OK)
        self.minerando = list()  # status de um jogador (OK)
        self.desafiado = list()  # status de um jogador (OK)
        self.lendo = list()  # status de um jogador (OK)
        self.recovery = list()  # status de um jogador (OK)
        # -----------================------------

        self.session = self.loop.run_until_complete(self.create_session())

        # haw_data
        self.config = config
        self.em = self.config["emojis"]["msg"]
        self.color = int(config['config']['default_embed'], 16)
        self.announcements = self.config['attribute']['announcements']
        self.all_prefix = self.config['attribute']['all_prefix']
        self.vip_cog = self.config['attribute']['vip_cog']
        self.titling = self.config['attribute']['titling']
        self.boxes_l = self.config['attribute']['boxes_l']
        self.chests_l = self.config['attribute']['chests_l']
        self.boxes = self.config['attribute']['boxes']
        self.chests = self.config['attribute']['chests']
        self.chests_lm = self.config['attribute']['chests_lm']
        self.chests_m = self.config['attribute']['chests_m']

        self.ash_stickers = dict()
        for TYPE in self.config['sticker_book'].keys():
            for STICKER in self.config['sticker_book'][TYPE]:
                self.ash_stickers[STICKER] = self.config['sticker_book'][TYPE][STICKER]

        self.money = self.config['attribute']['money']
        self.items = self.config['items']
        self.icons = self.config['icons']
        self.pets = self.config['pets']
        self.no_panning = self.config['attribute']['no_panning']
        self.staff = self.config['staff']['list']
        self.testers = self.config['staff']['testers'] + self.config['staff']['list']
        self.team = self.staff
        self.admin = [416606375498481686, 300592580381376513]
        self.shortcut = self.config['attribute']['shortcut']
        self.block = self.config['attribute']['block']

        # definição do inicio e o fim da manutenção
        self.maintenance = False  # Default: False
        self.maintenance_ini_end = ["13:00", "22:00"]  # inicio e fim da manutenção
        self.maintenance_msg = f"<a:xablau:525105065460105226>│`DESCULPE ESTOU EM MANUTENÇÃO. MAS DENTRO DE ALGUMAS" \
                               f" HORAS TUDO ESTARÁ NORMALIZADO. MANUTENÇÃO INICOU HOJE AS " \
                               f"({self.maintenance_ini_end[0]}) PREVISAO DE TERMINO " \
                               f"({self.maintenance_ini_end[1]}) +2h-2h PODENDO DURAR UM POUCO MENOS OU MAIS`\n" \
                               f"**OBS:** `ATUALMENTE APENAS PESSOAS AUTORIZADAS PODEM USAR OS RECURSOS DA ASHLEY," \
                               f" MAS LOGO TUDO ESTARÁ NORMALIZADO. A EQUIPE DA` **ASHLEY** `SENTE MUITO POR ESSE" \
                               f" TRANSTORNO!`"

        # status
        self.is_ashley = True  # Default: False
        self.d_event = [2021, 12, 23, (12, 31)]  # [ANO / MES /DIA INI ]/ MES END e DIA END
        self.event_now = "NATAL"  # NOME DO EVENTO ATUAL
        self.rate_drop = 4
        self.fastboot = True  # Default: True
        self.db_struct = False  # Default: False

        # inicio automatico do evento
        _DATE, _EVENT = date.localtime(), self.d_event
        if _DATE[0] == _EVENT[0]:  # verifica o ano
            if _DATE[1] == _EVENT[1] or _DATE[1] == _EVENT[3][0]:  # verifica o mes (inicio ou fim)
                if _EVENT[2] <= _DATE[2] or _DATE[2] <= _EVENT[3][1]:  # verifica o dia (inicio ou fim)
                    self.event_special = True
                else:
                    self.event_special = False
            else:
                self.event_special = False
        else:
            self.event_special = False
        self.winners_event_special = 3  # default: 3

        # info bot
        self.server_ = "HEROKU"
        self.github = "https://github.com/D3NKYT0/ashley_home"
        self.progress = f"V.2 -> {_auth['version']}"
        self.python_version = platform.python_version()
        self.version_str = f"2.2.5"
        self.version = f"API: {disnake.__version__} | BOT: {self.version_str} | VERSION: {self.progress}"

        # sub classes
        self.db: Database = Database(self)
        self.data: DataInteraction = DataInteraction(self)
        self.booster: Booster = Booster(self.items)
        self.push: OneSignal = OneSignal()

        # system adfly reward
        self.adfly = api_adfly

        # lottery system
        self.lt = [23]
        self.lt_per_day = {f"{self.lt[0]}": False}

        # boss system
        self.boss_live = False  # mostra se o boss esta vivo OK
        self.boss_now = None  # entidade do boss e seus status OK
        self.boss_players = dict()  # jogadores que estao matando o boss OK
        self.boss_msg = False  # msg do boss nascido OK
        self.bh = [11, 14, 18, 21, 1]  # [8, 11, 15, 18, 22] quantidade de bosses por dia OK
        self.boss_per_day = {f"{self.bh[0]}": False,  # primeiro boss
                             f"{self.bh[1]}": False,  # segundo boss
                             f"{self.bh[2]}": False,  # terceiro boss
                             f"{self.bh[3]}": False,  # quarto boss
                             f"{self.bh[4]}": False}  # quinto boss

    # create link adfly
    def adlinks(self, code):
        _link = self.adfly.shorten(f"https://ashleypro.herokuapp.com/adfly/{code}")
        return _link["data"][0]["id"], _link["data"][0]["short_url"]

    # delete link adfly
    def addelete(self, linkid):
        self.adfly.delete_url(linkid)

    @staticmethod
    async def create_session():
        return aiohttp.ClientSession()

    async def close(self):
        await self.session.close()
        await super().close()

    async def atr_initialize(self):
        self.blacklist = dumps(await self.db.get_all_data("blacklist"))
        print('\033[1;32m( 🔶 ) | Inicialização do atributo \033[1;34mBLACKLIST\033[1;32m foi feita sucesso!\33[m')

        self.shutdowns = dumps(await self.db.get_all_data("shutdown"))
        print('\033[1;32m( 🔶 ) | Inicialização do atributo \033[1;34mSHUTDOWN\033[1;32m foi feita sucesso!\33[m')

        _TEXT = "DESATIVADA"
        if self.event_special:
            _event = await (await self.db.cd("events")).find_one({"_id": self.event_now}, {"_id": 1, "status": 1})
            if _event is None:
                _data_event = {"_id": self.event_now, "status": True, "capsules": True, "winners": list()}
                await (await self.db.cd("events")).insert_one(_data_event)
                _ev_db = True
            else:
                _ev_db = True if _event["status"] else False
            self.event_special, _TEXT = _ev_db, "ATIVADA" if _ev_db else "DESATIVADA"
            if self.event_special:
                self.rate_drop = self.rate_drop * 2
        print(f'\033[1;32m( 🔶 ) | Inicialização do evento especial foi \033[1;34m{_TEXT}\033[1;32m com sucesso!\33[m')

        all_data = (await self.db.cd("guilds")).find({"vip": True}, {"_id": 0, "guild_id": 1})
        self.guilds_vips = [d["guild_id"] async for d in all_data]
        print('\033[1;32m( 🔶 ) | Inicialização do atributo \033[1;34mGUILDS_VIP\033[1;32m foi feita sucesso!\33[m')

    async def shutdown(self, reason):
        date_ = dt(*dt.utcnow().timetuple()[:6])
        data = {"_id": date_, "reason": reason}
        await self.db.push_data(data, "shutdown")
        self.shutdowns = dumps(await self.db.get_all_data("shutdown"))

    async def ban_(self, id_, reason: str):
        date_ = dt(*dt.utcnow().timetuple()[:6])
        data = {"_id": id_, str(date_): reason}
        if str(id_) not in self.blacklist:
            await self.db.push_data(data, "blacklist")
            self.blacklist = dumps(await self.db.get_all_data("blacklist"))
            return True
        else:
            return False

    async def un_ban_(self, id_):
        if str(id_) not in self.blacklist:
            return False
        else:
            await self.db.delete_data({"_id": int(id_)}, "blacklist")
            self.blacklist = dumps(await self.db.get_all_data("blacklist"))
            return True

    async def on_command(self, ctx):
        if ctx.guild is not None:
            query = {"_id": 0, "guild_id": 1}
            data_guild = await (await self.db.cd("guilds")).find_one({"guild_id": ctx.guild.id}, query)
            query = {"_id": 0, "user_id": 1}
            data_user = await (await self.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

            if data_user is not None and data_guild is not None:
                if (self.guilds_commands[ctx.guild.id] % 10) == 0:
                    for data in await self.db.get_announcements():
                        if data['data']['status']:
                            self.announcements.append(data["data"]["announce"])
                    announce = choice(self.announcements)
                    embed = disnake.Embed(
                        color=0x000000,
                        description=f'<:confirmed:721581574461587496>│**ANUNCIO**\n '
                                    f'```{announce}```')
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")
            try:
                _g = await ctx.guild.invites()
            except disnake.errors.Forbidden:
                _g = list()
            _l = "" if len(_g) == 0 else f"{_g[0]}\n"
            commands_log = self.get_channel(575688812068339717)
            await commands_log.send(f"`O membro` **{ctx.author.name}** `acabou de usar o comando` "
                                    f"**{str(ctx.command).upper()}** `dentro da guilda` **{ctx.guild.name}** "
                                    f"`no canal` **{str(ctx.channel)}** `na data e hora` **{date_format(dt.now())}**\n"
                                    f"```{_l}Memoria Atual: {self.get_ram(True)}```")

    async def on_command_completion(self, ctx):
        if ctx.guild is not None:
            _name = ctx.author.name.upper()
            cmd = str(ctx.command).lower()

            query_g = {"_id": 0, "guild_id": 1, "data": 1, "vip": 1, "available": 1}
            data_guild = await (await self.db.cd("guilds")).find_one({"guild_id": ctx.guild.id}, query_g)
            query_u = {"_id": 0, "user_id": 1, "security": 1, "user": 1, "inventory": 1,
                       "config": 1, "cooldown": 1, "treasure": 1, "rpg": 1, "guild_id": 1, "mails": 1}
            data_user = await (await self.db.cd("users")).find_one({"user_id": ctx.author.id}, query_u)
            query_user, query_guild = {"$set": {}, "$inc": {}}, {}

            if data_user is not None and data_guild is not None:
                self.commands_user[ctx.author.id] += 1
                self.commands_used[ctx.command] += 1
                self.guilds_commands[ctx.guild.id] += 1

                if ctx.author.id in self.cmd_event.keys():
                    try:
                        self.cmd_event[ctx.author.id][str(ctx.command).lower()] += 1
                    except KeyError:
                        self.cmd_event[ctx.author.id][str(ctx.command).lower()] = 1
                else:
                    self.cmd_event[ctx.author.id] = {str(ctx.command).lower(): 1}

                if ctx.author.id in self.cmd_marry.keys():
                    try:
                        self.cmd_marry[ctx.author.id][str(ctx.command).lower()] += 1
                    except KeyError:
                        self.cmd_marry[ctx.author.id][str(ctx.command).lower()] = 1
                else:
                    self.cmd_marry[ctx.author.id] = {str(ctx.command).lower(): 1}

                if data_user['security']['status']:
                    query_user["$inc"]["user.commands"] = 1
                if (data_user['user']['commands'] % 10) == 0:
                    guild_ = self.get_guild(data_user['guild_id'])
                    if guild_ is None:
                        perms = ctx.channel.permissions_for(ctx.me)
                        if perms.send_messages and perms.read_messages:
                            await ctx.send(f"<:negate:721581573396496464>│`{_name} SUA GUILDA DE CADASTRO FOI "
                                           f"DELETADA, TENTE USAR O COMANDO` **ASH TRANS** "
                                           f"`PARA MUDAR SUA GUILDA DE ORIGEM`")

                if (data_user['user']['commands'] % 2) == 0:
                    chance, quant = randint(1, 100), randint(1, 3)
                    if chance <= 50:
                        if data_user['security']['status']:
                            query_user["$inc"]["inventory.rank_point"] = quant
                            perms = ctx.channel.permissions_for(ctx.me)
                            if perms.send_messages and perms.read_messages:
                                await ctx.send(f"<:rank:519896825411665930>│🎊 **PARABENS** 🎉 `{_name} GANHOU:` "
                                               f"<:silver:519896828120924170> **{quant}** `RANKPOINT A MAIS!`",
                                               delete_after=10.0)

                if (data_user['user']['commands'] % 10) == 0:
                    chance = randint(1, 100)
                    if chance <= 20:
                        if data_user['security']['status']:
                            query_user["$inc"]["inventory.medal"] = 1
                            perms = ctx.channel.permissions_for(ctx.me)
                            if perms.send_messages and perms.read_messages:
                                await ctx.send(f"<:rank:519896825411665930>│🎊 **PARABENS** 🎉 `{_name} GANHOU:` "
                                               f"<:medals:519896836375314442> **1** `MEDALHA A MAIS!`",
                                               delete_after=10.0)

                for key in self.titling.keys():
                    if data_user['user']['commands'] >= int(key):
                        query_user["$set"]["user.titling"] = self.titling[key]

                if data_user['security']['status']:
                    if "$inc" not in query_guild.keys():
                        query_guild["$inc"] = {}
                    query_guild["$inc"]["data.commands"] = 1

                if (data_guild['data']['commands'] // 1000) > 5 and data_guild['data']['ranking'] == "Bronze":
                    _min = int(1 + (data_guild['data']['commands'] / 1000))
                    _max = _min + 1 if _min >= 200 else 200
                    chance = randint(_min, _max)
                    if chance < _min:
                        query_user["$inc"]["inventory.coins"] = 1000
                        data_guild['data']['ranking'] = "Silver"
                        perms = ctx.channel.permissions_for(ctx.me)
                        if perms.send_messages and perms.read_messages:
                            await ctx.send(f'🎊 **PARABENS** 🎉 {ctx.author} `você upou sua guilda para o ranking` '
                                           f'**Silver** `e ganhou a` **chance** `de garimpar mais ethernyas a '
                                           f'partir de agora e ` **+1000** `Fichas para jogar`')

                elif (data_guild['data']['commands'] // 1000) > 10 and data_guild['data']['ranking'] == "Silver":
                    _min = int(1 + (data_guild['data']['commands'] / 1000))
                    _max = _min + 1 if _min >= 200 else 200
                    chance = randint(_min, _max)
                    if chance < _min:
                        if "$set" not in query_guild.keys():
                            query_guild["$set"] = dict()
                        query_user["$inc"]["inventory.coins"] = 2000
                        query_guild["$set"]["data.ranking"] = "Gold"
                        perms = ctx.channel.permissions_for(ctx.me)
                        if perms.send_messages and perms.read_messages:
                            await ctx.send(f'🎊 **PARABENS** 🎉 {ctx.author} `você upou sua guilda para o ranking` '
                                           f'**Gold** `e ganhou a` **chance** `de garimpar mais ethernyas a '
                                           f'partir de agora e ` **+2000** `Fichas para jogar`')

                try:
                    _ev = len(self.cmd_event[ctx.author.id].keys())
                except KeyError:
                    _ev = 0

                try:
                    _ma = len(self.cmd_marry[ctx.author.id].keys())
                except KeyError:
                    _ma = 0

                user_status, user_marry = data_user['security']['status'], data_user['user']['married']

                # bau de evento
                if randint(1, 200) - _ev <= self.rate_drop and user_status and self.event_special:
                    try:
                        del self.cmd_event[ctx.author.id]
                    except KeyError:
                        pass
                    list_chests = []
                    for k, v in self.chests.items():
                        list_chests += [k] * v
                    _CHEST = choice(list_chests)
                    chest_type = [k for k in self.chests.keys()].index(_CHEST)

                    if ctx.author.id not in self.chests_users:
                        self.chests_users[ctx.author.id] = {"quant": 1, "chests": [chest_type]}
                    else:
                        self.chests_users[ctx.author.id]['quant'] += 1
                        self.chests_users[ctx.author.id]['chests'].append(chest_type)

                    embed = disnake.Embed(
                        title="**Baú de Evento Liberado**",
                        colour=self.color,
                        description=f"{ctx.author.mention} foi gratificado com 1 "
                                    f"**{self.chests_l[str(chest_type)]}**!\n "
                                    f"Para abri-lo é so usar o comando `ash event`\n "
                                    f"**Apenas você pode abrir seu baú**\n"
                                    f"**Obs:** Você tem **{self.chests_users[ctx.author.id]['quant']}** bau(s)!")
                    embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
                    embed.set_footer(text="Ashley ® Todos os direitos reservados.")

                    awards = 'images/elements/chest.gif'
                    file = disnake.File(awards, filename="reward_chest.gif")
                    embed.set_thumbnail(url="attachment://reward_chest.gif")
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(file=file, embed=embed, delete_after=5.0)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")

                # presente
                elif randint(1, 200) <= self.rate_drop and user_status and cmd not in self.block:
                    list_boxes = []
                    for k, v in self.boxes.items():
                        list_boxes += [k] * v

                    _BOX = choice(list_boxes)
                    box_type = [k for k in self.boxes.keys()].index(_BOX)
                    for _ in range(box_type + 1):
                        if ctx.guild.id not in self.box:
                            self.box[ctx.guild.id] = {"quant": 1, "boxes": [box_type]}
                        else:
                            self.box[ctx.guild.id]['quant'] += 1
                            self.box[ctx.guild.id]['boxes'].append(box_type)

                    embed = disnake.Embed(
                        title="**Presente Liberado**",
                        colour=self.color,
                        description=f"Esse servidor foi gratificado com {box_type + 1} presente(s) "
                                    f"**{self.boxes_l[str(box_type)]}**!\n Para abri-lo é so usar o comando "
                                    f"`ash open`\n **qualquer membro pode abrir um presente**\n"
                                    f"**Obs:** Essa guilda tem {self.box[ctx.guild.id]['quant']} presente(s) "
                                    f"disponiveis!")
                    embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
                    embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                    embed.set_thumbnail(url=_BOX)
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(embed=embed, delete_after=5.0)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")

                # figurinha
                elif randint(1, 200) <= self.rate_drop and user_status and cmd not in self.block:
                    amount = randint(2, 5)
                    if ctx.guild.id not in self.ash_sticker:
                        self.ash_sticker[ctx.guild.id] = amount
                    else:
                        self.ash_sticker[ctx.guild.id] += amount

                    embed = disnake.Embed(
                        title="**Figurinha Liberada**",
                        colour=self.color,
                        description=f"Esse servidor foi gratificado com {amount} figurinhas "
                                    f"**aleatorias**!\n Para pega-las é so usar o comando "
                                    f"`ash pick`\n **qualquer membro pode pegar uma figurinha**\n"
                                    f"**Obs:** Essa guilda tem {self.ash_sticker[ctx.guild.id]} figurinhas "
                                    f"disponiveis!")
                    embed.set_thumbnail(url="https://media.giphy.com/media/MTSADZF0IdHXFtxBXx/giphy.gif")
                    embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(embed=embed, delete_after=5.0)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")

                # moon bag
                elif randint(1, 200) <= self.rate_drop and user_status and cmd not in self.block:
                    amount = randint(1, 3)
                    if ctx.guild.id not in self.moon_bag:
                        self.moon_bag[ctx.guild.id] = amount
                    else:
                        self.moon_bag[ctx.guild.id] += amount

                    embed = disnake.Embed(
                        title="**Moon Bag Liberada**",
                        colour=self.color,
                        description=f"Esse servidor foi gratificado com **{amount} moon bag!**\n"
                                    f"Para pegar é so usar o comando `ash moon`\n"
                                    f"**qualquer membro pode pegar uma moon bag**\n"
                                    f"**Obs:** Essa guilda tem {self.moon_bag[ctx.guild.id]} moon bag "
                                    f"disponiveis!")
                    img = "https://i.pinimg.com/originals/f4/66/c7/f466c75b3fdbb134b2666cfa8f1f8e93.gif"
                    embed.set_thumbnail(url=img)
                    embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(embed=embed, delete_after=5.0)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")

                # bau de casamento
                elif randint(1, 200) - _ma <= self.rate_drop and user_status and user_marry:
                    try:
                        del self.cmd_marry[ctx.author.id]
                    except KeyError:
                        pass

                    list_chests = []
                    for k, v in self.chests_m.items():
                        list_chests += [k] * v
                    _CHEST = choice(list_chests)
                    chest_type = [k for k in self.chests_m.keys()].index(_CHEST)

                    if ctx.author.id not in self.chests_marry:
                        self.chests_marry[ctx.author.id] = {"quant": 1, "chests": [chest_type]}
                    else:
                        self.chests_marry[ctx.author.id]['quant'] += 1
                        self.chests_marry[ctx.author.id]['chests'].append(chest_type)

                    embed = disnake.Embed(
                        title="**Baú de Casamento Liberado**",
                        colour=self.color,
                        description=f"{ctx.author.mention} foi gratificado com 1 "
                                    f"**{self.chests_lm[str(chest_type)]}**!\n "
                                    f"Para abri-lo é so usar o comando `ash chest`\n "
                                    f"**Apenas você pode abrir seu baú**\n"
                                    f"**Obs:** Você tem **{self.chests_marry[ctx.author.id]['quant']}** bau(s)!")
                    embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
                    embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                    awards = 'images/elements/love.gif'
                    file = disnake.File(awards, filename="love_chest.gif")
                    embed.set_thumbnail(url="attachment://love_chest.gif")
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(file=file, embed=embed, delete_after=5.0)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")

                if str(ctx.command) in ["dance", "hug", "kick", "kiss", "lick", "punch", "push", "slap"]:
                    if "the_two_loves" in data_user['rpg']['quests'].keys():
                        _QUEST = data_user['rpg']['quests']["the_two_loves"]
                        if _QUEST["status"] == "in progress":
                            _NEXT, _INV = False, data_user["inventory"].keys()
                            if "heart_left" in _INV and "heart_right" in _INV:
                                data_user["inventory"]["heart_left"] -= 1
                                if data_user["inventory"]["heart_left"] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = {}
                                    query_user["$unset"]["inventory.heart_left"] = ""
                                else:
                                    query_user["$inc"]["inventory.heart_left"] = -1
                                data_user["inventory"]["heart_right"] -= 1
                                if data_user["inventory"]["heart_right"] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = {}
                                    query_user["$unset"]["inventory.heart_right"] = ""
                                else:
                                    query_user["$inc"]["inventory.heart_right"] = -1
                                _NEXT = True
                            reward = choice(["LADO A", "LADO B"])
                            if reward not in data_user['rpg']['quests']["the_two_loves"]["loves"] and _NEXT:
                                data_user['rpg']['quests']["the_two_loves"]["loves"].append(reward)
                                _LOVES = data_user['rpg']['quests']["the_two_loves"]["loves"]
                                query_user["$set"]["rpg.quests.the_two_loves.loves"] = _LOVES
                                await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                               f'✨ **[The 2 Loves]** ✨')

                if "the_four_crowns" in data_user['rpg']['quests'].keys():
                    _QUEST = data_user['rpg']['quests']["the_four_crowns"]
                    if _QUEST["status"] == "in progress":
                        _NEXT, _INV = False, data_user["inventory"].keys()
                        reward = choice(["dark_magician", "obelisk", "slifer", "white_dragon"])
                        if reward in _INV:
                            data_user["inventory"][reward] -= 1
                            if data_user["inventory"][reward] < 1:
                                if "$unset" not in query_user.keys():
                                    query_user["$unset"] = {}
                                query_user["$unset"][f"inventory.{reward}"] = ""
                            else:
                                query_user["$inc"][f"inventory.{reward}"] = -1
                            _NEXT = True
                        if reward not in data_user['rpg']['quests']["the_four_crowns"]["crowns"] and _NEXT:
                            data_user['rpg']['quests']["the_four_crowns"]["crowns"].append(reward)
                            _CROWNS = data_user['rpg']['quests']["the_four_crowns"]["crowns"]
                            query_user["$set"]["rpg.quests.the_four_crowns.crowns"] = _CROWNS
                            await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                           f'✨ **[The 4 Crowns]** ✨')

                if "the_nine_villages" in data_user['rpg']['quests'].keys() and randint(1, 200) <= 4:
                    _QUEST = data_user['rpg']['quests']["the_nine_villages"]
                    if _QUEST["status"] == "in progress" and len([m for m in ctx.guild.members if not m.bot]) >= 50:
                        if ctx.guild.id not in data_user['rpg']['quests']["the_nine_villages"]["villages"]:
                            data_user['rpg']['quests']["the_nine_villages"]["villages"].append(ctx.guild.id)
                            _VILLAGES = data_user['rpg']['quests']["the_nine_villages"]["villages"]
                            query_user["$set"]["rpg.quests.the_nine_villages.villages"] = _VILLAGES
                            await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                           f'✨ **[The 9 Villages]** ✨')

                patent = patent_calculator(data_user['inventory']['rank_point'], data_user['inventory']['medal'])
                if patent > data_user['user']['patent']:
                    query_user["$set"]["user.patent"] = patent
                    file = disnake.File(f'images/patente/{patent}.png', filename="patent.png")
                    embed = disnake.Embed(title='🎊 **PARABENS** 🎉\n`VOCE SUBIU DE PATENTE`', color=self.color)
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
                    embed.set_image(url="attachment://patent.png")
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        if perms.embed_links and perms.attach_files:
                            await ctx.send(file=file, embed=embed)
                        else:
                            await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                           "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")

                if data_user['config']['vip'] and str(ctx.command).lower() != "vip member":
                    try:
                        epoch = dt.utcfromtimestamp(0)
                        cooldown = data_user["cooldown"]["vip member"]
                        time_diff = (dt.utcnow() - epoch).total_seconds() - cooldown
                        if time_diff >= 2592000:  # um mes de diferença
                            if data_user['config']['vip']:
                                query_user["$set"]["config.vip"] = False
                                query_user["$set"]["rpg.vip"] = False
                                perms = ctx.channel.permissions_for(ctx.me)
                                if perms.send_messages and perms.read_messages:
                                    await ctx.send(f'<:negate:721581573396496464>│{ctx.author.mention} '
                                                   f'`INFELIZMENTE VOCÊ ACABOU DE PERDER SEU VIP!`')
                    except KeyError:
                        if (self.guilds_commands[ctx.guild.id] % 10) == 0:
                            perms = ctx.channel.permissions_for(ctx.me)
                            if perms.send_messages and perms.read_messages:
                                await ctx.send("<:alert:739251822920728708>│`Agora você pode comprar "
                                               "VIP ENTRANDO NO MEU SERVIDOR!`\n **Saiba mais usando ASH "
                                               "INVITE**")

                if data_guild['vip'] and str(ctx.command).lower() != "vip guild":
                    try:

                        query = {"_id": 0, "user_id": 1, "cooldown": 1}
                        du = await (await self.db.cd("users")).find_one({"user_id": ctx.guild.owner.id}, query)
                        cooldown = du["cooldown"]["vip guild"]

                        epoch = dt.utcfromtimestamp(0)
                        time_diff = (dt.utcnow() - epoch).total_seconds() - cooldown
                        if time_diff >= 2592000:  # um mes de diferença
                            if data_guild['vip']:
                                if "$set" not in query_guild.keys():
                                    query_guild["$set"] = dict()
                                available = data_guild['available']
                                query_guild["$set"]["vip"] = False
                                query_guild["$set"]["available"] = 0
                                perms = ctx.channel.permissions_for(ctx.me)
                                if perms.send_messages and perms.read_messages:
                                    await ctx.send(f'<:negate:721581573396496464>│ `INFELIZMENTE ESSA GUILDA ACABOU'
                                                   f' DE PERDER SEU VIP!`\n**E junto vc perdeu: {available} '
                                                   f'fragmentos nao dropados por seus membros!**')
                    except KeyError:
                        if (self.guilds_commands[ctx.guild.id] % 10) == 0:
                            perms = ctx.channel.permissions_for(ctx.me)
                            if perms.send_messages and perms.read_messages:
                                await ctx.send("<:alert:739251822920728708>│`Agora você pode comprar "
                                               "VIP GUILD ENTRANDO NO MEU SERVIDOR!`\n **Saiba mais usando ASH "
                                               "INVITE**")
                    except AttributeError:
                        pass

                # -----------------------------------------------------------------------------------------
                #                                  INICIO DO MACRO SYSTEM
                # -----------------------------------------------------------------------------------------

                data_user['security']['last_command'] = dt.today()
                data_user['security']['last_channel'] = ctx.channel.id
                data_user['security']['commands'] += 1
                query_user["$set"]["security.last_command"] = data_user['security']['last_command']
                query_user["$inc"]["security.commands_today"] = 1
                query_user["$set"]["security.last_channel"] = data_user['security']['last_channel']

                if data_user['security']['last_verify'] is None:
                    data_user['security']['last_verify'] = dt.today()
                    query_user["$set"]["security.last_verify"] = data_user['security']['last_verify']
                    query_user["$set"]["security.blocked"] = False

                last_verify_date, date_now = data_user['security']['last_verify'], dt.today()
                data_, limit = date_format(date_now), 5000
                last_verify = date.mktime(last_verify_date.timetuple())
                last_command = date.mktime(date_now.timetuple())
                m_last_verify = int(last_command - last_verify) // 60

                if data_user['security']['status']:
                    if data_user['security']['commands_today'] > int(limit / 100 * 80):
                        if data_user['security']['commands_today'] < limit:
                            warns, percent = False, int(data_user['security']['commands_today'] * 100 / limit)
                            if data_user['security']['commands_today'] >= int(limit / 100 * 80):
                                percent = 80
                            if data_user['security']['commands_today'] >= int(limit / 100 * 85):
                                percent = 85
                            if data_user['security']['commands_today'] >= int(limit / 100 * 90):
                                percent = 90
                            if data_user['security']['commands_today'] >= int(limit / 100 * 95):
                                percent = 95
                            if data_user['security']['commands_today'] >= int(limit / 100 * 100):
                                percent = 100
                            if percent >= 80 and not data_user['security']['warns'][str(percent)]:
                                warns = True
                            if warns:
                                _cmd = data_user['security']['commands_today']
                                pe = data_user['security']['commands_today'] * 100 / limit
                                await ctx.send(f'<a:red:525032764211200002>│`VOCE JA ATINGIU` **{pe}%**'
                                               f' `DA SUA COTA DIARIA DE COMANDOS:` **{_cmd}/{limit}** '
                                               f'`SE CONTINUAR ASSIM VAI SER BLOQUEADO POR 72 HORAS.`')
                                query_user["$set"][f"security.warns.{percent}"] = True

                    if data_user['security']['commands_today'] > limit:
                        query_user["$set"]["security.status"] = not data_user['security']['status']
                        query_user["$set"]["security.blocked"] = not data_user['security']['blocked']
                        query_user["$set"]["security.last_blocked"] = dt.today()
                        query_user["$inc"]["security.strikes_to_ban"] = 1
                        channel_ = self.get_channel(737467830571761786)
                        user = self.get_user(data_user["user_id"])
                        await channel_.send(f'```O USUARIO {data_user["user_id"]} {user} ESTAVA POSSIVELMENTE USANDO'
                                            f' MACRO E FOI BLOQUEADO\nNa Data e Hora: {data_}```')

                        await ctx.send(f'<a:red:525032764211200002>│`VOCE FOI BLOQUEADO POR 72 HORAS '
                                       f'POIS EXTRAPOLOU OS LIMITES HOJE`\n<a:red:525032764211200002>'
                                       f' **OBS: VOCE AINDA PODE USAR O BOT, POREM PERDEU OS '
                                       f'PRIVILEGIOS DE GANHAR OS ITENS** `ESSE BLOQUEIO FOI MAIS '
                                       f'RIGIDO,` **SE VOCE CONTINUAR LEVANDO ESSE BLOQUEIO IRÁ SER'
                                       f' BANIDO DE USAR MEUS SERVIÇOS** `AVISO PARA BANIMENTO:` '
                                       f'**{data_user["security"]["strikes_to_ban"]}**/10')

                    if data_user['security']['strikes_to_ban'] > 10:
                        answer = await self.ban_(data_user['user_id'], "BANIDO POR USAR MACRO!")
                        if answer:
                            embed = disnake.Embed(
                                color=disnake.Color.red(),
                                description=f'<:cry:530735037243719687>│`VOCE FOI BANIDO POR USAR MACRO!`'
                                            f' **SE QUISER CONTESTAR ENTRE NO MEU SERVIDOR DE SUPORTE!**')
                            await ctx.send(embed=embed)

                    if m_last_verify < 5 and data_user['security']['commands'] >= 40:
                        data_user["security"]["strikes"] += 1
                        data_user["security"]["strikes_today"] += 1
                        query_user["$inc"]["security.strikes"] = 1
                        query_user["$inc"]["security.strikes_today"] = 1
                        query_user["$set"]["security.commands"] = 0

                        channel_ = self.get_channel(737467830571761786)
                        user = self.get_user(data_user["user_id"])
                        await channel_.send(f'```O USUARIO {data_user["user_id"]} {user} FOI DETECTADO POSSIVELMENTE'
                                            f' USANDO MACRO\nNa Data e Hora: {data_}```')

                        if data_user['security']['strikes'] < 11:
                            await ctx.send(f'<a:red:525032764211200002>│`EI TENHA CALMA VOCE TA '
                                           f'USANDO COMANDOS RAPIDO DEMAIS, SE CONTINUAR ASSIM VAI SER'
                                           f' BLOQUEADO ATE AS 0 HORAS DO DIA DE HOJE.` '
                                           f'<a:red:525032764211200002>'
                                           f'**AVISO {data_user["security"]["strikes"]}/10**')

                        if data_user["security"]["strikes_today"] % 5 == 0:
                            query_user["$set"]["security.self_baned"] = True
                            query_user["$set"]["security.captcha_code"] = CreateCaptcha()
                            await ctx.send(f'<a:red:525032764211200002>│`VOCÊ ACABOU DE LEVAR UMA SERIE DE 5 STRIKES'
                                           f' E POR ISSO FOI BANIDO TEMPORARIAMENTE DA ASHLEY POR SUSPEITA DE USAR'
                                           f' MACRO, PARA VOLTAR A USAR A ASHLEY NORMALMENTE VOCÊ VAI PRECISAR FAZER'
                                           f' UM TESTE E PROVAR QUE NAO É UM ROBÔ, USANDO O COMANDO:` '
                                           f'**ASH CAPTCHA** <a:red:525032764211200002>')

                    elif m_last_verify < 5:
                        query_user["$inc"]["security.commands"] = 1

                    elif m_last_verify >= 5:
                        query_user["$set"]["security.last_verify"] = dt.today()
                        query_user["$set"]["security.blocked"] = False
                        query_user["$set"]["security.commands"] = 0
                        if data_user['security']['strikes'] > 0:
                            query_user["$inc"]["security.strikes"] = -1

                    if data_user['security']['strikes'] == 11:
                        query_user["$set"]["security.status"] = not data_user['security']['status']
                        channel_ = self.get_channel(737467830571761786)
                        user = self.get_user(data_user["user_id"])
                        await channel_.send(f'```O USUARIO {data_user["user_id"]} {user} ESTAVA POSSIVELMENTE USANDO'
                                            f' MACRO E FOI BLOQUEADO\nNa Data e Hora: {data_}```')

                        await ctx.send(f'<a:red:525032764211200002>│`VOCE FOI BLOQUEADO ATE AS 0 '
                                       f'HORAS DO DIA DE HOJE..` <a:red:525032764211200002>'
                                       f'**OBS: VOCE AINDA PODE USAR O BOT, POREM PERDEU OS '
                                       f'PRIVILEGIOS DE GANHAR OS ITENS**')

                # -----------------------------------------------------------------------------------------
                #                                    FIM DO MACRO SYSTEM
                # -----------------------------------------------------------------------------------------

                query_user["$set"]["rank"] = rank_definition(dict(data_user))  # atualização do rank

                a, b, c, d = data_guild['available'], data_guild['vip'], randint(1, 100), data_user['guild_id']
                if a > 0 and b and c < 25 and d == ctx.guild.id:
                    if "$inc" not in query_guild.keys():
                        query_guild["$inc"] = {}
                    query_user["$inc"]["true_money.fragment"] = 1
                    query_guild["$inc"]["available"] = -1
                    await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 {ctx.author.mention} `POR SUA "
                                   f"GUILDA SER VIP VOCÊ ACABOU DE GANHAR` ✨ **1 FRAGMENTO DE BLESSED ETHERNYA** ✨\n"
                                   f"`Disponíveis ainda:` **{data_guild['available']}/15000**")

                cl = await self.db.cd("users")
                await cl.update_one({"user_id": data_user["user_id"]}, query_user)

                if len(query_guild.keys()) > 0:
                    cl = await self.db.cd("guilds")
                    await cl.update_one({"guild_id": data_guild["guild_id"]}, query_guild)

                if str(ctx.command) not in self.no_panning:
                    money = (6, 12)
                    if data_user['config']['vip']:
                        money = (12, 24)
                    msg = await self.db.add_money(ctx, randint(money[0], money[1]), True)
                    _f = "<a:king:853247254744137739> " if data_user['config']['vip'] else ""
                    _guild = self.get_guild(519894833783898112)
                    _member = _guild.get_member(ctx.author.id)
                    if _member is not None:
                        _roles = [r.name for r in _member.roles if r.name != "@everyone"]
                    else:
                        _roles = []
                    _i = "<a:booster:853247252998651934> `BOOSTER MEMBER`" if "Server Booster" in _roles else ""
                    perms = ctx.channel.permissions_for(ctx.me)
                    if perms.send_messages and perms.read_messages:
                        await ctx.send(f"{_f}`Por usar um comando, {_name} tambem ganhou` {msg}{_i}", delete_after=5.0)

                chance = randint(1, 100)
                if chance <= 15:
                    mail_collection = await self.db.cd("mails")
                    all_data = [data async for data in mail_collection.find()]
                    mail = 0
                    for data in all_data:
                        _GB, _BN = data['guilds_benefited'], data['benefited']
                        mail_guild = data_user["guild_id"] in _GB if _GB else None
                        if data['_id'] in data_user["mails"].keys():
                            mail_user = data_user["mails"][data['_id']]
                        else:
                            mail_user = False
                        if data['global'] and not mail_user or ctx.author.id in _BN or mail_guild and not mail_user:
                            if not mail_user:
                                mail += 1
                    if mail > 0:
                        msg = f"<a:blue:525032762256785409> | `VOCÊ TEM {mail} CORRESPONDÊNCIA(S) NÃO LIDOS. PARA " \
                              f"LER SUAS CORRESPONDÊNCIAS, USE O COMANDO ASH MAIL READ.`"
                        await ctx.send(msg)

    async def on_guild_join(self, guild):
        if str(guild.id) in self.blacklist:
            msg = "EU FUI RETIRADA DESSE SERVIDOR SEM MOTIVO APARENTE, LOGO VC DEVE ENTRAR COM UM PEDIDO PARA RETIRAR" \
                  " SEU SERVIDOR (GUILD) DA MINHA LISTA NEGRA, VOCÊ PODE FAZER ISSO ENTRANDO NO MEU SERVIDOR (GUILD)" \
                  " DE SUPORTE E FALANDO COM UM DOS MEUS DESENVOLVEDORES\n LINK DO SERVIDOR:\n " \
                  "https://discord/rYT6QrM"
            try:
                if guild.system_channel is not None:
                    await guild.system_channel.send(msg)
            except disnake.errors.Forbidden:
                pass
            await guild.leave()
        else:
            entrance = self.get_channel(619899848082063372)
            embed = await guild_info(guild)
            await entrance.send(embed=embed)

    async def on_guild_remove(self, guild):
        if guild.id in [901538946222293002, 901750805948932126, 901610392583823413, 904222851647823873]:
            return
        if str(guild.id) not in self.blacklist:
            data = await self.db.get_data("guild_id", guild.id, "guilds")
            if data is not None:
                blacklist = self.get_channel(542134573010518017)
                msg = f"> **{guild.id}:** {guild.name} `ME RETIROU DO SERVIDOR LOGO ENTROU NA BLACKLIST`"
                await blacklist.send(msg)
                embed = await guild_info(guild)
                await blacklist.send(embed=embed)
                await self.ban_(guild.id, msg)
            else:
                blacklist = self.get_channel(542134573010518017)
                msg = f"> **{guild.id}:** {guild.name} `ME RETIROU DO SERVIDOR MAS NÃO TINHA FEITO O RESGISTRO, " \
                      f"ENTÃO NÃO ENTROU NA MINHA BLACKLIST!`"
                await blacklist.send(msg)
                embed = await guild_info(guild)
                await blacklist.send(embed=embed)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.guild is not None:

            ctx = await self.get_context(message)
            if not include(str(ctx.command), ["eval", "jsk", "jishaku"]):
                msg = copy.copy(message)
                msg.content = message.content.lower()
            else:
                msg = copy.copy(message)

            ctx = await self.get_context(msg)
            perms = ctx.channel.permissions_for(ctx.me)
            if not perms.send_messages or not perms.read_messages:
                return

            if ctx.command is not None:
                if not perms.embed_links or not perms.attach_files:
                    return await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                          "LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR CORRETAMENTE!**")
                if message.author.id not in self.testers and self.maintenance:
                    embed = disnake.Embed(color=self.color, description=self.maintenance_msg)
                    return await message.channel.send(embed=embed)

            self.msg_cont += 1

            if message.webhook_id is not None:
                return await self.invoke(ctx)

            if str(message.author.id) not in self.blacklist:
                await self.data.add_experience(message, randint(5, 15))

                run_command = False
                data_guild = await self.db.get_data("guild_id", message.guild.id, "guilds")
                query_u = {"_id": 0, "user_id": 1, "security": 1}
                data_user = await (await self.db.cd("users")).find_one({"user_id": message.author.id}, query_u)
                if data_guild is not None:

                    # sistem do bloqueador de comandos
                    if data_guild['command_locked']['status']:  # modo while_list
                        # bloqueia todos os canais / liberando apenas os que estao na: while_list
                        if message.channel.id in data_guild['command_locked']['while_list']:
                            run_command = True

                    else:  # modo black_list
                        # libera todos os canais / bloqueando apenas os que estao na: black_list
                        if message.channel.id not in data_guild['command_locked']['black_list']:
                            run_command = True

                else:
                    run_command = True
                    if message.guild.system_channel is not None and (self.msg_cont % 10) == 0:
                        if await verify_cooldown(self, f"{message.guild.id}_no_register", 86400):
                            embed = disnake.Embed(
                                color=self.color,
                                description="<a:blue:525032762256785409>│`SEU SERVIDOR AINDA NAO ESTA CADASTRADO USE`"
                                            " **ASH REGISTER GUILD** `PARA QUE EU POSSA PARTICIPAR DAS ATIVIDADES DE "
                                            "VOCES TAMBEM, É MUITO FACIL E RAPIDO. QUALQUER DUVIDA ENTRE EM CONTATO "
                                            "COM MEU SERVIDOR DE SUPORTE` [CLICANDO AQUI](https://discord/rYT6QrM)")
                            try:
                                await message.guild.system_channel.send(embed=embed)
                            except disnake.Forbidden:
                                try:
                                    await message.channel.send(embed=embed)
                                except disnake.Forbidden:
                                    try:
                                        if message.guild.owner is not None:
                                            await message.guild.owner.send(embed=embed)
                                    except disnake.Forbidden:
                                        pass

                if str(ctx.command) in ['channel']:  # exceção dos comandos
                    run_command = True

                if run_command:
                    if msg.content in self.shortcut:
                        msg.content = self.shortcut[message.content.lower()]
                    if self.is_ashley:
                        if data_user is None:
                            await self.process_commands(msg)
                        elif not data_user["security"]["self_baned"]:
                            await self.process_commands(msg)
                        else:
                            if ctx.command is not None:
                                if str(ctx.command) == "captcha":
                                    await self.process_commands(msg)
                                else:
                                    await message.channel.send('<a:red:525032764211200002>│`VOCÊ ACABOU DE LEVAR UMA '
                                                               'SERIE DE 5 STRIKES E POR ISSO FOI BANIDO '
                                                               'TEMPORARIAMENTE DA ASHLEY POR SUSPEITA DE USAR MACRO,'
                                                               ' PARA VOLTAR A USAR A ASHLEY NORMALMENTE VOCÊ VAI '
                                                               'PRECISAR FAZER UM TESTE E PROVAR QUE NAO É UM ROBÔ,'
                                                               ' USANDO O COMANDO:` **ASH CAPTCHA** '
                                                               '<a:red:525032764211200002>')
                    else:
                        if ctx.command is not None:
                            await message.channel.send("<:negate:721581573396496464>|`AINDA ESTOU SENDO INICIADA, "
                                                       "AGUARDE MAIS UM POUCO...!`", delete_after=5.0)
                else:
                    if ctx.command is not None:
                        await message.channel.send("<:alert:739251822920728708>|`NAO POSSO EXECUTAR COMANDOS NESSE"
                                                   " CANAL!`\n**CASO QUERIA ALTERAR ESSA CONFIGURAÇÃO, USE O COMANDO "
                                                   "ASH CHANNEL**")

            if message.channel.id == 837054554637467648:  # canal de sugestões da ASHLEY!
                await message.add_reaction("<:confirmed:721581574461587496>")
                await message.add_reaction("<:negate:721581573396496464>")

        else:
            await self.process_commands(message)

    @staticmethod
    def get_ram(special=False):
        proc = psutil.Process()
        with proc.oneshot():
            try:
                _mem = proc.memory_full_info()
            except psutil.AccessDenied:
                pass
        mem_proc = humanize.naturalsize(_mem.rss)
        mem = psutil.virtual_memory()
        _memory = f"{mem.used / 0x40_000_000:.2f}/{mem.total / 0x40_000_000:.2f}GB ({mem.percent}%) in Machine.\n" \
                  f"{mem_proc} in Ashley!"
        return _memory if not special else mem_proc

    async def web_hook_rpg(self, ctx, wh_avatar_url, wh_name, content, pet_name):
        perms = ctx.channel.permissions_for(ctx.me)
        if not perms.manage_webhooks:
            if not perms.send_messages:
                return
            return await ctx.send(f'<:negate:721581573396496464>│`Eu não tenho a permissão de:` '
                                  f'**Gerenciar Webhooks**')

        emoji = choice(self.config['emojis']['ashley'])
        guild = self.get_guild(519894833783898112)
        link = [emo for emo in guild.emojis if str(emo) == emoji][0].url

        query = {"_id": 0, "guild_id": 1, "webhook": 1}
        data_guild = await (await self.db.cd("guilds")).find_one({"guild_id": ctx.guild.id}, query)
        query_guild = {"$set": {}}
        if data_guild['webhook'] is None:
            avatar = open(wh_avatar_url, 'rb')
            _webhook = await ctx.channel.create_webhook(name=wh_name, avatar=avatar.read())
            query_guild["$set"]["webhook"] = _webhook.url
            cl = await self.db.cd("guilds")
            await cl.update_one({"user_id": data_guild["guild_id"]}, query_guild, upsert=False)

        pet = f"{pet_name} do {ctx.author.name} disse:\n```{content}```"
        msg = f"{pet if pet_name != 'Ashley' else content}"
        embed = disnake.Embed(colour=random_color(), description=msg, timestamp=dt.utcnow())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=link)

        webhook = Webhook.from_url(data_guild['webhook'], session=self.session)
        g_perms = ctx.me.guild_permissions
        if g_perms.manage_webhooks:
            try:
                _channel = [h for h in await ctx.channel.webhooks() if h == webhook][0].channel
                if _channel.id != ctx.channel.id:
                    await ctx.send(f"<:alert:739251822920728708>│`Sua resposta:` {_channel.mention}")
            except IndexError:
                pass
        _url = wh_avatar_url if validate_url(wh_avatar_url) else None
        await webhook.send(embed=embed, username=wh_name, avatar_url=_url)


def main_bot():
    desc = f"Um bot de assistencia para servidores criado por: Denky#5960\n" \
           f"**Adicione para seu servidor:**: {config['config']['default_link']}\n" \
           f"**Servidor de Origem**: {config['config']['default_invite']}\n"

    intents = disnake.Intents.default()
    intents.members = True
    bot = Ashley(command_prefix=_auth['prefix'], description=desc, pm_help=True, intents=intents)
    bot.remove_command('help')
    emojis, cont = {"ON": "🟢", "IDLE": "🟡", "OFF": "🔴", "VIP": "🟣"}, 0

    print("\033[1;35m( >> ) | Iniciando a ASHLEY!\033[m\n")
    print("\033[1;35m( >> ) | Iniciando o carregamento de extensões comuns...\033[m")

    if bot.maintenance:
        f = open("maintenance.txt", "r")
    else:
        f = open("modulos.txt", "r")

    for name in f.readlines():
        if len(name.strip()) > 0:
            try:
                if '@' not in name.strip() and '#' not in name.strip():
                    bot.load_extension(name.strip())
                    if name.strip() not in bot.vip_cog:
                        bot.data_cog[name.strip()] = emojis['ON']
                    else:
                        bot.data_cog[name.strip()] = emojis['VIP']
                    cont += 1
                else:
                    if '#' not in name.strip():
                        print(f'\033[1;36m( ☢️ ) | Cog: \033[1;34m{name.strip()}\033[1;36m não foi carregada!\33[m')
                        bot.data_cog[name.strip()] = emojis['OFF']
            except Exception as e:
                if '#' not in name.strip():
                    print(f"\033[1;31m( ❌ ) | Cog: \033[1;34m{name}\033[1;31m teve um [Erro] : \033[1;35m{e}\33[m")
                    bot.data_cog[name.strip()] = emojis['IDLE']
                    traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                continue
    f.close()

    print("\033[1;35m( >> ) | Finalizado o carregamento de extensões comuns...\033[m")
    print("\033[1;35m( >> ) | Iniciando o carregamento de extensões SLASHS...\033[m")

    f = open("slashs.txt", "r")
    for name in f.readlines():
        if len(name.strip()) > 0:
            try:
                if '@' not in name.strip() and '#' not in name.strip():
                    bot.load_extension(name.strip())
                    if name.strip() not in bot.vip_cog:
                        bot.data_cog[name.strip()] = emojis['ON']
                    else:
                        bot.data_cog[name.strip()] = emojis['VIP']
                    cont += 1
                else:
                    if '#' not in name.strip():
                        print(f'\033[1;36m( ☢️ ) | Cog: \033[1;34m{name.strip()}\033[1;36m não foi carregada!\33[m')
                        bot.data_cog[name.strip()] = emojis['OFF']
            except Exception as e:
                if '#' not in name.strip():
                    print(f"\033[1;31m( ❌ ) | Cog: \033[1;34m{name}\033[1;31m teve um [Erro] : \033[1;35m{e}\33[m")
                    bot.data_cog[name.strip()] = emojis['IDLE']
                    traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                continue
    f.close()

    print("\033[1;35m( >> ) | Finalizado o carregamento de extensões SLASH...\033[m")
    print("\033[1;35m( >> ) | Iniciando o carregamento de extensões EXTRAS...\033[m")
    bot.load_extension("jishaku")  # load extenção JISHAKU
    print('\033[1;33m( 🔶 ) | A cog \033[1;34mJISHAKU\033[1;33m foi carregada com sucesso!\33[m')
    print("\033[1;35m( >> ) | Finalizado o carregamento de extensões EXTRAS...\033[m")
    print(f"\033[1;35m( ✔ ) | {cont + 1}/{len(bot.data_cog.keys()) + 1} extensões foram carregadas!\033[m")
    return bot, _auth['_t__ashley']


if __name__ == "__main__":
    ashley, token = main_bot()
    ashley.run(token)
