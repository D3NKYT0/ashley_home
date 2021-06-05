import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from asyncio import TimeoutError
from datetime import datetime


class RpgStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.c = "`Comando Cancelado`"
        self.cl = ['paladin', 'necromancer', 'wizard', 'warrior', 'priest', 'warlock', 'assassin']

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='rpg', aliases=['start'])
    async def rpg(self, ctx):
        """Comando necessario para iniciar sua jornada no rpg da ashley"""
        def check_battle(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_option(m):
            return m.author == ctx.author and m.content.isdigit()

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        data_guild_native = await self.bot.db.get_data("guild_id", update['guild_id'], "guilds")
        update_guild_native = data_guild_native

        if data['rpg']['active']:
            embed = discord.Embed(color=self.bot.color, description=f'<:alert:739251822920728708>│`VOCE JA INICIOU O '
                                                                    f'RPG, SE VOCE DESEJA ALTERAR ALGO COMO: MODO DE '
                                                                    f'IMAGEM E CLASSE, VAI GASTAR AS PEDRAS ABAIXO:`')
            await ctx.send(embed=embed)
            n_cost = [15000, 5000, 500]
            t = data['treasure']
            await ctx.send(f"{self.bot.money[0]} `Custa:` **{n_cost[0]}**| "
                           f"{self.bot.money[1]} `Custa:` **{n_cost[1]}**| "
                           f"{self.bot.money[2]} `Custa:` **{n_cost[2]}**.")

            if t["bronze"] < n_cost[0] or t["silver"] < n_cost[1] or t["gold"] < n_cost[2]:
                return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não tem pedras suficientes.` '
                                      '**COMANDO CANCELADO**')

            for key in update['rpg']["equipped_items"].keys():
                if update['rpg']["equipped_items"][key] is not None:
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não pode trocar de classe '
                                          'com itens equipados, use o comando:` **ASH EQUIP RESET** `antes de mudar'
                                          ' de classe.`')

            msg = await ctx.send(f"<:alert:739251822920728708>│`VOCE JA TEM TODAS AS PEDRAS NECESSARIOS, "
                                 f"DESEJA ALTERAR A CLASSE OU MODO DE IMAGEM AGORA?`"
                                 f"\n**1** para `SIM` ou **0** para `NÃO`")
            try:
                answer = await self.bot.wait_for('message', check=check_battle, timeout=30.0)
            except TimeoutError:
                await msg.delete()
                return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
            if answer.content == "0":
                await msg.delete()
                return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
            await msg.delete()

            # DATA DO MEMBRO
            update['treasure']["bronze"] -= n_cost[0]
            update['treasure']["silver"] -= n_cost[1]
            update['treasure']["gold"] -= n_cost[2]
            # DATA NATIVA DO SERVIDOR
            update_guild_native['data'][f"total_bronze"] -= n_cost[0]
            update_guild_native['data'][f"total_silver"] -= n_cost[1]
            update_guild_native['data'][f"total_gold"] -= n_cost[2]

        asks = {'lower_net': False, 'class_now': None}

        embed = discord.Embed(color=self.bot.color,
                              description=f'<a:blue:525032762256785409>│`DESEJA ATIVAR O MODO DE BATALHA SEM '
                                          f'IMAGEM?`\n`O modo de batalha sem imagem faz com que seja carregado '
                                          f'mais rapido as mensagens`\n**1** para `SIM` ou **0** para `NÃO`')
        msg = await ctx.send(embed=embed)

        try:
            answer = await self.bot.wait_for('message', check=check_battle, timeout=30.0)
        except TimeoutError:
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│{self.c}')
            return await ctx.send(embed=embed)

        asks['lower_net'] = True if answer.content == "1" else False
        await msg.delete()

        embed = discord.Embed(color=self.bot.color,
                              description=f'<a:blue:525032762256785409>│`QUAL CLASSE VOCE DESEJA APRENDER?`\n'
                                          f'`As classes fazem voce aprender habilidades unicas de cada uma`\n'
                                          f'`USE OS NUMEROS PARA DIZER QUAL CLASSE VOCE DESEJA:`\n'
                                          f'**1** para `{self.cl[0].upper()}`\n**2** para `{self.cl[1].upper()}`\n'
                                          f'**3** para `{self.cl[2].upper()}`\n**4** para `{self.cl[3].upper()}`\n'
                                          f'**5** para `{self.cl[4].upper()}`\n**6** para `{self.cl[5].upper()}`\n'
                                          f'**7** para `{self.cl[6].upper()}`')
        msg = await ctx.send(embed=embed)

        try:
            answer = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│{self.c}')
            return await ctx.send(embed=embed)

        if int(answer.content) in [1, 2, 3, 4, 5, 6, 7]:
            asks['class_now'] = self.cl[int(answer.content) - 1]
        else:
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`ESSA OPÇAO NAO ESTÁ DISPONIVEL, TENTE NOVAMENTE!`")
        await msg.delete()
        if not data['rpg']['active']:
            rpg = {
                "class": 'default',
                "active": True,
                "lower_net": asks['lower_net'],
                "class_now": asks['class_now'],
                "vip": update['rpg']['vip'],
                "sub_class": {
                    "paladin": {"level": 1, "xp": 0, "level_max": False},
                    "warrior": {"level": 1, "xp": 0, "level_max": False},
                    "necromancer": {"level": 1, "xp": 0, "level_max": False},
                    "wizard": {"level": 1, "xp": 0, "level_max": False},
                    "warlock": {"level": 1, "xp": 0, "level_max": False},
                    "assassin": {"level": 1, "xp": 0, "level_max": False},
                    "priest": {"level": 1, "xp": 0, "level_max": False}
                },
                "status": {"con": 5, "prec": 5, "agi": 5, "atk": 5, "luk": 0, "pdh": 1},
                'items': dict(),
                'skills': [0, 0, 0, 0, 0],
                "armors": {
                    "shoulder": [0, 0, 0, 0, 0],
                    "breastplate": [0, 0, 0, 0, 0],
                    "gloves": [0, 0, 0, 0, 0],
                    "leggings": [0, 0, 0, 0, 0],
                    "boots": [0, 0, 0, 0, 0],
                    "shield": [0, 0, 0, 0, 0],
                    "necklace": [0, 0, 0, 0, 0],
                    "earring": [0, 0, 0, 0, 0],
                    "ring": [0, 0, 0, 0, 0]
                },
                'equipped_items': {
                    "shoulder": None,
                    "breastplate": None,
                    "gloves": None,
                    "leggings": None,
                    "boots": None,
                    "consumable": None,
                    "sword": None,
                    "shield": None,
                    "necklace": None,
                    "earring": None,
                    "ring": None
                },
                "activated_at": datetime.today(),
                "quests": dict()
            }
        else:
            pdh = update['rpg']['sub_class'][asks['class_now']]["level"]
            rpg = {
                "active": True,
                "class": 'default',
                "lower_net": asks['lower_net'],
                "class_now": asks['class_now'],
                "vip": update['rpg']['vip'],
                "sub_class": update['rpg']['sub_class'],
                "status": {"con": 5, "prec": 5, "agi": 5, "atk": 5, "luk": 0, "pdh": pdh},
                'items': update['rpg']['items'],
                'skills': update['rpg']['skills'],
                "armors": update['rpg']['armors'],
                'equipped_items': update['rpg']['equipped_items'],
                "activated_at": update['rpg']['activated_at'],
                "quests": update['rpg']['quests']
            }

        update['rpg'] = rpg
        await self.bot.db.update_data(data, update, 'users')
        await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')
        msg = f'<:confirmed:721581574461587496>│`CONFIGURAÇÃO DO RPG FEITA COM SUCESSO!`'
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='rpg_verify', aliases=['rpgv'])
    async def rpg_verify(self, ctx, member: discord.Member = None):
        """Comando para verificar a data de entrada no RPG da ASHLEY"""
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        date_old = data['rpg']['activated_at']
        date_now = datetime.today()
        d1 = date_old.strftime("%d-%m-%Y")
        days = abs((date_old - date_now).days)
        hour = datetime.now().strftime("%H:%M:%S")
        msg = f"**Data de Entrada no RPG:** `{d1}`\n" \
              f"**Faz{'em' if days > 1 else ''}:** `{days} dia{'s' if days > 1 else ''}`"
        embed = discord.Embed(color=self.bot.color, description=msg)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='user_verify', aliases=['userv'])
    async def user_verify(self, ctx, member: discord.Member = None):
        """Comando para verificar a data de registro na ASHLEY"""
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        date_old = data["config"]["create_at"]

        if date_old is None:
            cl = await self.bot.db.cd("users")
            query = {"$set": {f"config.create_at": datetime.today()}}
            await cl.update_one({"user_id": member.id}, query)
            date_old = datetime.today()

        date_now = datetime.today()
        d1 = date_old.strftime("%d-%m-%Y")
        days = abs((date_old - date_now).days)
        hour = datetime.now().strftime("%H:%M:%S")
        msg = f"**Data de registro na ASHLEY:** `{d1}`\n" \
              f"**Faz{'em' if days > 1 else ''}:** `{days} dia{'s' if days > 1 else ''}`"
        embed = discord.Embed(color=self.bot.color, description=msg)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='guild_verify', aliases=['guildv'])
    async def guild_verify(self, ctx, guild: discord.Guild = None):
        """Comando para verificar a data de registro na ASHLEY"""

        data = await self.bot.db.get_data("guild_id", guild.id, "guilds")
        if data is None:
            return ctx.send("<:alert:739251822920728708>│`Guilda nao cadastrada!`")

        date_old = data["data"]["create_at"]
        if date_old is None:
            cl = await self.bot.db.cd("guilds")
            query = {"$set": {f"data.create_at": datetime.today()}}
            await cl.update_one({"guild_id": guild.id}, query)
            date_old = datetime.today()

        date_now = datetime.today()
        d1 = date_old.strftime("%d-%m-%Y")
        days = abs((date_old - date_now).days)
        hour = datetime.now().strftime("%H:%M:%S")
        msg = f"**Data de registro na ASHLEY:** `{d1}`\n" \
              f"**Faz{'em' if days > 1 else ''}:** `{days} dia{'s' if days > 1 else ''}`"
        embed = discord.Embed(color=self.bot.color, description=msg)
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RpgStart(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mRPG_START_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
