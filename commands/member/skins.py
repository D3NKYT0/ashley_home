import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class SkinsClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.skins = self.bot.config['attribute']['skins']

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='skin', aliases=['skins'])
    async def skin(self, ctx, skin=None):
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if skin is None:
            skins = "`Voce nao tem skins disponiveis`"
            if len(data["rpg"]["skins"]) != 0:
                skins = "\n".join(data["rpg"]["skins"])
            msg = f"<:confirmed:721581574461587496>│`Segue abaixo suas skins disponiveis:`\n{skins}"
            embed = discord.Embed(olor=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if skin not in self.skins:
            msg = f"<:negate:721581573396496464>│`Essa skin nao existe`"
            embed = discord.Embed(olor=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if skin not in data["rpg"]["skins"]:
            msg = f"<:alert:739251822920728708>│`Essa skin nao esta disponivel pra voce`"
            embed = discord.Embed(olor=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        update = data
        update['rpg']['skin'] = skin
        await self.bot.db.update_data(data, update, "users")
        msg = f"<:confirmed:721581574461587496>│`Sua skin foi mudada para:` **{skin.upper()}**"
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SkinsClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mSKINS\033[1;32m foi carregado com sucesso!\33[m')
