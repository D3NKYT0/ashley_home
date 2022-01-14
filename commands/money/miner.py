import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database


class ViewDefault(disnake.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__()

    async def interaction_check(self, inter):
        if inter.user.id != self.author.id:
            return False
        else:
            return True


class ProvinceExchange(disnake.ui.View):
    def __init__(self, province):
        self.province = province
        super().__init__()

    @disnake.ui.button(label="Buy", style=disnake.ButtonStyle.green)
    async def _buy(self, button, inter):
        pass

    @disnake.ui.button(label="Sell", style=disnake.ButtonStyle.danger)
    async def _sell(self, button, inter):
        pass

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.primary)
    async def _back(self, button, inter):

        if button:
            pass

        await inter.response.edit_message(embed=disnake.Embed(description="Menu Principal"), view=View)


class SelectProvinces(disnake.ui.Select):
    def __init__(self, provinces):
        self.provinces = provinces
        super().__init__(
            placeholder="Selecione uma provincia",
            options=[disnake.SelectOption(label=province, value=province) for province in self.provinces],
            min_values=1, max_values=1)

    async def callback(self, inter):
        value = inter.values[0]
        await inter.response.edit_message(embed=disnake.Embed(description=f"Provincia selecionada: {value}"),
                                          view=ProvinceExchange(value))


class Miner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color
        self.broker = self.bot.broker

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='bk')
    async def bk(self, ctx):

        provinces = list(self.bot.broker.exchanges.keys())
        view = ViewDefault(ctx.author)
        view.add_item(SelectProvinces(provinces))
        await ctx.send(embed=disnake.Embed(description=f"SISTEMA DE AÇÕES DA ASHLEY"), view=view)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='broker', aliases=['corretora'])
    async def broker(self, ctx):
        if ctx.invoked_subcommand is None:
            self.status()
            embed = disnake.Embed(color=self.color)
            embed.add_field(name="Broker Commands: [BETA TESTE]",
                            value=f"{self.st[117]} `broker buy` **compra ações na corretora**\n"
                                  f"{self.st[117]} `broker sell` **vende ações na corretora**\n"
                                  f"{self.st[117]} `broker asset` **mostra informações sobre um ativo**\n"
                                  f"{self.st[117]} `broker exchange` **mostra    informações sobre uma ação**\n"
                                  f"{self.st[117]} `broker exchanges` **mostra todas as ações disponiveis**\n"
                                  f"{self.st[117]} `broker wallet` **mostra todas as ações da sua carteira**")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='buy', aliases=['c', 'comprar'])
    async def _buy(self, ctx):
        pass

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='sell', aliases=['v', 'vender'])
    async def _sell(self, ctx):
        pass

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='asset', aliases=['a', 'ativo'])
    async def _asset(self, ctx):
        pass

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='exchange', aliases=['t', 'troca'])
    async def _exchange(self, ctx):
        pass

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='exchanges', aliases=['e', 'ex'])
    async def _exchanges(self, ctx):
        pass

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='wallet', aliases=['w', 'carteira'])
    async def _wallet(self, ctx):
        pass

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

            else:
                msg = "<:negate:721581573396496464>│`Você ja tem um minerador esperando para iniciar`"
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
