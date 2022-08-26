import sys
import disnake
import traceback
import aiohttp

from disnake.ext import commands
from resources.utility import ERRORS

cor = {
    'clear': '\033[m',
    'cian': '\033[1;36m',
    'roxo': '\033[1;35m',
    'azul': '\033[1;34m',
    'amar': '\033[1;33m',
    'verd': '\033[1;32m',
    'verm': '\033[1;31m',
    'pers': '\033[1;35;47m'
}


class SlashCommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color
        self.read = ["read letter", "read assemble", "read aungen", "read soul", "read nw", "read waffen"]
        self.errors = [aiohttp.ClientOSError, ConnectionResetError, disnake.errors.DiscordServerError,
                       disnake.errors.HTTPException]
        self.errors_str = [
            "Command raised an exception: HTTPException: 504 Gateway Time-out (error code: 0): <!DOCTYPE html>",
            "Command raised an exception: discordServerError: 500 Internal Server Error (error code: 0): 500: "
            "Internal Server Error",
            "Command raised an exception: discordServerError: 503 Service Temporarily Unavailable (error code: 0):"
            " <html> ",
            "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions",
            "Command raised an exception: discordServerError: 503 Service Unavailable (error code: 0): upstream"
            "connect error or disconnect/reset before headers. reset reason: connection failure",
            "aiohttp.client_exceptions.ClientOSError: [Errno 32] Broken pipe",
            "Command raised an exception: ClientOSError: [Errno 104] Connection reset by peer",
            "disnake.errors.DiscordServerError: 500 Internal Server Error (error code: 0): 500: Internal Server Error"
        ]

    def error_check(self, error):
        for _err in self.errors:
            if isinstance(error, _err):
                return True
        for _errs in self.errors_str:
            if error.__str__() == _errs or _errs in error.__str__() or error.__str__() in _errs:
                return True
        return False

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):

        if error.__str__() in ERRORS:
            return

        # Isso faz com que os comandos com argumentos invalidos tenham um retorno explicatorio!
        if isinstance(error, commands.BadArgument):
            perms = inter.channel.permissions_for(inter.me)
            if perms.send_messages and perms.read_messages:
                inter.command.reset_cooldown(inter)
                return await inter.response.send_message(
                    f'<:alert:739251822920728708>│`VOCE INSERIU UMA INFORMAÇÃO INVALIDA! POR FAVOR '
                    f'TENTE NOVAMENTE OU USE O COMANDO:` **ASH HELP {str(inter.command).upper()}**'
                    f' `PARA MAIORES INFORMAÇÕES.`')

        # Todos os eventos de erros ignorados, qualquer coisa ignorada retornará e impedirá que algo aconteça.
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.UserInputError):
            if self.bot.maintenance and inter.author.id not in self.bot.testers:
                perms = inter.channel.permissions_for(inter.me)
                if perms.send_messages and perms.read_messages:
                    embed = disnake.Embed(color=self.color, description=self.bot.maintenance_msg)
                    return await inter.response.send_message(embed=embed)
            return

        # Qualquer interação vazia nao gera erro no terminal
        if isinstance(error, disnake.errors.NotFound):
            return

        # Qualquer comando desabilitado retornará uma mensagem de aviso
        if isinstance(error, commands.DisabledCommand):
            perms = inter.channel.permissions_for(inter.me)
            if perms.send_messages and perms.read_messages:
                return await inter.response.send_message(
                    f'<:negate:721581573396496464>│**{inter.command}** `foi desabilitado`')

        # Manipulação de erros voltados para erro de checagem, aqui eu trato de maneira particular erros de Check
        # dentro dos comandos para fins pessoais, ignorando totalmente os padroes comuns.
        if isinstance(error, commands.CheckFailure):
            if error.__str__() == 'The check functions for command register guild failed.':
                perms = inter.channel.permissions_for(inter.me)
                if perms.send_messages and perms.read_messages:
                    return await inter.response.send_message(
                        f"<:negate:721581573396496464>│`VOCÊ NÃO TEM PERMISSÃO PARA USAR ESSE "
                        f"COMANDO!`")

            perms = inter.channel.permissions_for(inter.me)
            if perms.send_messages and perms.read_messages:
                return await inter.response.send_message(f"{error}")

        # aqui faço as verificações dos cooldowns dos comandos padroes
        # obs: existem comandos com cooldowns personalizados que nao entram nesse contexto
        if isinstance(error, commands.CommandOnCooldown):
            perms = inter.channel.permissions_for(inter.me)
            if perms.send_messages and perms.read_messages and float(
                    "{:.2f}".format(error.retry_after)) > 6.0:
                return await inter.response.send_message(
                    f"<:alert:739251822920728708>│**Aguarde**: `Você deve esperar` **{{:.2f}}** "
                    f"`segundos` `para mandar outro comando!`".format(error.retry_after),
                    delete_after=float("{:.2f}".format(error.retry_after)))

        # Check de Erros fora de CTX
        if self.error_check(error):
            if str(inter.command) in ["wave"]:
                if inter.author.id not in self.bot.recovery:
                    self.bot.recovery.append(inter.author.id)
            if str(inter.command) in ["battle", "boss", "wave", "pvp"]:
                if inter.author.id in self.bot.batalhando:
                    self.bot.batalhando.remove(inter.author.id)
            if str(inter.command) in ["card", "whats", "hot", "guess", "hangman", "jkp", "pokemon"]:
                if inter.author.id in self.bot.jogando:
                    self.bot.jogando.remove(inter.author.id)
            if str(inter.command) in ["marry", "divorce"]:
                if inter.author.id in self.bot.casando:
                    self.bot.casando.remove(inter.author.id)
            if str(inter.command) in ["box buy", "box booster", "craft"]:
                if inter.author.id in self.bot.comprando:
                    self.bot.comprando.remove(inter.author.id)
            if str(inter.command) in ["mine"]:
                if inter.author.id in self.bot.minerando:
                    self.bot.minerando.remove(inter.author.id)
            if str(inter.command) in ["pvp"]:
                if inter.author.id in self.bot.desafiado:
                    self.bot.desafiado.remove(inter.author.id)
            if str(inter.command) in self.read:
                if inter.author.id in self.bot.lendo:
                    self.bot.lendo.remove(inter.author.id)
            if str(inter.command) in ["dungeon"]:
                if inter.author.id in self.bot.explorando:
                    self.bot.explorando.remove(ctx.author.id)

            # retorno da msg de erro fora de CTX
            await inter.response.send_message(
                f"<:alert:739251822920728708>│{inter.author.mention} `HOUVE UM ERRO NA API DO DISCORD E "
                f"SEU COMANDO FOI PARADO NO MEIO DO PROCESSO, INFELIZMENTE VOCÊ VAI TERÁ QUE USAR O "
                f"COMANDO NOVAMENTE!`", delete_after=30.0)

        # Todos os outros erros não retornados vêm aqui... E podemos mostrar o TraceBack padrão.
        # como nao quero print de comando esperando para ser usado, faço a exceção
        # e como nao quero print de comando mal executado pelo usuario faço a outra exceção
        if not isinstance(error, commands.CommandOnCooldown) and not isinstance(error, commands.CheckFailure):
            # nao quero mostrar os erros de API e desconexão
            if not isinstance(error, disnake.errors.DiscordServerError) or self.error_check(error):
                # aqui quando um erro nao é tratado eu registro sua ocorrencia para averiguar sua origem
                # PRINT INTERNO (disnake LOG)
                channel = self.bot.get_channel(530419409311760394)
                perms = inter.channel.permissions_for(inter.me)
                if perms.send_messages and perms.read_messages:
                    await channel.send(f"<:negate:721581573396496464>│`Ocorreu um erro no comando:` "
                                       f"**{inter.application_command}**, `no servidor:` **{inter.guild}**, "
                                       f"`no canal:` **{inter.channel}** `com o membro:` **{inter.author}**  "
                                       f"`com o id:` **{inter.author.id}**, `com o erro:` "
                                       f"**{error.__str__()[:1500]}**")

                # aqui so passa os logs dos erros nao tratados
                # PRINT EXTERNO (PAPERTRAIL LOG)
                print(f"{cor['verm']}( ❌ ) | error in command: {cor['azul']}{str(inter.application_command).upper()}\n"
                      f"{cor['verm']}>> in Guild: "
                      f"{cor['azul']}{inter.guild} {cor['verm']}- {cor['amar']}ID: {inter.guild.id}\n"
                      f"{cor['verm']}>> in Channel: "
                      f"{cor['azul']}{inter.channel} {cor['verm']}- {cor['amar']}ID: {inter.channel.id}\n"
                      f"{cor['verm']}>> with the Member: "
                      f"{cor['azul']}{inter.author} {cor['verm']}- {cor['amar']}ID: {inter.author.id}\n"
                      f"{cor['verm']}>> with error:\n "
                      f"{cor['roxo']}{error}\n\n")

                # Permite verificar exceções originais geradas e enviadas para CommandInvokeError.
                # Se nada for encontrado. Mantemos a exceção passada para on_command_error.
                _error = getattr(error, 'original', error)

                # o print do traceback é para ver os erros mais detalhadamente
                # PRINT EXTERNO (TRACEBACK LOG)
                traceback.print_exception(type(_error), _error, _error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(SlashCommandErrorHandler(bot))
    print('\033[1;36m( 🔶 ) | O Handler \033[1;31mON_SLASH_COMMAND_ERROR\033[1;36m foi carregado com sucesso!\33[m')
