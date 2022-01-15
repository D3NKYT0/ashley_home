import json
import disnake
import datetime
from random import randint
from disnake.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient as Client
from resources.utility import parse_duration, quant_etherny, create_id
from resources.structure import user_data_structure, guild_data_structure

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())

with open("data/config.json") as config:
    config = json.loads(config.read())

epoch = datetime.datetime.utcfromtimestamp(0)


class Database(object):
    def __init__(self, bot):
        self.bot = bot
        self._connect = Client(_auth['db_url'], connectTimeoutMS=30000)
        self._database = self._connect[_auth['db_name']]

    async def cd(self, collections):  # atualizado no banco de dados
        return self._database[collections]

    async def push_data(self, data, db_name):  # atualizado no banco de dados
        db = self._database[db_name]
        await db.insert_one(data)

    async def delete_data(self, data, db_name):  # atualizado no banco de dados
        db = self._database[db_name]
        await db.delete_one(data)

    async def update_data(self, data, update, db_name):  # DESATUALIZADO
        db = self._database[db_name]
        await db.update_one({'_id': data['_id']}, {'$set': update}, upsert=False)

    async def update_all_data(self, search, update, db_name):  # DESATUALIZADO
        db = self._database[db_name]
        await db.update_many(search, {'$set': update})

    async def get_data(self, key, value, db_name):  # DESATUALIZADO
        db = self._database[db_name]
        data = await db.find_one({key: value})
        return data

    async def get_all_data(self, db_name):  # DESATUALIZADO
        db = self._database[db_name]
        all_data = [data async for data in db.find()]
        return all_data

    async def get_announcements(self):  # DESATUALIZADO
        db = self._database["announcements"]
        all_data = [data async for data in db.find()]
        return all_data

    # ----------------------------------- ============================ -----------------------------------
    #                               ITERAÇÕES DIRETAS COM O BANCO DE DADOS
    # ---------------------------------- ============================ -----------------------------------

    async def add_user(self, ctx):  # atualizado no banco de dados
        if await self.get_data("user_id", ctx.author.id, "users") is None:
            _data = user_data_structure
            _data["_id"] = create_id()
            _data["user_id"] = ctx.author.id
            _data["guild_id"] = ctx.guild.id
            _data["config"]["create_at"] = datetime.datetime.today()
            await self.push_data(_data, "users")

    async def add_guild(self, guild, data):  # atualizado no banco de dados
        _data = guild_data_structure
        _data['_id'] = create_id()
        _data['guild_id'] = guild.id
        _data["data"]["create_at"] = datetime.datetime.today()

        _data['log_config']['log'] = data.get("log", False)
        _data['log_config']['log_channel_id'] = data.get("log_channel_id", None)

        _data['ia_config']["auto_msg"] = data.get("auto_msg", False)

        _data['bot_config']["ash_draw"] = data.get("ash_draw", False)
        _data['bot_config']["ash_draw_id"] = data.get("ash_draw_id", None)

        _data['func_config']["cont_users"] = data.get("cont_users", False)
        _data['func_config']["cont_users_id"] = data.get("cont_users_id", None)
        _data['func_config']["member_join"] = data.get("member_join", False)
        _data['func_config']["member_join_id"] = data.get("member_join_id", None)
        _data['func_config']["member_remove"] = data.get("member_remove", False)
        _data['func_config']["member_remove_id"] = data.get("member_remove_id", None)

        if await self.get_data("guild_id", guild.id, "guilds") is None:
            await self.push_data(_data, "guilds")

    async def take_money(self, ctx, amount: int = 0):  # atualizado no banco de dados
        query = {"_id": 0, "user_id": 1, "guild_id": 1, "treasure.money": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        query = {"_id": 0, "guild_id": 1, "data.total_money": 1}
        data_guild_native = await (await self.bot.db.cd("guilds")).find_one({"guild_id": data_user['guild_id']}, query)

        data_user['treasure']['money'] -= amount
        if data_guild_native is not None:
            data_guild_native['data']['total_money'] -= amount

            cl = await self.bot.db.cd("guilds")
            query = {"$set": {"data.total_money": data_guild_native['data']['total_money']}}
            await cl.update_one({"guild_id": data_guild_native["guild_id"]}, query, upsert=False)

        cl = await self.bot.db.cd("users")
        query = {"$set": {"treasure.money": data_user['treasure']['money']}}
        await cl.update_one({"user_id": data_user["user_id"]}, query, upsert=False)

        a = '{:,.2f}'.format(float(amount))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')

        return f"<:confirmed:721581574461587496>│**R$ {d}** `DE` **Ethernyas** `RETIRADOS COM SUCESSO!`"

    async def give_money(self, ctx, amount: int = 0, user=None, guilds=None):  # atualizado no banco de dados
        if ctx is not None:
            user_id = user if user is not None else ctx.author.id
        else:
            user_id = user

        query = {"_id": 0, "user_id": 1, "guild_id": 1, "treasure.money": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": user_id}, query)
        query = {"_id": 0, "guild_id": 1, "data.total_money": 1}

        try:
            guild = data_user['guild_id']
            data_guild_native = await (await self.bot.db.cd("guilds")).find_one({"guild_id": guild}, query)
        except TypeError:
            if ctx is not None:
                guild = ctx.guild.id
                data_guild_native = await (await self.bot.db.cd("guilds")).find_one({"guild_id": guild}, query)
            else:
                guild = guilds
                data_guild_native = await (await self.bot.db.cd("guilds")).find_one({"guild_id": guilds}, query)

        data_user['treasure']['money'] += amount
        if data_guild_native is not None:
            data_guild_native['data']['total_money'] += amount

            cl = await self.bot.db.cd("guilds")
            query = {"$set": {"data.total_money": data_guild_native['data']['total_money']}}
            await cl.update_one({"guild_id": guild}, query, upsert=False)

        cl = await self.bot.db.cd("users")
        query = {"$set": {"treasure.money": data_user['treasure']['money']}}
        await cl.update_one({"user_id": data_user["user_id"]}, query, upsert=False)

        a = '{:,.2f}'.format(float(amount))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')

        if user is not None and ctx is not None:
            _user = self.bot.get_user(user)
            try:
                await _user.send(f"<:confirmed:721581574461587496>│`Voce acabou de vender um item no mercado, "
                                 f"e recebeu o valor de` **R$ {d}** `Ethernyas. Aproveite e olhe sua lojinha.`")
            except disnake.errors.Forbidden:
                pass
            except AttributeError:
                pass

        return f"<:confirmed:721581574461587496>│**R$ {d}** `DE` **Ethernyas** `ADICIONADOS COM SUCESSO!`"

    async def add_money(self, ctx, amount, ext=False):  # atualizado no banco de dados

        query = {"_id": 0, "user_id": 1, "security": 1, "user": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        change, msg, answer = randint(1, 100), None, quant_etherny(amount)
        if data_user is not None:

            if not data_user['security']['status']:
                return '`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'

            if data_user['user']['ranking'] == 'Bronze':
                await self.add_type(ctx, (answer['amount'] * 1), answer['list'])

                a = '{:,.2f}'.format(float(answer['amount']))
                b = a.replace(',', 'v')
                c = b.replace('.', ',')
                d = c.replace('v', '.')

                msg = f"**R${d}** de `Ethernyas`"
            elif data_user['user']['ranking'] == 'Silver':
                if change <= 75:
                    await self.add_type(ctx, (answer['amount'] * 1), answer['list'])

                    a = '{:,.2f}'.format(float(answer['amount']))
                    b = a.replace(',', 'v')
                    c = b.replace('.', ',')
                    d = c.replace('v', '.')

                    msg = f"**R${d}** de `Ethernyas`"
                else:
                    answer['list'][0] = (answer['list'][0] * 2)
                    answer['list'][1] = (answer['list'][1] * 2)
                    answer['list'][2] = (answer['list'][2] * 2)
                    await self.add_type(ctx, (answer['amount'] * 2), answer['list'])

                    a = '{:,.2f}'.format(float(answer['amount'] * 2))
                    b = a.replace(',', 'v')
                    c = b.replace('.', ',')
                    d = c.replace('v', '.')

                    msg = f"**R${d}** de `Ethernyas`"
            elif data_user['user']['ranking'] == 'Gold':
                if change <= 75:
                    await self.add_type(ctx, (answer['amount'] * 1), answer['list'])

                    a = '{:,.2f}'.format(float(answer['amount']))
                    b = a.replace(',', 'v')
                    c = b.replace('.', ',')
                    d = c.replace('v', '.')

                    msg = f"**R${d}** de `Ethernyas`"
                elif change <= 95:
                    answer['list'][0] = (answer['list'][0] * 2)
                    answer['list'][1] = (answer['list'][1] * 2)
                    answer['list'][2] = (answer['list'][2] * 2)
                    await self.add_type(ctx, (answer['amount'] * 2), answer['list'])

                    a = '{:,.2f}'.format(float(answer['amount'] * 2))
                    b = a.replace(',', 'v')
                    c = b.replace('.', ',')
                    d = c.replace('v', '.')

                    msg = f"**R${d}** de `Ethernyas`"
                else:
                    answer['list'][0] = (answer['list'][0] * 3)
                    answer['list'][1] = (answer['list'][1] * 3)
                    answer['list'][2] = (answer['list'][2] * 3)
                    await self.add_type(ctx, (answer['amount'] * 3), answer['list'])

                    a = '{:,.2f}'.format(float(answer['amount'] * 3))
                    b = a.replace(',', 'v')
                    c = b.replace('.', ',')
                    d = c.replace('v', '.')

                    msg = f"**R${d}** de `Ethernyas`"
            if ext:
                msg += f"\n`e a quantidade de pedras abaixo:` " \
                       f"**{answer['list'][0]}**  {self.bot.money[0]} | " \
                       f"**{answer['list'][1]}**  {self.bot.money[1]} | " \
                       f"**{answer['list'][2]}**  {self.bot.money[2]}\n"
            return msg

    async def add_reward(self, ctx, list_, one=False, wave=False):  # atualizado no banco de dados
        query = {"_id": 0, "user_id": 1, "security": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        query_user = {"$inc": {}}

        if not data_user['security']['status']:
            return '`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'

        response, items, reward_list = '`Caiu pra você:` \n\n' if not wave else '', dict(), list()
        for item in list_:
            amount = randint(1, 3) if not one else 1

            try:
                items[item] += amount
            except KeyError:
                items[item] = amount

        for k, v in items.items():
            query_user["$inc"][f"inventory.{k}"] = v

        for it in items.keys():
            if wave:
                if len(response) <= 900:
                    response += f"{self.bot.items[it][0]} **{items[it]}** `{self.bot.items[it][1].upper()}`\n"
                else:
                    reward_list.append(response)
                    response = f"{self.bot.items[it][0]} **{items[it]}** `{self.bot.items[it][1].upper()}`\n"
            else:
                response += f"{self.bot.items[it][0]} **{items[it]}** `{self.bot.items[it][1].upper()}`\n"

        cl = await self.bot.db.cd("users")
        await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)
        response += '```dê uma olhada no seu inventario com o comando: "ash i"```'
        if wave:
            reward_list.append(response)
            return reward_list
        return response

    async def add_rpg(self, ctx, list_, one=False, amount=0):  # atualizado no banco de dados
        query = {"_id": 0, "user_id": 1, "security": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        query_user = {"$inc": {}}

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))
        rew = None

        if not data_user['security']['status']:
            return '`USUARIO DE MACRO / OU USANDO COMANDOS RAPIDO DEMAIS` **USE COMANDOS COM MAIS CALMA JOVEM...**'

        response = '`Caiu pra você:` \n'
        for item in list_:
            tot = randint(1, 3 if amount == 0 else amount) if not one else 1
            query_user["$inc"][f"rpg.items.{item}"] = tot

            for i in equips_list:
                if i[0] == item:
                    rew = i[1]

            if rew is not None:
                response += f"{rew['icon']} `{tot}` `{rew['name']}`\n"
        cl = await self.bot.db.cd("users")
        await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)
        response += '```dê uma olhada no seu inventario de equipamentos com o comando: "ash es"```'
        return response

    async def add_type(self, ctx, amount, ethernya):  # atualizado no banco de dados
        # DATA DO MEMBRO
        query = {"_id": 0, "user_id": 1, "guild_id": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        query_user = {"$inc": {}}
        query_user["$inc"]["treasure.bronze"] = ethernya[0] * 2
        query_user["$inc"]["treasure.silver"] = ethernya[1] * 2
        query_user["$inc"]["treasure.gold"] = ethernya[2] * 2
        query_user["$inc"]["treasure.money"] = amount * 2
        cl = await self.bot.db.cd("users")
        await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

        # DATA NATIVA DO SERVIDOR
        query = {"_id": 0, "guild_id": 1}
        data_guild_native = await (await self.bot.db.cd("guilds")).find_one({"guild_id": data_user['guild_id']}, query)
        if data_guild_native is not None:
            query_guild = {"$inc": {}}
            query_guild["$inc"]["data.total_bronze"] = ethernya[0] * 2
            query_guild["$inc"]["data.total_silver"] = ethernya[1] * 2
            query_guild["$inc"]["data.total_gold"] = ethernya[2] * 2
            query_guild["$inc"]["data.total_money"] = amount * 2
            cl = await self.bot.db.cd("guilds")
            await cl.update_one({"guild_id": data_guild_native["guild_id"]}, query_guild, upsert=False)

        # DATA DO SERVIDOR ATUAL
        query = {"_id": 0, "guild_id": 1}
        data_guild = await (await self.bot.db.cd("guilds")).find_one({"guild_id": ctx.guild.id}, query)
        query_guild2 = {"$inc": {}}
        query_guild2["$inc"]["data.total_bronze"] = ethernya[0] * 2
        query_guild2["$inc"]["data.total_silver"] = ethernya[1] * 2
        query_guild2["$inc"]["data.total_gold"] = ethernya[2] * 2
        query_guild2["$inc"]["data.total_money"] = amount * 2
        cl = await self.bot.db.cd("guilds")
        await cl.update_one({"guild_id": data_guild["guild_id"]}, query_guild2, upsert=False)

    async def is_registered(self, ctx, **kwargs):  # atualizado no banco de dados

        if ctx.message.webhook_id is not None:
            return True

        if ctx.guild is not None:
            query = {"_id": 0, "guild_id": 1, "vip": 1}
            data_guild = await (await self.bot.db.cd("guilds")).find_one({"guild_id": ctx.guild.id}, query)

            query = {"_id": 0, "user_id": 1, "config": 1, "cooldown": 1, "user": 1}
            data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
            query_user = {"$set": {}}

            if data_guild is None:
                raise commands.CheckFailure('<:alert:739251822920728708>│`Sua guilda ainda não está registrada, por '
                                            'favor digite:` **ash register guild** `para cadastrar sua guilda '
                                            'no meu` **banco de dados!**')

            if data_user is not None:
                if kwargs.get("cooldown"):
                    if str(ctx.command) in data_user["cooldown"].keys():
                        tt = (datetime.datetime.utcnow() - epoch).total_seconds()
                        time_diff = tt - data_user["cooldown"][str(ctx.command)]
                        time_left = kwargs.get("time") - time_diff
                        if time_diff < kwargs.get("time"):
                            if str(ctx.command) == "pick":
                                now = datetime.datetime.now()
                                minutes = 60 - now.minute
                                s = "s" if minutes > 1 else ""
                                raise commands.CheckFailure(f'<:alert:739251822920728708>│**Aguarde**: `Você deve '
                                                            f'esperar` **{minutes} minuto{s}** `para usar esse comando'
                                                            f' novamente!`')

                            raise commands.CheckFailure(f'<:alert:739251822920728708>│**Aguarde**: `Você deve '
                                                        f'esperar` **{{}}** `para usar esse comando '
                                                        f'novamente!`'.format(parse_duration(int(time_left))))

                    gc = self.bot.guilds_commands[ctx.guild.id]
                    if gc > 50 and str(ctx.command) == "daily work" or str(ctx.command) != "daily work":

                        limit = 20 if data_user["config"]["vip"] else 10
                        limit += 20 if self.bot.event_special else limit
                        t1, t2 = str(ctx.command) == "pick", (data_user["user"]["stickers"] + 1) % limit == 0
                        t3 = str(ctx.command) != "pick"

                        if t1 and t2 or t3:
                            tt = (datetime.datetime.utcnow() - epoch).total_seconds()
                            query_user["$set"][f"cooldown.{str(ctx.command)}"] = tt
                            cl = await self.bot.db.cd("users")
                            await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

                if kwargs.get("g_vip") and data_guild['vip']:
                    if kwargs.get("vip") and data_user['config']['vip']:
                        return True
                    if kwargs.get("vip") and not data_user['config']['vip']:
                        raise commands.CheckFailure("<:alert:739251822920728708>│`APENAS USUARIOS COM VIP ATIVO "
                                                    "PODEM USAR ESSE COMANDO`\n **Para saber como ser vip use o"
                                                    " comando ASH VIP**")
                    return True
                elif kwargs.get("g_vip") and data_guild['vip'] is False:
                    if str(ctx.command) in ["guild convert", "guild reward"] and ctx.guild.id == 519894833783898112:
                        pass
                    else:
                        raise commands.CheckFailure("<:alert:739251822920728708>│`APENAS SERVIDORES COM VIP ATIVO "
                                                    "PODEM USAR ESSE COMANDO`\n **Para saber como ser vip use o"
                                                    " comando ASH VIP**")

                if kwargs.get("vip") and data_user['config']['vip']:
                    return True
                elif kwargs.get("vip") and data_user['config']['vip'] is False:
                    raise commands.CheckFailure("<:alert:739251822920728708>│`APENAS USUARIOS COM VIP ATIVO "
                                                "PODEM USAR ESSE COMANDO`\n **Para saber como ser vip use o"
                                                " comando ASH VIP**")

                return True
            else:
                raise commands.CheckFailure(f'<:alert:739251822920728708>│`Você ainda não está registrado, '
                                            f'por favor use` **ash register**.')
        else:
            return True


class DataInteraction(object):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    async def add_sts(self, member, status, amount=None):  # atualizado no banco de dados
        cl = await self.bot.db.cd("users")
        if amount is None:
            query = {"$inc": {}}
            for sts in status:
                query["$inc"][f"statistic.{sts}"] = 1
        else:
            query = {"$inc": {f"statistic.{status}": amount}}
        await cl.update_one({"user_id": member.id}, query)

    async def add_experience(self, message, exp):  # atualizado no banco de dados

        run_command = False
        query = {"_id": 0, "guild_id": 1, "command_locked": 1, "func_config": 1}
        data_guild = await (await self.bot.db.cd("guilds")).find_one({"guild_id": message.guild.id}, query)

        if data_guild is not None:
            if data_guild['command_locked']['status']:
                if message.channel.id in data_guild['command_locked']['while_list']:
                    run_command = True
            else:
                if message.channel.id not in data_guild['command_locked']['black_list']:
                    run_command = True

        query = {"_id": 0, "user_id": 1, "user": 1, "cooldown": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": message.author.id}, query)
        query_user = {}

        if data_user is None:
            return

        if data_user["user"]['xp_time'] is None:
            query_user["$set"] = dict()
            data_user["user"]['xp_time'] = datetime.datetime.today()
            query_user["$set"]["user.xp_time"] = datetime.datetime.today()

        if (datetime.datetime.today() - data_user["user"]['xp_time']).seconds > 5:
            query_user["$inc"] = dict()
            query_user["$inc"]["user.experience"] = exp * data_user['user']['level']

            if "$set" not in query_user.keys():
                query_user["$set"] = dict()
            data_user["user"]['xp_time'] = datetime.datetime.today()
            query_user["$set"]["user.xp_time"] = datetime.datetime.today()

        if 10 < data_user['user']['level'] < 20 and data_user['user']['ranking'] is not None:
            if randint(1, 200) == 200 and data_user['user']['ranking'] == "Bronze":
                if "$set" not in query_user.keys():
                    query_user["$set"] = dict()
                if "$inc" not in query_user.keys():
                    query_user["$inc"] = dict()
                query_user["$set"]["user.ranking"] = "Silver"
                query_user["$inc"]["inventory.coins"] = 1000

                if run_command:
                    if message.guild.id != 425864977996578816:
                        if data_guild['func_config']['level_up_channel']:
                            channel = self.bot.get_channel(data_guild['func_config']['level_up_channel_id'])
                            if channel is not None:
                                await channel.send('🎊 **PARABENS** 🎉 {} `você subiu seu ranking` **SOCIAL** '
                                                   '`e ganhou a` **chance** `de garimpar mais ethernyas '
                                                   'e` **+1000** `Fichas`'.format(message.author))

        elif 20 < data_user['user']['level'] < 30 and data_user['user']['ranking'] is not None:
            if randint(1, 200) == 200 and data_user['user']['ranking'] == "Silver":
                if "$set" not in query_user.keys():
                    query_user["$set"] = dict()
                if "$inc" not in query_user.keys():
                    query_user["$inc"] = dict()
                query_user["$set"]["user.ranking"] = "Gold"
                query_user["$inc"]["inventory.coins"] = 2000

                if run_command:
                    if message.guild.id != 425864977996578816:
                        if data_guild['func_config']['level_up_channel']:
                            channel = self.bot.get_channel(data_guild['func_config']['level_up_channel_id'])
                            if channel is not None:
                                await channel.send('🎊 **PARABENS** 🎉 {} `você subiu seu ranking` **SOCIAL** `e ganhou'
                                                   ' a` **chance** `de garimpar mais eternyas do que o ranking passado'
                                                   ' e` **+2000** `Fichas`'.format(message.author))

        experience = data_user['user']['experience']
        lvl_anterior = data_user['user']['level']
        lvl_now = int(experience ** 0.2)
        if lvl_anterior < lvl_now:
            if "$set" not in query_user.keys():
                query_user["$set"] = dict()
            if "$inc" not in query_user.keys():
                query_user["$inc"] = dict()
            query_user["$set"]["user.level"] = lvl_now
            query_user["$inc"]["inventory.coins"] = 200

            if run_command:
                if message.guild.id != 425864977996578816:
                    if data_guild['func_config']['level_up_channel']:
                        channel = self.bot.get_channel(data_guild['func_config']['level_up_channel_id'])
                        if channel is not None:
                            await message.channel.send('🎊 **PARABENS** 🎉 {} `você upou seu level social para o'
                                                       ' level` **{}** `e ganhou` **+200** '
                                                       '`Fichas`'.format(message.author, lvl_now))

        if len(query_user.keys()) > 0:
            cl = await self.bot.db.cd("users")
            await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

    async def add_xp(self, ctx, exp):  # atualizado no banco de dados
        _LEVEL_MAXIMO = 100  # para alterar o level maximo (apenas mude esse level)
        _limit = _LEVEL_MAXIMO - 1
        query, query_user = {"_id": 0, "user_id": 1, "rpg": 1}, dict()
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        _name = data_user['rpg']["class_now"]
        _class = data_user["rpg"]["sub_class"][_name]
        if _class['level'] < _LEVEL_MAXIMO:
            if not data_user["rpg"]["sub_class"][_name]["level_max"]:  # verifica se o player esta no lvl maximo
                if "$inc" not in query_user.keys():
                    query_user["$inc"] = dict()
                _class['xp'] += exp
                query_user["$inc"][f"rpg.sub_class.{_name}.xp"] = exp
                lvl, xp = _class['level'], _class['xp']
                _class['xp'] = ((lvl + 1) ** 5) - 1 if int(xp ** 0.2) == _LEVEL_MAXIMO else xp
                experience, lvl_anterior = _class['xp'], _class['level']
                lvl_now = int(experience ** 0.2) if lvl_anterior > 1 else 2
                if lvl_anterior < lvl_now and not _class['level_max']:
                    if "$set" not in query_user.keys():
                        query_user["$set"] = dict()

                    pdh = lvl_now - lvl_anterior if lvl_now - lvl_anterior > 0 else 1
                    coins = pdh * 200
                    query_user["$set"][f"rpg.sub_class.{_name}.level"] = lvl_now if lvl_now < _LEVEL_MAXIMO else _limit
                    query_user["$inc"][f"rpg.sub_class.{_name}.status.pdh"] = pdh if lvl_now < _LEVEL_MAXIMO else 0
                    if lvl_now < _LEVEL_MAXIMO:
                        query_user["$inc"]["inventory.coins"] = coins

                    if lvl_now == 26 and lvl_now < _LEVEL_MAXIMO:
                        mention = ctx.author.mention
                        msg = f'🎊 **PARABENS** 🎉 {mention} `você upou no RPG para o level` **{lvl_now},** ' \
                              f'`ganhou` **+{coins}** `Fichas e +{pdh} PDH (olhe o comando \"ash skill\")`\n' \
                              f'```Markdown\n[>>]: AGORA VOCE TAMBEM GANHOU O BONUS DE STATUS DA SUA CLASSE```'
                        img = "https://i.gifer.com/143t.gif"

                    elif lvl_now < _LEVEL_MAXIMO:
                        mention = ctx.author.mention
                        msg = f'🎊 **PARABENS** 🎉 {mention} `você upou no RPG para o level` **{lvl_now},** ' \
                              f'`ganhou` **+{coins}** `Fichas e +{pdh} PDH (olhe o comando \"ash skill\")`'
                        img = "https://i.pinimg.com/originals/7e/58/1c/7e581c87b8cf5cdae354258789b2fc32.gif"

                    else:
                        query_user["$set"][f"rpg.sub_class.{_name}.level_max"] = True
                        mention = ctx.author.mention
                        msg = f'🎊 **PARABENS** 🎉 {mention} `você upou no RPG para o level` **MAXIMO,** ' \
                              f'`ganhou` **+{coins}** `Fichas (olhe o comando \"ash skill\")`\n' \
                              f'```Markdown\n[>>]: AGORA VOCE TAMBEM GANHOU O BONUS DE STATUS DA SUA CLASSE```'
                        img = "https://i.gifer.com/143t.gif"

                    embed = disnake.Embed(color=self.bot.color, description=f'<:confirmed:721581574461587496>│{msg}')
                    embed.set_image(url=img)
                    await ctx.send(embed=embed)

        if len(query_user.keys()) > 0:
            cl = await self.bot.db.cd("users")
            await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)

    async def add_announcement(self, ctx, announce):  # atualizado no banco de dados
        date = datetime.datetime(*datetime.datetime.utcnow().timetuple()[:6])
        data = {
            "_id": ctx.author.id,
            "data": {
                "status": False,
                "announce": announce,
                "date": "{}".format(date)
            }
        }
        await self.db.push_data(data, "announcements")
        await ctx.send('<:confirmed:721581574461587496>│`Anuncio cadastrado com sucesso!`\n```AGUARDE APROVAÇÃO```')
        pending = self.bot.get_channel(619969149791240211)
        msg = f"{ctx.author.id}: **{ctx.author.name}** `ADICIONOU UM NOVO ANUNCIO PARA APROVAÇÃO!`"
        await pending.send(msg)

    # ----------------------------------- ============================ -----------------------------------
    #                                              TOP ASHLEY
    # ----------------------------------- ============================ -----------------------------------

    async def get_rank_level(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "user.level": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("user.experience", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds['user']['level'])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['user']['level'])}"
        return rank

    async def get_rank_money(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "treasure.money": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("treasure.money", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.2f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["treasure"]["money"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > R$ {money(data_user['treasure']['money'])}"
        return rank

    async def get_rank_gold(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "treasure.gold": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("treasure.gold", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["treasure"]["gold"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['treasure']['gold'])}"
        return rank

    async def get_rank_silver(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "treasure.silver": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("treasure.silver", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["treasure"]["silver"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['treasure']['silver'])}"
        return rank

    async def get_rank_bronze(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "treasure.bronze": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("treasure.bronze", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["treasure"]["bronze"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['treasure']['bronze'])}"
        return rank

    async def get_rank_point(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "config.points": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("config.points", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["config"]["points"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['config']['points'])}"
        return rank

    async def get_rank_commands(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "user.commands": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("user.commands", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["user"]["commands"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['user']['commands'])}"
        return rank

    async def get_rank_rpg(self, limit, ctx, _class):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, f"rpg.sub_class.{_class}.level": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([(f"rpg.sub_class.{_class}.xp", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds, classe):
            return money(ds["rpg"]["sub_class"][classe]["level"])

        rk = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x], _class)}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rk += f"\n--------------------------------------------------------------------\n" \
              f"{position}º: {player} > {money(data_user['rpg']['sub_class'][_class]['level'])}"
        return rk

    async def get_rank_raid(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "user.raid": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("user.raid", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["user"]["raid"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['user']['raid'])}"
        return rank

    async def get_rank_blessed(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "true_money.blessed": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("true_money.blessed", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["true_money"]["blessed"])

        rk = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rk += f"\n--------------------------------------------------------------------\n" \
              f"{position}º: {player} > {money(data_user['true_money']['blessed'])}"

        return rk

    async def get_rank_event(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "guild_id": 1, "event.points": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("guilds")).find({}, f).sort([("event.points", -1)]))]
        position = int([int(_["guild_id"]) for _ in dt].index(ctx.guild.id)) + 1

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def get_guild(bot, _dt):
            if bot.get_guild(int(_dt["guild_id"])) is not None:
                return str(self.bot.get_guild(int(_dt["guild_id"]))).replace("'", "").replace("#", "_")
            else:
                return "Servidor Fantasma"

        rank = "\n".join([f"{x + 1}" + "º: " + get_guild(self.bot, dt[x]) + " > "
                          + str(money(dt[x]["event"]["points"])) for x in range(limit)])
        data_user = await self.db.get_data("guild_id", ctx.guild.id, "guilds")
        player = str(ctx.guild).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['event']['points'])}"
        return rank

    async def get_rank_fragment(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "true_money.fragment": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("true_money.fragment", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            return money(ds["true_money"]["fragment"])

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > {money(data_user['true_money']['fragment'])}"
        return rank

    async def get_rank_bitash(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "true_money.bitash": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("true_money.bitash", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds, bot):
            return bot.broker.format_bitash(ds["true_money"]["bitash"])

        rk = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x], self.bot)}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rk += f"\n--------------------------------------------------------------------\n" \
              f"{position}º: {player} > {money(data_user['true_money']['bitash'])}"
        return rk

    async def get_rank_pvp(self, limit, ctx):  # atualizado no banco de dados

        f = {"_id": 0, "user_id": 1, "statistic": 1}
        dt = [_ async for _ in ((await self.bot.db.cd("users")).find({}, f).sort([("statistic.pvp_win", -1)]))]
        position = int([int(_["user_id"]) for _ in dt].index(ctx.author.id)) + 1
        cd = await self.bot.db.cd("discriminators")
        dl = [_["_id"] async for _ in cd.find()]

        async def gn(bot, cl, user, dlist):
            _id, name = user["user_id"], ""

            if _id in dlist:
                user = bot.get_user(_id)
                if user is None:
                    data = await cl.find_one({"_id": _id})
                    name = data["discriminator"]
                else:
                    name = str(user)

            if len(name) == 0:
                name = str(await bot.fetch_user(_id))
                await cl.insert_one({"_id": _id, "discriminator": name})

            return name.replace("'", "").replace("#", "_")

        def money(amount):
            a = '{:,.0f}'.format(float(amount))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')
            return d

        def gd(ds):
            texto = f'WIN: {money(ds["statistic"].get("pvp_win", 0))} | ' \
                    f'LOSE: {money(ds["statistic"].get("pvp_lose", 0))} | ' \
                    f'TOTAL: {money(ds["statistic"].get("pvp_total", 0))}'
            return texto

        rank = "\n".join([f'{x + 1}º: {await gn(self.bot, cd, dt[x], dl)} > {gd(dt[x])}' for x in range(limit)])
        data_user = await self.db.get_data("user_id", ctx.author.id, "users")
        player = str(ctx.author).replace("'", "").replace("#", "_")
        rank += f"\n--------------------------------------------------------------------\n" \
                f"{position}º: {player} > WIN: {money(data_user['statistic'].get('pvp_win', 0))} | " \
                f"LOSE: {money(data_user['statistic'].get('pvp_lose', 0))} | " \
                f"TOTAL: {money(data_user['statistic'].get('pvp_total', 0))}"
        return rank

    async def get_item_amount(self, item):  # atualizado no banco de dados
        ff, fd, amount = {f'inventory.{item}': {"$exists": True}}, {"_id": 0, "inventory": 1}, 0
        dt = [d async for d in ((await self.bot.db.cd("users")).find(ff, fd).sort([(f'inventory.{item}', -1)]))]
        for data in dt:
            amount += data["inventory"][item]
        return amount
