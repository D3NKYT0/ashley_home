import discord
import psutil

from discord.ext import commands
from resources.check import check_it
from datetime import datetime
from resources.db import Database
from collections import Counter
from datetime import datetime as dt


class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @staticmethod
    def format_delta(delta, fmt):
        d = {"days": delta.days}
        d['hours'], rem = divmod(delta.seconds, 3600)
        d['years'], d['dias'] = divmod(delta.days, 365)
        d['minutes'], d['seconds'] = divmod(rem, 60)
        return fmt.format(**d)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='botinfo', aliases=['infobot', 'info', 'bi', 'ib'])
    async def botinfo(self, ctx):
        """Comando para ter informações sobre a Ashley
        Use ash botinfo"""
        total_members = sum(len(s.members) for s in self.bot.guilds)
        channel_types = Counter(isinstance(c, discord.TextChannel) for c in self.bot.get_all_channels())
        ver_, voice, text = self.bot.version, channel_types[False], channel_types[True]
        owner = str(self.bot.get_user(self.bot.owner_id))
        txt = "{hours} horas, {minutes} minutos e {seconds} segundos."
        uptime = self.format_delta((dt.utcnow() - self.bot.start_time), txt)

        embed_bot = discord.Embed(title='🤖 **Informações da Ashley**', color=self.color, description='\n')
        embed_bot.set_thumbnail(url=self.bot.user.avatar_url)
        embed_bot.add_field(name="📨 | Comandos Executados",
                            value='**{}** `comandos`'.format(sum(self.bot.commands_used.values())), inline=False)
        embed_bot.add_field(name="📖 | Canais de texto", value='**{}** `canais de texto`'.format(text), inline=False)
        embed_bot.add_field(name="🎤 | Canais de voz", value='**{}** `canais de voz`'.format(voice), inline=False)
        embed_bot.add_field(name="<:processor:522400972094308362> | Porcentagem da CPU",
                            value="**{}%**".format(psutil.cpu_percent()), inline=False)
        embed_bot.add_field(name="<:memory:522400971406573578> | Memoria Usada", value=f'**{self.bot.get_ram()}**',
                            inline=False)
        embed_bot.add_field(name="<:mito:745375589145247804> | Entre no meu servidor",
                            value="[Clique Aqui](https://discord.gg/rYT6QrM)", inline=False)
        embed_bot.add_field(name='`💮 | Nome`', value=self.bot.user.name, inline=False)
        embed_bot.add_field(name='`◼ | Id bot`', value=self.bot.user.id, inline=False)
        embed_bot.add_field(name='💠 | Criado em', value=self.bot.user.created_at.strftime("%d %b %Y %H:%M"),
                            inline=False)
        embed_bot.add_field(name='📛 | Tag', value=self.bot.user, inline=False)
        embed_bot.add_field(name='‍💻 | Servidores', value=str(len(self.bot.guilds)), inline=False)
        embed_bot.add_field(name='👥 | Usuarios', value='{}'.format(total_members), inline=False)
        embed_bot.add_field(name='‍⚙ | Programador', value=str(owner), inline=False)
        embed_bot.add_field(name='🐍 Python  | Version', value=f"`{self.bot.python_version}`", inline=False)
        embed_bot.add_field(name='<:cool:745375589245911190> Bot  | Version', value=str(ver_), inline=False)
        embed_bot.add_field(name="<a:loading:520418506567843860> | Tempo Online", value=f"{uptime}", inline=False)
        embed_bot.add_field(name="<:yep:745375589564809216> | Me add em seu Servidor",
                            value="[Clique Aqui](https://discordapp.com/oauth2/authorize?client_id=478977311266570242&s"
                                  "cope=bot&permissions=8)", inline=False)
        embed_bot.set_footer(text="Comando usado por {} as {} Hrs".format(ctx.author, datetime.now().hour),
                             icon_url=ctx.author.avatar_url)
        await ctx.send(delete_after=120, embed=embed_bot)


def setup(bot):
    bot.add_cog(BotInfo(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mBOTINFO\033[1;32m foi carregado com sucesso!\33[m')
