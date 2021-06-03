import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class WikiClass(commands.Cog):
    """docstring for WikiClass"""

    def __init__(self, bot):
        super(WikiClass, self).__init__()
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='wiki', aliases=['pesquisar'])
    async def wiki(self, ctx, *, item=None):
        wiki, file = self.bot.config['wiki'], None
        if item is not None:
            item = item.lower()
            if item in wiki.keys():
                wiki, desc, rare, how = wiki[item], wiki['description'], wiki['rare'], wiki['how']
                typew, img, item = wiki['type'], wiki['image'], "exódia, o proibido" if item == "exodia" else item
                description = f'{item.title()}\n' \
                              f'\u200b\n' \
                              f'**Descrição**: {desc}\n' \
                              f'**Tipo**: {typew}\n' \
                              f'**Raridade**: {rare}\n' \
                              f'**Como Adquirir**: {how}'
                embed = discord.Embed(title=f"Wikipedia", color=self.bot.color, description=description)
                embed.set_thumbnail(url="http://sisadm2.pjf.mg.gov.br/imagem/ajuda.png")
                if img:
                    file = discord.File(img, filename="image.png")
                    embed.set_image(url=f'attachment://image.png')
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send('<:negate:721581573396496464>|`DIGITE UM NOME DE UM ITEM VÁLIDO.`')
        else:
            await ctx.send('<:negate:721581573396496464>|`DIGITE UM NOME DE UM ITEM. CASO NAO SAIBA USE O COMANDO:`'
                           ' **ASH WIKI** `PARA VER A WIKI DE UM ITEM!`')


def setup(bot):
    bot.add_cog(WikiClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mWIKI_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
