import disnake
import asyncio

from disnake.ext import commands
from resources.db import Database
from resources.check import check_it
from stopwatch import Stopwatch as timer


class PingMSslash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.slash_command(name="ping", description="Latencia do bot", guild_ids=[519894833783898112])
    async def ping(self, inter):
        """comando pra verificar a latencia do bot
        Use ash ping"""
        if inter.guild is not None:
            dt = disnake.utils.utcnow()
            before_ws = int(round(self.bot.latency * 1000, 1))
            pingdb = timer()
            events = await self.bot.db.cd("events")
            events.find()
            pingdb.stop()
            await inter.response.send_message(embed=disnake.Embed(
                title="PING",
                color=0x3399ff,
                timestamp=dt,
                description=f"** Ping API:** `{before_ws} ms`\n"
                            f"**Tempo de Resposta da database:** `{pingdb}`"
            ).set_footer(text=f"Comando usado por {inter.user.name}", icon_url=inter.user.display_avatar))


def setup(bot):
    bot.add_cog(PingMSslash(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mPINGMSSLASH\033[1;32m foi carregado com sucesso!\33[m')
