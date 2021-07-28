import discord

from resources.check import check_it
from discord.ext import commands
from resources.db import Database


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='vote', aliases=['v', 'voto'])
    async def vote(self, ctx):
        """Comando usado pra votar na ashley
        Use ash vote"""
        link_gg = "https://top.gg/bot/478977311266570242/vote"
        link_best = "https://bestlist.online/bots/478977311266570242"
        description = f"`Top.gg`\n**[Clique Aqui]({link_gg})**\n\n`Bestlist`\n**[Clique Aqui]({link_best})**"
        embed = discord.Embed(description=description, color=self.color)
        embed.set_footer(text=f"Pedido por {ctx.author}")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Vote(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mVOTE\033[1;32m foi carregado com sucesso!\33[m')
