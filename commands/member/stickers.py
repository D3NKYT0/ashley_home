import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.img_edit import stickers, remove_acentos_e_caracteres_especiais


class StickerClass(commands.Cog):
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
    @commands.group(name='sticker', aliases=["figurinha", "f"])
    async def sticker(self, ctx):
        """Comando usado pra retornar a lista de comandos pra staff
        Use ash staff"""
        if ctx.invoked_subcommand is None:
            self.status()
            embed = discord.Embed(color=self.color)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="Stickers Commands:",
                            value=f"{self.st[121]} `yugioh` seu album na tematica do anime yugioh.\n"
                                  f"{self.st[121]} `kozmo` seu album na tematica do anime yugioh.\n"
                                  f"{self.st[121]} `especial` seu album na tematica do anime yugioh.\n"
                                  f"{self.st[121]} `cdz` seu album na tematica do anime CDZ.\n")
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @sticker.command(name='yugioh', aliases=["ygo", "y"])
    async def _yugioh(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        if data is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        data_stickers = {
            "name": remove_acentos_e_caracteres_especiais(member.display_name),
            "type": "yugioh",
            "artifacts": data["stickers"]
        }

        await stickers(data_stickers)
        await ctx.send(file=discord.File('stickers.png'), content="> `CLIQUE NA IMAGEM PARA MAIORES DETALHES`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @sticker.command(name='kozmo', aliases=["k"])
    async def _kozmo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        if data is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        data_stickers = {
            "name": remove_acentos_e_caracteres_especiais(member.display_name),
            "type": "kozmo",
            "artifacts": data["stickers"]
        }

        await stickers(data_stickers)
        await ctx.send(file=discord.File('stickers.png'), content="> `CLIQUE NA IMAGEM PARA MAIORES DETALHES`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @sticker.command(name='especial', aliases=["e"])
    async def _especial(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        if data is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        data_stickers = {
            "name": remove_acentos_e_caracteres_especiais(member.display_name),
            "type": "especial",
            "artifacts": data["stickers"]
        }

        await stickers(data_stickers)
        await ctx.send(file=discord.File('stickers.png'), content="> `CLIQUE NA IMAGEM PARA MAIORES DETALHES`")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @sticker.command(name='cdz', aliases=["c"])
    async def _cdz(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.get_data("user_id", member.id, "users")
        if data is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        data_stickers = {
            "name": remove_acentos_e_caracteres_especiais(member.display_name),
            "type": "cdz",
            "artifacts": data["stickers"]
        }

        await stickers(data_stickers)
        await ctx.send(file=discord.File('stickers.png'), content="> `CLIQUE NA IMAGEM PARA MAIORES DETALHES`")


def setup(bot):
    bot.add_cog(StickerClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mSTICKER_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
