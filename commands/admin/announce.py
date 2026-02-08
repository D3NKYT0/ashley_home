import datetime
import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from asyncio import TimeoutError


class RegisterAnnounce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.em = self.bot.em

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, cooldown=True, time=300))
    @commands.command(name='announce', aliases=['anuncio'])
    async def announce(self, ctx, *, announce: str = None):
        """Usado pra anunciar na ashley
        Exemplo: ash announce <texto do anuncio aqui>
        seu texto será analizado por um dos desenvolvedores por questoes de segurança"""
        if ctx.author.id != ctx.guild.owner.id:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del update_['cooldown'][str(ctx.command)]
            await self.bot.db.update_data(data_, update_, 'users')
            return await ctx.send(f"{self.em['negate']}│`Apenas donos de Guilda vip podem usar esse "
                                  f"comando!`")

        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        if data_guild['vip'] is False:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del update_['cooldown'][str(ctx.command)]
            await self.bot.db.update_data(data_, update_, 'users')
            return await ctx.send(f"{self.em['negate']}│`Você é o líder da guilda, mas sua Guilda ainda "
                                  f"nao é VIP, você precisa conquistar 10 estrelas para tornar sua guilda VIP!`")

        if announce is None:
            try:
                data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                update_ = data_
                del update_['cooldown'][str(ctx.command)]
                await self.bot.db.update_data(data_, update_, 'users')
            except KeyError:
                pass
            return await ctx.send(f"{self.em['negate']}│`Você precisa colocar um anuncio, para que eu"
                                  f" adicione no banco de dados!`")

        for data in await self.bot.db.get_announcements():
            if data['_id'] == ctx.author.id:
                await ctx.send(f"{self.em['alert']}│`Você já tem um anuncio em vigor, se colocar"
                               f" outro anuncio vai sobrepor seu anuncio antigo. Deseja mesmo assim proseguir?` "
                               f"**Responda com: S ou N**")

                def check(m):
                    return m.author.id == ctx.author.id and m.content.upper() == 'S' or m.author.id == ctx.author.id \
                           and m.content.upper() == 'N'

                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=30.0)
                except TimeoutError:
                    data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
                    update_ = data_
                    del update_['cooldown'][str(ctx.command)]
                    await self.bot.db.update_data(data_, update_, 'users')
                    return await ctx.send(f'{self.em["negate"]}│`Desculpe, você demorou muito:` '
                                          f'**COMANDO CANCELADO**')
                if answer.content.upper() == "N":
                    return await ctx.send(f'{self.em["negate"]}│ **COMANDO CANCELADO**')
                else:
                    update = data
                    update['data']['status'] = False
                    date = datetime.datetime(*datetime.datetime.utcnow().timetuple()[:6])
                    update['data']['date'] = date
                    update['data']['announce'] = announce
                    await self.bot.db.update_data(data, update, "announcements")
                    await ctx.send(f'{self.em["confirm"]}│`Anuncio cadastrado com sucesso!`\n'
                                   f'```AGUARDE APROVAÇÃO```')
                    pending = self.bot.get_channel(619969149791240211)
                    msg = f"{ctx.author.id}: **{ctx.author.name}** `ADICIONOU UM NOVO ANUNCIO PARA APROVAÇÃO!`"
                    return await pending.send(msg)
        await self.bot.data.add_announcement(ctx, announce)

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='verify', aliases=['verificar'])
    async def verify(self, ctx):
        """apenas desenvolvedores
        mostra a lista de anuncios pendentes"""
        announces = list()
        for data in await self.bot.db.get_announcements():
            if data['data']['status'] is False:
                announces.append(data)
        for announce in range(len(announces)):
            await ctx.send(f"{announce + 1}º Anuncio:\n{announces[announce]}")
        if len(announces) > 0:
            await ctx.send(f"{self.em['alert']}│`Qual anuncio você deseja verificar? Obs: Digite o "
                           f"numero do anuncio`")
        else:
            return await ctx.send(f"{self.em['alert']}│`VOCE NAO TEM ANUNCIOS DISPONIVEIS!`")

        def check(m):
            return m.author.id == ctx.author.id and m.content.isdigit()

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)
            num = int(answer.content)
            answer = int(answer.content)
            if answer < 0:
                answer = 0
        except TimeoutError:
            return await ctx.send(f'{self.em["negate"]}│`Desculpe, você demorou muito:` '
                                  f'**COMANDO CANCELADO**')
        if len(announces) >= answer > 0:
            pass
        else:
            return await ctx.send(f'{self.em["negate"]}│ **DESCULPE VOCÊ DIGITOU UM NUMERO INEXISTENTE!**')

        await ctx.send(announces[num - 1])
        await ctx.send(f"{self.em['alert']}│`Esse anuncio é valido?  Obs: Digite"
                       f" S ou N`")

        def check(m):
            return m.author.id == ctx.author.id and m.content.upper() == 'S' or m.author.id == ctx.author.id \
                   and m.content.upper() == 'N'

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            return await ctx.send(f'{self.em["negate"]}│`Desculpe, você demorou muito:` '
                                  f'**COMANDO CANCELADO**')
        if answer.content.upper() == "S":
            pass
        else:
            data = announces[num - 1]
            await self.bot.db.delete_data(data, 'announcements')
            await ctx.send(f"{self.em['confirm']}│`Anuncio verificado com sucesso!`")
            try:
                member = self.bot.get_user(data['_id'])
                await member.send(f"{self.em['negate']}│`Seu anuncio foi verificado, mas não foi aprovado!`")
            except discord.Forbidden:
                pass
            return await ctx.send(f'{self.em["alert"]}│ **ANUNCIO DELETADO**')

        data = announces[num - 1]
        update = data
        update['data']['status'] = True
        await self.bot.db.update_data(data, update, "announcements")
        await ctx.send(f"{self.em['confirm']}│`Anuncio verificado com sucesso!`")
        try:
            member = self.bot.get_user(data['_id'])
            await member.send(f"{self.em['confirm']}│`Seu anuncio foi verificado e foi aprovado"
                              f" parabens!`")
        except discord.Forbidden:
            pass


async def setup(bot):
    await bot.add_cog(RegisterAnnounce(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mREGISTER_ANNOUNCE\033[1;32m foi carregado com sucesso!\33[m')
