import copy
import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=False)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='help', aliases=['ajuda'])
    async def help(self, ctx, *, command_help=None):
        """há fala serio!"""
        if command_help is None:
            embed = discord.Embed(title="-==Artigo de Ajuda==-\nPara detalhar o comando use: ash help <command>",
                                  color=self.color, description=f"Olá {ctx.author.name}, eu sou a **Ashley**, um bot "
                                                                f"de diversão e jogos, incluindo RPG de turnos e "
                                                                f"sistemas de economia completo!")

            embed.add_field(name="**Categorias de comandos:**",
                            value="🔧 [Comandos Admin](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#-comandos-admin)\n"
                                  "👩 [Comandos Ashley](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#-comandos-ashley)\n"
                                  "❇️ [Comandos Funny](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#%EF%B8%8F-comandos-funny)\n"
                                  "🕹️ [Comandos Mini-Games](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#%EF%B8%8F-comandos-mini-games)\n"
                                  "🖼️ [Comandos Image](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#%EF%B8%8F-comandos-image)\n"
                                  "👥 [Comandos Guild](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#-comandos-guild)\n"
                                  "👤 [Comandos Member](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#-comandos-member)\n"
                                  "💰 [Comandos Economy](https://github.com/Ashley-Lab/ashley_home/wiki/Comandos#-comandos-economy)",
                            inline=False)

            embed.add_field(name="**Extras:**", 
                            value="ℹ [Sobre a Ashley](https://github.com/Ashley-Lab/ashley_home/wiki/Sobre)\n"
                                  "📓 [Iniciando na Ashley](https://github.com/Ashley-Lab/ashley_home/wiki/Iniciando-na-Ashley)\n"
                                  "👑 [Benefícios VIP](https://github.com/Ashley-Lab/ashley_home/wiki/Beneficios-VIP)\n"
                                  "<:gemash:761064114650873877> [Blessed Ethernya](https://github.com/Ashley-Lab/ashley_home/wiki/Blessed-Ethernya)\n"
                                  "🏰 [Lore](https://github.com/Ashley-Lab/ashley_home/wiki/Lore)\n"
                                  "🌎 [Províncias](https://github.com/Ashley-Lab/ashley_home/wiki/Provincias)\n",
                            inline=False)

            embed.add_field(name="**Acesso nosso Artigo de Ajuda**",
                            value="[Clique Aqui](https://github.com/Ashley-Lab/Ashley/blob/master/README.md)",
                            inline=False)

            embed.set_author(name=ctx.me.name, icon_url=ctx.me.avatar_url)
            embed.set_thumbnail(url="http://sisadm2.pjf.mg.gov.br/imagem/ajuda.png")
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)
        else:
            msg = copy.copy(ctx.message)
            msg.content = 'ash ' + command_help
            ctx_ = await self.bot.get_context(msg)
            if ctx_.command is not None:
                if ctx_.command.help is not None:
                    text = f"`{ctx_.prefix + ctx_.command.qualified_name + ' ' + ctx_.command.signature}`"
                    return await ctx.send(f"**Modo de Uso:** {text}\n```{ctx_.command.help}```")
                await ctx.send("<:alert:739251822920728708>│`Comando Ainda nao tem uma ajuda definida`")
            else:
                await ctx.send("<:alert:739251822920728708>│`Comando Inválido`")


def setup(bot):
    bot.add_cog(Helper(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mAJUDA\033[1;32m foi carregado com sucesso!\33[m')
