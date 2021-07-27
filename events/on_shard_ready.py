import json
from resources.color import random_color
from discord import Embed
from discord.ext import commands
from resources.webhook import Webhook
from datetime import datetime

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())


class Shards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color
        self.webhook = Webhook(url=_auth["_t__webhook_ready"])

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):

        commands_log = self.bot.get_channel(575688812068339717)
        text = f"**O shard** `{shard_id}` **se encontra pronto para uso**"
        embed = Embed(color=self.color, description=text)
        await commands_log.send(embed=embed)

        self.webhook.embed = Embed(
            colour=random_color(),
            description=f"**O shard** `{shard_id}` **se encontra pronto para uso**\nAproveite o dia ;)",
            timestamp=datetime.utcnow()
        ).set_author(
            name=f"Shard {shard_id}",
            icon_url=self.bot.user.avatar_url
        ).set_thumbnail(
            url=self.bot.user.avatar_url
        ).to_dict()
        if _auth["on_shard"]:
            await self.webhook.send()


def setup(bot):
    bot.add_cog(Shards(bot))
    print('\033[1;33m( 🔶 ) | O evento \033[1;34mON_SHARD_READY\033[1;33m foi carregado com sucesso!\33[m')
