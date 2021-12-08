from disnake.ext import commands
from resources.check import check_it
from resources.db import Database


class ChannelClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.em = self.bot.em

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='channel', aliases=['locker', 'ch', 'lk'])
    async def channel(self, ctx):
        """Esse comando bloqueia a ashley de usar comandos em determinados canais, usando o sistema de
        lista branca e lista negra.
        ash channel (troca de listra negra e branca)"""
        if ctx.invoked_subcommand is None:
            data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
            update_guild = data_guild
            update_guild['command_locked']['status'] = not update_guild['command_locked']['status']
            await self.bot.db.update_data(data_guild, update_guild, 'guilds')

            if update_guild['command_locked']['status']:
                await ctx.send(f"{self.em['confirm']}│`BLOQUEADOR DE COMANDOS ESTA NO MODO:` **WHITELIST**\n"
                               f"```\nNeste modo todos os canais são bloqueados, exceto os que estão na: WHITELIST```"
                               f"\n**Obs:** `adicione ou retire um canal da WHITELIST com os comandos:` "
                               f"**ASH CHANNEL ADD/REMOVE**")
            else:
                await ctx.send(f"{self.em['negate']}│`BLOQUEADOR DE COMANDOS ESTA NO MODO:` **BLACKLIST**\n"
                               f"```\nNeste modo todos os canais são liberados, exceto os que estão na: BLACKLIST```"
                               f"\n**Obs:** `adicione ou retire um canal da BLACKLIST com os comandos:` "
                               f"**ASH CHANNEL ADD/REMOVE**")

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @channel.command(name='add', aliases=['on'])
    async def _add(self, ctx):
        """Esse comando bloqueia a ashley de usar comandos em determinados canais, usando o sistema de
        lista branca e lista negra.
        ash channel add (adiciona um canal a lista vigente)"""
        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update_guild = data_guild

        if update_guild['command_locked']['status']:
            if ctx.channel.id not in update_guild['command_locked']['while_list']:
                update_guild['command_locked']['while_list'].append(ctx.channel.id)
                await self.bot.db.update_data(data_guild, update_guild, 'guilds')
                await ctx.send(f"{self.em['confirm']}│`O CANAL` **{ctx.channel.name}** `FOI DESBLOQUEADO COM "
                               f"SUCESSO!`")
            else:
                await ctx.send(f"{self.em['alert']}│`ESSE CANAL JA ESTA DESBLOQUEADO!`")

        else:
            if ctx.channel.id not in update_guild['command_locked']['black_list']:
                update_guild['command_locked']['black_list'].append(ctx.channel.id)
                await self.bot.db.update_data(data_guild, update_guild, 'guilds')
                await ctx.send(f"{self.em['confirm']}│`O CANAL` **{ctx.channel.name}** `FOI BLOQUEADO COM "
                               f"SUCESSO!`")
            else:
                await ctx.send(f"{self.em['alert']}│`ESSE CANAL JA ESTA BLOQUEADO!`")

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @channel.command(name='remove', aliases=['off'])
    async def _remove(self, ctx):
        """Esse comando bloqueia a ashley de usar comandos em determinados canais, usando o sistema de
        lista branca e lista negra.
        ash channel remove (remove um canal a lista vigente)"""
        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update_guild = data_guild

        if update_guild['command_locked']['status']:
            if ctx.channel.id in update_guild['command_locked']['while_list']:
                update_guild['command_locked']['while_list'].remove(ctx.channel.id)
                await self.bot.db.update_data(data_guild, update_guild, 'guilds')
                await ctx.send(f"{self.em['confirm']}│`O CANAL` **{ctx.channel.name}** `FOI BLOQUEADO COM "
                               f"SUCESSO!`")
            else:
                await ctx.send(f"{self.em['alert']}│`ESSE CANAL JA ESTA BLOQUEADO!`")

        else:
            if ctx.channel.id in update_guild['command_locked']['black_list']:
                update_guild['command_locked']['black_list'].remove(ctx.channel.id)
                await self.bot.db.update_data(data_guild, update_guild, 'guilds')
                await ctx.send(f"{self.em['confirm']}│`O CANAL` **{ctx.channel.name}** `FOI DESBLOQUEADO COM "
                               f"SUCESSO!`")
            else:
                await ctx.send(f"{self.em['alert']}│`ESSE CANAL JA ESTA DESBLOQUEADO!`")

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @channel.command(name='reset', aliases=['r'])
    async def _reset(self, ctx):
        """Esse comando bloqueia a ashley de usar comandos em determinados canais, usando o sistema de
        lista branca e lista negra.
        ash channel reset (reseta todos os canais da lista vigente)"""
        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update_guild = data_guild

        if update_guild['command_locked']['status']:
            update_guild['command_locked']['while_list'] = list()
            await self.bot.db.update_data(data_guild, update_guild, 'guilds')
            await ctx.send(f"{self.em['confirm']}│`A LISTA DO MODO:` **WHITELIST** `FOI LIMPA COM SUCESSO!`")

        else:
            update_guild['command_locked']['black_list'] = list()
            await self.bot.db.update_data(data_guild, update_guild, 'guilds')
            await ctx.send(f"{self.em['confirm']}│`A LISTA DO MODO:` **BLACKLIST** `FOI LIMPA COM SUCESSO!`")

    @channel.error
    async def _check_channel_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f'{self.em["negate"]}│`Você não tem permissão para usar esse comando!`')

    @_add.error
    async def _check_add_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f'{self.em["negate"]}│`Você não tem permissão para usar esse comando!`')

    @_remove.error
    async def _check_remove_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f'{self.em["negate"]}│`Você não tem permissão para usar esse comando!`')

    @_reset.error
    async def _check_reset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f'{self.em["negate"]}│`Você não tem permissão para usar esse comando!`')


def setup(bot):
    bot.add_cog(ChannelClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mCHANNEL_LOCKER\033[1;32m foi carregado com sucesso!\33[m')
