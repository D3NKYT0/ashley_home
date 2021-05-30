import discord
import time as date

from discord.ext import commands
from resources.db import Database
from resources.check import check_it
from datetime import datetime as dt

epoch = dt.utcfromtimestamp(0)


class LoverClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='lower_net', aliases=['ln'])
    async def lower_net(self, ctx):
        """Comando para ativar/desativar imagens e gifs do battle."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if ctx.author.id in self.bot.jogando:
            return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                  " vocÊ estiver livre!`")

        if not data['rpg']['active']:
            embed = discord.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        update['rpg']['lower_net'] = not update['rpg']['lower_net']
        await self.bot.db.update_data(data, update, "users")
        msg = "ATIVADO" if not update['rpg']['lower_net'] else "DESATIVADO"
        emo = "<:confirmed:721581574461587496>" if not update['rpg']['lower_net'] else "<:negate:721581573396496464>"
        await ctx.send(f"{emo}│`O MODO DE IMAGEM FOI {msg}!`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=3600))
    @commands.command(name='lover', aliases=['al'])
    async def lover(self, ctx):
        """Esse comando te transforma em um lover da ahsley, sendo pingado para novidades."""
        try:
            role = discord.utils.find(lambda r: r.name == "</Ash_Lovers>", ctx.guild.roles)
            if role is not None:
                if role not in [r for r in ctx.author.roles]:
                    await ctx.author.add_roles(role)
                    await ctx.send("<:confirmed:721581574461587496>│`VOCE AGORA É UM LOVER MEU!!`")
                else:
                    data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                    update_ = data_
                    del data_['cooldown'][str(ctx.command)]
                    await self.bot.db.update_data(data_, update_, 'users')
                    await ctx.send("🌺`VOCE JA É UM LOVER MEU! MAS OBG POR TANTO AMOR`🌸")
            else:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
                await ctx.send(f"<:alert:739251822920728708>│`PEÇA PRA UM ADMINISTRADOR CRIAR UM CARGO CHAMADO:` "
                               f"**</Ash_Lovers>** `PARA ESSE SERVIDOR DESFRUTAR DOS MEUS SERVIÇOS DE PING.`")
        except discord.Forbidden:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del data_['cooldown'][str(ctx.command)]
            await self.bot.db.update_data(data_, update_, 'users')
            await ctx.send("<:negate:721581573396496464>│`NAO TENHO PERMISSÃO DE ADICIONAR CARGOS!`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=3600))
    @commands.command(name='unlover', aliases=['ual'])
    async def unlover(self, ctx):
        """Esse comando retira seu lover, assim voce nao é mais notificado"""
        try:
            role = discord.utils.find(lambda r: r.name == "</Ash_Lovers>", ctx.guild.roles)
            if role is not None:
                if role in [r for r in ctx.author.roles]:
                    await ctx.author.remove_roles(role)
                    await ctx.send("<:confirmed:721581574461587496>│`QUE PENA, VOCE NAO ME AMA MAIS?!`")
                else:
                    data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                    update_ = data_
                    del data_['cooldown'][str(ctx.command)]
                    await self.bot.db.update_data(data_, update_, 'users')
                    await ctx.send("<:cry:530735037243719687>│`VOCE NAO TEM MAIS O MEU CARGO, POXA..."
                                   " ME ODEIA TANTO ASSIM?`")
            else:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
                await ctx.send(f"<:alert:739251822920728708>│`PEÇA PRA UM ADMINISTRADOR CRIAR UM CARGO CHAMADO:`"
                               f" **</Ash_Lovers>** `PARA ESSE SERVIDOR DESFRUTAR DOS MEUS SERVIÇOS DE PING.`")
        except discord.Forbidden:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del data_['cooldown'][str(ctx.command)]
            await self.bot.db.update_data(data_, update_, 'users')
            await ctx.send("<:negate:721581573396496464>│`NAO TENHO PERMISSÃO DE RETIRAR CARGOS!`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 30.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='status', aliases=['estado'])
    async def status(self, ctx):
        """Esse comando mostra seus status atuais, numa visao geral do bot."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        g_data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        user = self.bot.user_commands[ctx.author.id]
        guild = self.bot.guilds_commands[ctx.guild.id]

        try:
            time_diff = (dt.utcnow() - epoch).total_seconds() - data["cooldown"]["daily coin"]
            coin = True if time_diff > 86400 else False
        except KeyError:
            coin = True

        try:
            time_diff = (dt.utcnow() - epoch).total_seconds() - data["cooldown"]["daily work"]
            work = True if time_diff > 86400 and guild > 50 and user > 20 else False
        except KeyError:
            work = True if guild > 50 and user > 20 else False

        try:
            time_diff = (dt.utcnow() - epoch).total_seconds() - data["cooldown"]["rec"]['date']
            rec = True if time_diff > 86400 or time_diff < 86400 and data['cooldown']['rec']['cont'] < 10 else False
        except KeyError:
            rec = True

        try:
            time_diff = (dt.utcnow() - epoch).total_seconds() - data["cooldown"]["daily energy"]
            energy = True if time_diff > 86400 else False
        except KeyError:
            energy = True

        try:
            time_diff = (dt.utcnow() - epoch).total_seconds() - data["cooldown"]["guild reward"]
            reward = True if time_diff > 3600 else False
        except KeyError:
            reward = True

        if not g_data['vip']:
            reward = False

        date_now = dt.today()

        m_last_command = 0
        if data['security']['last_command'] is not None:
            last_command = data['security']['last_command']
            last_verify = date.mktime(date_now.timetuple())
            last_command = date.mktime(last_command.timetuple())
            m_last_command = int(int(last_verify - last_command) / 60)

        m_last_verify = 0
        if data['security']['last_verify'] is not None:
            last_command = data['security']['last_verify']
            last_verify = date.mktime(date_now.timetuple())
            last_command = date.mktime(last_command.timetuple())
            m_last_verify = int(int(last_verify - last_command) / 60)

        m_last_blocked = 0
        if data['security']['last_blocked'] is not None:
            last_command = data['security']['last_blocked']
            last_verify = date.mktime(date_now.timetuple())
            last_command = date.mktime(last_command.timetuple())
            m_last_blocked = int(int(last_verify - last_command) / 60)

        if m_last_blocked < 1000:
            mlb = f"Ha {m_last_blocked} minutos"
        else:
            if m_last_blocked / 60 < 1000:
                mlb = f"Ha {int(m_last_blocked / 60)} horas"
            else:
                mlb = f"Ha {int(m_last_blocked / 60 / 24)} dias"

        commands_today = data['security']['commands_today']
        last_command = f"Ha {m_last_command} minutos" if data['security']['last_command'] is not None else "Pendente..."
        last_channel = self.bot.get_channel(data['security']['last_channel'])
        last_verify = f"Ha {m_last_verify} minutos" if data['security']['last_verify'] is not None else "Pendente..."
        last_blocked = "Ficha Limpa" if data['security']['last_blocked'] is None else mlb
        wa = data['security']['warns']
        strikes = data['security']['strikes']
        strikes_to_ban = data['security']['strikes_to_ban']
        status = "Liberado" if data['security']['status'] else "Bloqueado"
        blocked = "Liberado" if not data['security']['blocked'] else "Bloqueado"

        msg, n = "", 1
        for k in wa.keys():
            msg += f"**{n}º** {'`Avisado`' if wa[k] else '`Livre`'} **|** "
            n += 1

        s1 = "Comandos que voce usou desde que o bot iniciou."
        s2 = "Comandos que voce usou hoje."
        s3 = "Comandos que essa guilda usou desde que o bot iniciou."

        a1 = ctx.author.id in self.bot.casando
        a2 = ctx.author.id in self.bot.jogando
        a3 = ctx.author.id in self.bot.batalhando
        a4 = ctx.author.id in self.bot.comprando
        a5 = ctx.author.id in self.bot.minerando
        a6 = data['config']['provinces']

        embed = discord.Embed(color=self.bot.color)

        embed.add_field(name="-== STATUS DO USUARIO ==-", inline=False,
                        value=f"{'🟢' if a1 else '🔴'} `Casando` Se for verde esta ativado.\n"
                              f"{'🟢' if a2 else '🔴'} `Jogando` Se for verde esta ativado.\n"
                              f"{'🟢' if a3 else '🔴'} `Batalhando` Se for verde esta ativado.\n"
                              f"{'🟢' if a4 else '🔴'} `Comprando` Se for verde esta ativado.\n"
                              f"{'🟢' if a5 else '🔴'} `Minerando` Se for verde esta ativado.\n"
                              f"{'🟢' if a6 is not None else '🔴'} `Provincia` Se for verde esta ativado.")

        embed.add_field(name="-== COMANDOS DIARIOS ==-", inline=False,
                        value=f"{'🟢' if coin else '🔴'} `Coin` Se tiver verde está disponivel pra usar.\n"
                              f"{'🟢' if work else '🔴'} `Work` Se tiver verde está disponivel pra usar.\n"
                              f"{'🟢' if rec else '🔴'} `Rec` Se tiver verde está disponivel pra usar.\n"
                              f"{'🟢' if energy else '🔴'} `Energy` Se tiver verde está disponivel pra usar.\n"
                              f"{'🟢' if reward else '🔴'} `Reward` Se tiver verde está disponivel pra usar.")

        embed.add_field(name="--== COMANDOS USADOS ==--", inline=False,
                        value=f"`{commands_today}/5000{(' ' * (10 - len(f'{commands_today}/5000')))}` {s2}\n"
                              f"`{user}{(' ' * (5 - len(str(user))))}` {s1}\n"
                              f"`{guild}{(' ' * (5 - len(str(guild))))}` {s3}")

        embed.add_field(name="--== SISTEMA DE SEGURANÇA ==--", inline=False,
                        value=f"`{'ultimo comando'.upper()}:` **{last_command}**\n"
                              f"`{'ultimo canal'.upper()}:` **{last_channel}**\n"
                              f"`{'ultima verificação'.upper()}:` **{last_verify}**\n"
                              f"`{'ultimo bloqueio'.upper()}:` **{last_blocked}**\n"
                              f"`{'avisos'.upper()}:` {msg}\n"
                              f"`{'strikes para bloqueio diario'.upper()}:` **{strikes} / 10**\n"
                              f"`{'strikes para banimento'.upper()}:` **{strikes_to_ban} / 10**\n"
                              f"`{'bloqueado hoje'.upper()}:` **{status}**\n"
                              f"`{'bloqueado por 72h'.upper()}:` **{blocked}**\n")

        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LoverClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mLOVER_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
