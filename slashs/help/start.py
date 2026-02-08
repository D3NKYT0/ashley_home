import discord
from discord import app_commands
from discord.ext import commands


class HelperSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @app_commands.command(name="help", description="Artigos de Ajuda")
    @app_commands.describe(command_help="Nome do comando para detalhar")
    async def help_slash(self, interaction: discord.Interaction, command_help: str = None):
        """há fala serio!"""
        if command_help is None:
            embed = discord.Embed(title="-==Artigo de Ajuda==-\nPara detalhar o comando use: ash help <command>",
                                  color=self.color, description=f"Olá {interaction.user.name}, eu sou a **Ashley**, um bot"
                                                                f" de diversão e jogos, incluindo RPG de turnos e "
                                                                f"sistemas de economia completo!")

            embed.add_field(name="**Categorias de comandos - Utilidades**:",
                            value="🔧 [Comandos Admin](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#-comandos"
                                  "-admin)\n "
                                  "👩 [Comandos Ashley](https://github.com/D3NKYT0/ashley_home/wiki/Comandos"
                                  "#-comandos-ashley)\n "
                                  "ℹ️ [Comandos Utility](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#%E2%84"
                                  "%B9%EF%B8%8F-comandos-utility)\n "
                                  "👑 [Comandos VIP](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#-comandos"
                                  "-vip)\n "
                                  "👥 [Comandos Guild](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#-comandos"
                                  "-guild)\n "
                                  "👤 [Comandos Member](https://github.com/D3NKYT0/ashley_home/wiki/Comandos"
                                  "#-comandos-member)",
                            inline=False)
            embed.add_field(name="**Categorias de comandos - Diversão**:",
                            value="⚔️ [Comandos RPG](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#%EF%B8%8F"
                                  "-comandos-rpg)\n "
                                  "💰 [Comandos Economy](https://github.com/D3NKYT0/ashley_home/wiki/Comandos"
                                  "#-comandos-economy)\n "
                                  "🕹️ [Comandos Mini-Games](https://github.com/D3NKYT0/ashley_home/wiki/Comandos"
                                  "#%EF%B8%8F-comandos-mini-games)\n "
                                  "❇️ [Comandos Funny](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#%EF%B8"
                                  "%8F-comandos-funny)\n "
                                  "🖼️ [Comandos Image](https://github.com/D3NKYT0/ashley_home/wiki/Comandos#%EF%B8"
                                  "%8F-comandos-image)",
                            inline=False)

            embed.add_field(name="**Extras:**",
                            value="ℹ [Sobre a Ashley](https://github.com/D3NKYT0/ashley_home/wiki/Sobre)\n"
                                  "📄 [Política de Privacidade](https://github.com/D3NKYT0/ashley_home/wiki/Pol%C3%ADtica"
                                  "-de-Privacidade)\n"
                                  "📓 [Iniciando na Ashley](https://github.com/D3NKYT0/ashley_home/wiki/Iniciando-na"
                                  "-Ashley)\n "
                                  "👑 [Benefícios VIP](https://github.com/D3NKYT0/ashley_home/wiki/Beneficios-VIP)\n"
                                  "<:gemash:761064114650873877> [Blessed Ethernya]("
                                  "https://github.com/D3NKYT0/ashley_home/wiki/Blessed-Ethernya)\n "
                                  "🏰 [Lore](https://github.com/D3NKYT0/ashley_home/wiki/Lore)\n"
                                  "🌎 [Províncias](https://github.com/D3NKYT0/ashley_home/wiki/Provincias)\n",
                            inline=False)

            embed.add_field(name="**Acesse a minha wiki para mais informações:**",
                            value="[Clique Aqui](https://github.com/D3NKYT0/ashley_home/wiki)",
                            inline=False)

            embed.set_author(name=interaction.client.user.name, icon_url=interaction.client.user.display_avatar.url)
            embed.set_thumbnail(url="http://sisadm2.pjf.mg.gov.br/imagem/ajuda.png")
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await interaction.response.send_message(embed=embed)
        else:

            all_commands = []
            for command in self.bot.commands:
                all_commands.append(command)
                if isinstance(command, commands.Group):
                    all_commands.extend(command.commands)

            command = None
            for cmd in all_commands:
                if cmd.qualified_name == command_help:
                    command = cmd

            if command is not None:

                if command.help is not None:
                    text = f"ash `{command.qualified_name + ' ' + command.signature}`"
                    return await interaction.response.send_message(f"**Modo de Uso:** {text}\n```{command.help}```")

                await interaction.response.send_message("<:alert:739251822920728708>│`Comando Ainda nao tem uma ajuda"
                                                  " definida`")

            else:
                await interaction.response.send_message("<:alert:739251822920728708>│`Comando Inválido`")


async def setup(bot):
    await bot.add_cog(HelperSlash(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mAJUDA\033[1;32m foi carregado com sucesso!\33[m')
