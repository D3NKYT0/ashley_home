import discord
from discord import app_commands
from discord.ext import commands
from stopwatch import Stopwatch as timer


class PingMSslash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Latencia do bot")
    @app_commands.guilds(discord.Object(id=519894833783898112))
    async def ping_slash(self, interaction: discord.Interaction):
        """comando pra verificar a latencia do bot
        Use ash ping"""
        if interaction.guild is not None:
            from datetime import datetime, timezone
            dt = datetime.now(timezone.utc)
            before_ws = int(round(self.bot.latency * 1000, 1))
            pingdb = timer()
            events = await self.bot.db.cd("events")
            events.find()
            pingdb.stop()
            await interaction.response.send_message(embed=discord.Embed(
                title="PING",
                color=0x3399ff,
                timestamp=dt,
                description=f"** Ping API:** `{before_ws} ms`\n"
                            f"**Tempo de Resposta da database:** `{pingdb}`"
            ).set_footer(text=f"Comando usado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url))


async def setup(bot):
    await bot.add_cog(PingMSslash(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mPINGMSSLASH\033[1;32m foi carregado com sucesso!\33[m')
