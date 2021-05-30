import discord

from discord.ext import commands
from config import data as config
from asyncio import sleep
from resources.utility import include


class SystemMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is not None and str(message.author.id) not in self.bot.blacklist:

            # filtro de comandos ( para nao haver iteração em cima de comandos )
            # -----------======================-----------
            ctx = await self.bot.get_context(message)
            if ctx.command is not None:
                return
            # -----------======================-----------

            cl = await self.bot.db.cd("guilds")
            data_guild = await cl.find_one({"guild_id": message.guild.id}, {"_id": 0, "guild_id": 1})
            if data_guild is None:
                try:
                    if message.mentions[0] == self.bot.user:

                        perms = ctx.channel.permissions_for(ctx.me)
                        if not perms.send_messages or not perms.read_messages:
                            return

                        await message.channel.send('<:negate:721581573396496464>│`Sua guilda ainda não está '
                                                   'registrada, por favor digite:` **ash register guild** '
                                                   '`para cadastrar sua guilda no meu` **banco de dados!**')
                except IndexError:
                    pass


def setup(bot):
    bot.add_cog(SystemMessage(bot))
    print('\033[1;33m( 🔶 ) | O evento \033[1;34mON_MESSAGE\033[1;33m foi carregado com sucesso!\33[m')
