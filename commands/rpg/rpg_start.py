import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database
from asyncio import TimeoutError
from datetime import datetime


class RpgStart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.c = "`Comando Cancelado`"
        self.cls = ['paladin [hammer and shield]',
                    'necromancer [staffer and shield]',
                    'wizard [sword and shield]',
                    'warrior [dual sword / no shield]',
                    'priest [bow and arrow]',
                    'warlock [spear / no shield]',
                    'assassin [dagguer / no shield]']
        self.cl = ['paladin',
                   'necromancer',
                   'wizard',
                   'warrior',
                   'priest',
                   'warlock',
                   'assassin']

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='rpg', aliases=['start'])
    async def rpg(self, ctx):
        """Comando necessario para iniciar sua jornada no rpg da ashley"""

        def check_stone(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_sex(m):
            return m.author == ctx.author and m.content == '1' or m.author == ctx.author and m.content == '2'

        def check_option(m):
            return m.author == ctx.author and m.content.isdigit()

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        data_guild_native = await self.bot.db.get_data("guild_id", update['guild_id'], "guilds")
        update_guild_native = data_guild_native

        if data['rpg']['active']:
            embed = disnake.Embed(color=self.bot.color, description=f'<:alert:739251822920728708>│`VOCE JA INICIOU O '
                                                                    f'RPG, SE VOCE DESEJA ALTERAR A CLASSE:`')
            await ctx.send(embed=embed)

            for key in update['rpg']["equipped_items"].keys():
                if update['rpg']["equipped_items"][key] is not None:
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não pode trocar de classe '
                                          'com itens equipados, use o comando:` **ASH EQUIP RESET** `antes de mudar'
                                          ' de classe.`')

            msg = await ctx.send(f"<:alert:739251822920728708>│`VOCE DESEJA ALTERAR A CLASSE AGORA?`"
                                 f"\n**1** para `SIM` ou **0** para `NÃO`")
            try:
                answer = await self.bot.wait_for('message', check=check_stone, timeout=30.0)
            except TimeoutError:
                await msg.delete()
                return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
            if answer.content == "0":
                await msg.delete()
                return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
            await msg.delete()

        asks = {'sex': 'male', 'class_now': None}

        embed = disnake.Embed(color=self.bot.color,
                              description=f'<a:blue:525032762256785409>│`QUAL O SEXO DO SEU PERSONAGEM?`\n'
                                          f'`O sexo definirá a img que aparecera no comando (ash equip)`\n'
                                          f'**1** para `HOMEM` ou **2** para `MULHER`')
        msg = await ctx.send(embed=embed)

        try:
            answer = await self.bot.wait_for('message', check=check_sex, timeout=30.0)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│{self.c}')
            return await ctx.send(embed=embed)

        asks['sex'] = "male" if answer.content == "1" else "female"
        await msg.delete()

        embed = disnake.Embed(color=self.bot.color,
                              description=f'<a:blue:525032762256785409>│`QUAL CLASSE VOCE DESEJA APRENDER?`\n'
                                          f'`As classes fazem voce aprender habilidades unicas de cada uma`\n'
                                          f'`USE OS NUMEROS PARA DIZER QUAL CLASSE VOCE DESEJA:`\n'
                                          f'**1** para `{self.cls[0].upper()}`\n**2** para `{self.cls[1].upper()}`\n'
                                          f'**3** para `{self.cls[2].upper()}`\n**4** para `{self.cls[3].upper()}`\n'
                                          f'**5** para `{self.cls[4].upper()}`\n**6** para `{self.cls[5].upper()}`\n'
                                          f'**7** para `{self.cls[6].upper()}`')
        msg = await ctx.send(embed=embed)

        try:
            answer = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│{self.c}')
            return await ctx.send(embed=embed)

        if int(answer.content) in [1, 2, 3, 4, 5, 6, 7]:
            asks['class_now'] = self.cl[int(answer.content) - 1]
        else:
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`ESSA OPÇAO NAO ESTÁ DISPONIVEL, TENTE NOVAMENTE!`")
        await msg.delete()
        if not data['rpg']['active']:

            if asks['class_now'] in ["paladin", "warrior"]:
                set_ini = {"16": 1, "17": 1, "18": 1, "19": 1, "20": 1}

            elif asks['class_now'] in ["necromancer", "wizard", "warlock"]:
                set_ini = {"61": 1, "62": 1, "63": 1, "64": 1, "65": 1}

            else:
                set_ini = {"11": 1, "12": 1, "13": 1, "14": 1, "15": 1}

            update['rpg']["active"] = True
            update['rpg']["class_now"] = asks['class_now']
            update['rpg']["sex"] = asks['sex']
            update['rpg']["items"] = set_ini
            update['rpg']["activated_at"] = datetime.today()

            bonus = "\n`Olá aventureiro! Bem vindo ao RPG, sua jornada será longa e é perigoso ir sozinho, então " \
                    "estou lhe dando um presente, olhe seu inventário de equipamentos com o comando:` **ash es**\n" \
                    "`Qualquer duvida use os comandos:`\n**ash wiki <nome do que voce quer saber>** `e` **ash help**"

        else:

            update['rpg']["class_now"] = asks['class_now']
            update['rpg']["sex"] = asks['sex']
            bonus = ""

        await self.bot.db.update_data(data, update, 'users')
        await self.bot.db.update_data(data_guild_native, update_guild_native, 'guilds')
        msg = f'<:confirmed:721581574461587496>│`CONFIGURAÇÃO DO RPG FEITA COM SUCESSO!` {bonus}'
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='rpg_verify', aliases=['rpgv'])
    async def rpg_verify(self, ctx, member: disnake.Member = None):
        """Comando para verificar a data de entrada no RPG da ASHLEY"""
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        date_old = data['rpg']['activated_at']

        if date_old is None:
            msg = f'<:negate:721581573396496464>│{member} `USE O COMANDO` **ASH RPG** `ANTES!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        date_now = datetime.today()
        d1 = date_old.strftime("%d-%m-%Y")
        days = abs((date_old - date_now).days)
        hour = datetime.now().strftime("%H:%M:%S")
        msg = f"**Data de Entrada no RPG:** `{d1}`\n" \
              f"**Faz{'em' if days > 1 else ''}:** `{days} dia{'s' if days > 1 else ''}`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        embed.set_thumbnail(url=str(member.display_avatar))
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='user_verify', aliases=['userv'])
    async def user_verify(self, ctx, member: disnake.Member = None):
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
        embed = disnake.Embed(color=self.bot.color, description=msg)
        embed.set_thumbnail(url=str(member.display_avatar))
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='guild_verify', aliases=['guildv'])
    async def guild_verify(self, ctx, guild: disnake.Guild = None):
        """Comando para verificar a data de registro da guilda na ASHLEY"""

        if guild is None:
            guild = ctx.guild

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
        embed = disnake.Embed(color=self.bot.color, description=msg)
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RpgStart(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mRPG_START_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
