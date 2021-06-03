import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class QuestClass(commands.Cog):
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
    @commands.group(name='quest', aliases=['q'])
    async def quest(self, ctx):
        """Comando usado pra retornar a lista de subcomandos de quest
                Use ash quest"""
        if ctx.invoked_subcommand is None:
            self.status()
            embed = discord.Embed(color=self.color)
            embed.add_field(name="Quest Commands:",
                            value=f"{self.st[117]} `quest ht` [Hero is First Task]")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='hero_task', aliases=['ht'])
    async def _hero_task(self, ctx):
        """..."""
        await ctx.send(f"Comando em contrução...")


def setup(bot):
    bot.add_cog(QuestClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mQUESTCLASS\033[1;32m foi carregado com sucesso!\33[m')
