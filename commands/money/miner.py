import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database


class Miner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='miner', aliases=['minerador'])
    async def miner(self, ctx):
        if ctx.invoked_subcommand is None:
            self.status()
            embed = disnake.Embed(color=self.color)
            embed.add_field(name="Miner Commands: [BETA TESTE]",
                            value=f"{self.st[117]} `miner create`")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @miner.group(name='create', aliases=['c'])
    async def _create(self, ctx, limit: int = None):
        if limit is None:
            msg = "<:negate:721581573396496464>│`Voce precisa dizer um limite de mineração`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if limit >= 100:
            msg = "<:negate:721581573396496464>│`O limite de mineração nao pode ser maior que 100`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if f"{ctx.author.id}" in self.bot.minelist.keys():
            if self.bot.minelist[f"{ctx.author.id}"]["active"]:
                msg = "<:negate:721581573396496464>│`Você ja tem um minerador ativo`"
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        miner = {"active": False, "user_id": ctx.author.id, "limit": limit}
        self.bot.minelist[f"{ctx.author.id}"] = miner
        msg = "<:confirmed:721581574461587496>│`Minerador criado com sucesso`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Miner(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMINER_GROUP\033[1;32m foi carregado com sucesso!\33[m')
