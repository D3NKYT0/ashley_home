import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database


class GenreClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='genre', aliases=['sex', 'sexo', 'genero'])
    async def genre(self, ctx):
        """Altere seu genero no sistema de RPG da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        update['rpg']['sex'] = "male" if update['rpg']['sex'] == "female" else "female"
        genre = "HOMEM" if update['rpg']['sex'] == "male" else "MULHER"
        await self.bot.db.update_data(data, update, "users")
        embed = disnake.Embed(
            color=self.bot.color,
            description=f"<:confirmed:721581574461587496>│`Seu genero foi trocado para:` **{genre}**")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GenreClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mGENRE\033[1;32m foi carregado com sucesso!\33[m')
