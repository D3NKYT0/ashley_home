import discord
import pytz

from datetime import datetime
from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='serverinfo', aliases=['infoserver', 'si', 'is', 'guildinfo', 'infoguild', 'gi', 'ig'])
    async def serverinfo(self, ctx):
        """comando que gera uma lista de informações da sua guild
        Use ash serverinfo"""

        afk = ctx.guild.afk_channel.name if ctx.guild.afk_channel else "Sem canal de AFK"
        verification_level = {
            "none": "Nenhuma",
            "low": "Baixo: Precisa ter um e-mail verificado na conta do discord.",
            "medium": "Médio: Precisa ter uma conta no discord há mais de 5 minutos.",
            "high": "Alta: Também precisa ser um membro deste servidor há mais de 10 minutos.",
            "table_flip": "Alta: Precisa ser um membro deste servidor há mais de 10 minutos.",
            "extreme": "Extrema: Precisa ter um telefone verificado na conta do discord.",
            "double_table_flip": "Extrema: Precisa ter um telefone verificado na conta do discord."
        }

        verification = verification_level.get(str(ctx.guild.verification_level))

        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")

        if data is not None:
            link = f'{self.bot.config["config"]["site"]}/guild/{ctx.guild.id}'
            database = f"**[Clique Aqui]({link})**"
        else:
            database = "SERVIDOR NAO CADASTRADO"

        if data['vip']:
            status = "<:vip_guild:546020055440425016>"
        else:
            status = "<:negate:721581573396496464>"
        try:
            cmds = str(data['data']['commands']) + " comandos contabilizados no total"
        except KeyError:
            cmds = str(self.bot.guilds_commands[ctx.guild.id]) + "comandos usados desde que fiquei online"
        hour = datetime.utcnow().astimezone(pytz.timezone('America/Sao_Paulo')).strftime("%H:%M")
        created = ctx.guild.created_at
        embed = discord.Embed(title="\n", color=self.color, description="Abaixo está as informaçoes principais do "
                                                                        "servidor!")
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_footer(text="{} • {}".format(ctx.author, hour))
        embed.add_field(name="Nome:", value=ctx.guild.name, inline=True)
        embed.add_field(name="Dono:", value=str(ctx.guild.owner))
        embed.add_field(name="ID:", value=ctx.guild.id, inline=True)
        embed.add_field(name="Cargos:", value=str(len(ctx.guild.roles)), inline=True)
        embed.add_field(name="Membros:", value=str(len(ctx.guild.members)), inline=True)
        embed.add_field(name="Canais de Texto", value=f'{len(ctx.guild.text_channels)}', inline=True)
        embed.add_field(name="Canais de Voz", value=f"{len(ctx.guild.voice_channels)}", inline=True)
        embed.add_field(name="Canal de AFK", value=str(afk), inline=True)
        embed.add_field(name="Bots:", value=str(len([a for a in ctx.guild.members if a.bot])), inline=True)
        embed.add_field(name="Nível de verificação", value=f"{verification}", inline=True)
        embed.add_field(name="Criado em:", value=f"<t:{created:%s}:f>", inline=True)
        embed.add_field(name="Comandos Usados: ", value=str(cmds), inline=True)
        embed.add_field(name="Vip: ", value=status, inline=True)
        embed.add_field(name="DataBase:", value=database)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mSERVERINFO\033[1;32m foi carregado com sucesso!\33[m')
