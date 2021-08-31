import discord

from random import choice
from discord.ext import commands
from resources.check import check_it
from resources.db import Database


git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class VipSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='vip')
    async def vip(self, ctx):
        """Comando usado pra retornar uma lista de todos os subcomandos de vip
        Use ash vip"""
        if ctx.invoked_subcommand is None:
            self.status()
            vip = discord.Embed(color=self.color)
            vip.add_field(name="Vip Commands:",
                          value=f"{self.st[66]} `vip member` Compre seu vip de membro.\n"
                                f"{self.st[66]} `vip guild` Compre seu vip de servidor.\n")
            vip.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            vip.set_thumbnail(url=self.bot.user.avatar_url)
            vip.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=vip)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=2592000))
    @vip.group(name='member', aliases=['membro', 'player', 'jogador'])
    async def _member(self, ctx):
        """Comando usado pra comprar vip da Ashley (usavel somente no server da Ashley)
        Use ash vip"""
        if ctx.guild.id != self.bot.config['config']['default_guild']:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass

            return await ctx.send('<:alert:739251822920728708>│`Você só pode pegar o vip dentro '
                                  'do meu servidor de suporte, para isso use o comando ASH INVITE para receber no '
                                  'seu privado o link do meu servidor.`')

        data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_ = data_
        if update_['config']['vip']:
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Você já tem vip ativo na sua conta!`')

        data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_ = data_
        if update_['true_money']['blessed'] < 20:
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Você precisa de pelo menos` **20 Blesseds Ethernyas**'
                                  ' `para comprar o seu vip mensal`')

        if "vip_coin" not in update_['inventory'].keys():
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Você precisa de pelo menos` **1 Vip Coin**'
                                  ' `para comprar o seu vip mensal`')

        update_['inventory']['vip_coin'] -= 1
        if update_['inventory']['vip_coin'] < 1:
            del update_['inventory']['vip_coin']
        update_['true_money']['blessed'] -= 20
        update_['config']['vip'] = True
        update_['rpg']['vip'] = True
        await self.bot.db.update_data(data_, update_, 'users')
        img = choice(git)
        embed = discord.Embed(color=self.bot.color)
        embed.set_image(url=img)
        await ctx.send(embed=embed)
        await ctx.send(f'<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `ACABOU DE COMPRAR '
                       f'1 MÊS DE VIP!`\n **Pelo custo de 20 Blesseds Ethernyas**')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=2592000))
    @vip.group(name='guild', aliases=['servidor', 'guilda', 'server'])
    async def _guild(self, ctx, guild: discord.Guild = None):
        """Comando usado pra comprar vip guild da ashley (usavel somente no server da Ashley)
        Use ash vip guild"""
        if guild is None:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass

            return await ctx.send('<:alert:739251822920728708>│`Você precisa colocar o ID da sua guilda!`\n'
                                  '**Obs:** `use o comando` **ash gi** `no servidor que voce quer ver o ID`')

        author = guild.get_member(ctx.author.id)
        if author is None:
            return await ctx.send(f'<:alert:739251822920728708>│`Você não está em:` **{str(guild).upper()}**')

        if not author.guild_permissions.manage_guild:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass

            return await ctx.send('<:alert:739251822920728708>│`Você não tem a permissão de:` **GERENCIAR SERVIDOR**')

        if ctx.guild.id != self.bot.config['config']['default_guild']:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del data_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass

            return await ctx.send('<:alert:739251822920728708>│`Você só pode pegar o vip dentro '
                                  'do meu servidor de suporte, para isso use o comando ASH INVITE para receber no '
                                  'seu privado o link do meu servidor.`')

        data_guild = await self.bot.db.get_data("guild_id", guild.id, "guilds")
        update_guild = data_guild
        if data_guild is None:
            return await ctx.send('<:alert:739251822920728708>│`Apenas guildas casdastradas podem comprar o vip!`')

        data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_ = data_

        if update_guild['vip']:
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Essa guilda já tem vip ativo na sua conta!`')

        data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_ = data_
        if update_['true_money']['blessed'] < 30:
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Você precisa de pelo menos` **30 Blesseds Ethernyas**'
                                  ' `para comprar o vip mensal da sua guilda`')

        if "vip_coin" not in update_['inventory'].keys():
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Você precisa de pelo menos` **2 Vip Coin**'
                                  ' `para comprar o seu vip mensal`')

        if update_['inventory']["vip_coin"] < 2:
            try:
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send('<:alert:739251822920728708>│`Você precisa de pelo menos` **2 Vip Coin**'
                                  ' `para comprar o seu vip mensal`')

        update_['inventory']['vip_coin'] -= 2
        if update_['inventory']['vip_coin'] < 1:
            del update_['inventory']['vip_coin']
        update_['true_money']['blessed'] -= 30
        update_guild['vip'] = True
        update_guild['available'] = 15000
        await self.bot.db.update_data(data_, update_, 'users')
        await self.bot.db.update_data(data_guild, update_guild, 'guilds')
        img = choice(git)
        embed = discord.Embed(color=self.bot.color)
        embed.set_image(url=img)
        await ctx.send(embed=embed)
        await ctx.send(f'<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `ACABOU DE COMPRAR'
                       f' 1 MÊS DE VIP GUILD!`\n **Pelo custo de 30 Blesseds Ethernyas**\n'
                       f'`ALEM DE LIBERAR 15.000 FRAGMENTOS DE BLESSEDS ETERNYAS PARA SEUS MEMBROS!`')


def setup(bot):
    bot.add_cog(VipSystem(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mVIP_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
