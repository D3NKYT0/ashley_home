import disnake
import psutil
import pytz

from disnake.ext import commands
from resources.check import check_it
from humanize import i18n, precisedelta
from resources.db import Database
from collections import Counter
from datetime import datetime as dt

i18n.activate("pt_BR")


class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='botinfo', aliases=['infobot', 'info', 'bi', 'ib'])
    async def botinfo(self, ctx):
        """Comando para ter informações sobre a Ashley
        Use ash botinfo"""
        total_members = sum(len(s.members) for s in self.bot.guilds)
        channel_types = Counter(isinstance(c, disnake.TextChannel) for c in self.bot.get_all_channels())
        ver_, voice, text = self.bot.version, channel_types[False], channel_types[True]
        owner, dated = str(self.bot.get_user(self.bot.owner_ids[0])), ctx.me.created_at
        uptime = precisedelta(dt.utcnow() - self.bot.start_time, format='%0.0f')
        date = dt.utcnow().astimezone(pytz.timezone('America/Sao_Paulo')).strftime("%H:%M")

        embed_bot = disnake.Embed(title='🤖 **Informações da Ashley**', color=self.color, description='\n')
        embed_bot.set_thumbnail(url=ctx.me.display_avatar)
        embed_bot.add_field(name="📨 | Comandos Executados",
                            value='**{}** `comandos`'.format(sum(self.bot.commands_used.values())), inline=False)
        embed_bot.add_field(name="📖 | Canais de texto", value='**{}** `canais de texto`'.format(text), inline=False)
        embed_bot.add_field(name="🎤 | Canais de voz", value='**{}** `canais de voz`'.format(voice), inline=False)
        embed_bot.add_field(name="<:processor:918166968509562911> | Porcentagem da CPU",
                            value="**{}%**".format(psutil.cpu_percent()), inline=False)
        embed_bot.add_field(name="<:memory:918166968849289216> | Memoria Usada", value=f'**{self.bot.get_ram()}**',
                            inline=False)
        embed_bot.add_field(name="<:mito:745375589145247804> | Entre no meu servidor",
                            value="[Clique Aqui](https://disnake.gg/rYT6QrM)", inline=False)
        embed_bot.add_field(name='`💮 | Nome`', value=ctx.me.name, inline=False)
        embed_bot.add_field(name='`◼ | Id bot`', value=ctx.me.id, inline=False)
        embed_bot.add_field(name='💠 | Criado em', value=f"<t:{dated:%s}:f>",
                            inline=False)
        embed_bot.add_field(name='📛 | Tag', value=ctx.me, inline=False)
        embed_bot.add_field(name='‍💻 | Servidores', value=str(len(self.bot.guilds)), inline=False)
        embed_bot.add_field(name='👥 | Usuarios', value='{}'.format(total_members), inline=False)
        embed_bot.add_field(name='‍⚙ | Programador', value=str(owner), inline=False)
        embed_bot.add_field(name='🐍 Python  | Version', value=f"`{self.bot.python_version}`", inline=False)
        embed_bot.add_field(name='<:cool:745375589245911190> Bot  | Version', value=str(ver_), inline=False)
        embed_bot.add_field(name="<a:loading:520418506567843860> | Tempo Online", value=f"{uptime}", inline=False)
        embed_bot.add_field(name="<:yep:745375589564809216> | Me add em seu Servidor",
                            value="[Clique Aqui](https://disnakeapp.com/oauth2/authorize?client_id=478977311266570242&s"
                                  "cope=bot&permissions=806218998)", inline=False)
        embed_bot.set_footer(text=f"Comando usado por {ctx.author} às {date}",
                             icon_url=ctx.author.display_avatar)
        await ctx.send(delete_after=120, embed=embed_bot)


def setup(bot):
    bot.add_cog(BotInfo(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mBOTINFO\033[1;32m foi carregado com sucesso!\33[m')
