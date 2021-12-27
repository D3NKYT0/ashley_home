import disnake
import asyncio

from disnake.ext import commands
from resources.db import Database
from resources.check import check_it
from stopwatch import Stopwatch as timer


class PingMSslash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='ping', aliases=['latency'])
    @commands.slash_command(name="ping", description="Latencia do bot", guild_ids=[519894833783898112])
    async def ping(self, inter):
        """comando pra verificar a latencia do bot
        Use ash ping"""
        if inter.guild is not None:
            ping = round(self.bot.latency * 1000)
            await inter.response.send_message("🏓 `Pong:` **{}ms**".format(ping))

            dt = disnake.utils.utcnow()
            """ Pong! """
            before_ws = int(round(self.bot.latency * 1000, 1))
            pingdb = timer()
            await self.bot.pool.execute('SELECT version();')
            pingdb.stop()
            _timer = timer()
            mes = await inter.response.send_message(embed=disnake.Embed(title="Calculando o ping..."))
            _timer.stop()
            await asyncio.sleep(1)
            await mes.edit_message(embed=disnake.Embed(
                title="PING",
                color=0x3399ff,
                timestamp=dt,
                description=f"**:api: Ping API:** `{before_ws} ms`\n"
                            f"**:time: Tempo de Resposta:** `{_timer}`\n"
                            f"**:databasetime: Tempo de Resposta da database:** `{pingdb}`"
            ).set_footer(text=f"Comando usado por {ctx.author.name}", icon_url=ctx.author.display_avatar)
                           )


def setup(bot):
    bot.add_cog(PingMSslash(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mPINGMSSLASH\033[1;32m foi carregado com sucesso!\33[m')
