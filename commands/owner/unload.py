import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class UnloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='unload')
    async def unload(self, ctx, cog):
        """apenas desenvolvedores"""
        try:
            self.bot.unload_extension(cog)
            msg = f'<:confirmed:721581574461587496>│Extenção **{cog}**, parada com sucesso!'
            embed = discord.Embed(color=self.color, description=msg)
            await ctx.send(embed=embed)
        except discord.ext.commands.errors.ExtensionNotLoaded as e:
            msg = f'<:negate:721581573396496464>│Falha ao parar a extenção **{cog}**. \n```{e}```'
            embed = discord.Embed(color=discord.Color.red(), description=msg)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UnloadCog(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mUNLOAD\033[1;32m foi carregado com sucesso!\33[m')
