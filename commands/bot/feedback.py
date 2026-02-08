import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.color import random_color


class FeedBackClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 60.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='feedback', aliases=['sugestao', 'report', 'suggestion'])
    async def feedback(self, ctx, *, msg: str = None):
        """Comando usado pra dar feedback direto pros desenvolvedores
        Use ash feedback <mensagem desejada>"""
        if msg is None:
            return await ctx.send('<:negate:721581573396496464>│`SEU FEEDBACK NÃO PODE SER VAZIO!`')
        try:
            member = ctx.author
            server = ctx.guild
            channel = self.bot.get_channel(530418605284917252)
            embed = discord.Embed(title='Feedback', color=random_color())
            embed.add_field(name='Info',
                            value=f'● Server: {server.name}\n● ServerID: {server.id}\n● Usuario: {member.name}\n● '
                            f'UsuarioID: {member.id}')
            embed.add_field(name='Feedback', value=f'{msg}', inline=False)
            embed.set_thumbnail(url="{}".format(member.display_avatar))
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await channel.send(embed=embed)
            await ctx.send('<:confirmed:721581574461587496>│`Feedback enviado com sucesso!`')
        except discord.HTTPException:
            await ctx.send("<:negate:721581573396496464>│`SEU FEEDBACK FOI GRANDE DEMAIS, TENTE MANDAR "
                           "EM PARTES!`")


async def setup(bot):
    await bot.add_cog(FeedBackClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mFEEDBACK\033[1;32m foi carregado com sucesso!\33[m')
