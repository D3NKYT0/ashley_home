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


class SelectProvinces(disnake.ui.Select):
    def __init__(self, provinces, bot):
        self.provinces = provinces
        self.bot = bot
        super().__init__(
            placeholder="Selecione uma provincia",
            options=[disnake.SelectOption(label=province, value=province) for province in self.provinces],
            min_values=1, max_values=1)

    async def callback(self, inter):
        exchange = inter.values[0]

        description = f"```\n" \
                      f"Provincia selecionada: {exchange}" \
                      f"```"

        embed = disnake.Embed(color=self.bot.color, title="BITASH CORRETORA", description=description)
        cd = await self.bot.db.cd("exchanges")
        tot, emo = 1000, ['🟢', '🔴', '🟠', '⚪']  # verde / vermelho / laranja / branco

        value = self.bot.broker.get_exchange(exchange)
        be = self.bot.broker.format_bitash(value / self.bot.current_rate)
        be_tot = self.bot.broker.format_bitash(value / self.bot.current_rate * tot)

        data = await cd.find_one({"_id": exchange})
        ast, sold = len(data['assets'].keys()), len(data['sold'].keys())

        text = f"`Able:` **{ast}**`/1000`\n" \
               f"`Sold:` **{sold}**\n" \
               f"`Value:` **{be}** `BTA`\n" \
               f"`Total:` **{be_tot}**"

        _emo = emo[3] if ast == tot else emo[0] if 100 <= ast <= 999 else emo[2] if 1 <= ast <= 99 else emo[1]
        embed.add_field(name=f"{_emo} {exchange}", value=text, inline=True)

        embed.set_thumbnail(url=inter.user.display_avatar)
        embed.set_footer(text=f"Ashley ® Todos os direitos reservados.")

        await inter.response.edit_message(embed=embed, view=ProvinceExchange(value, self.bot))


class ProvinceExchange(disnake.ui.View):
    def __init__(self, province, bot):
        self.province = province
        self.bot = bot
        super().__init__()

    @disnake.ui.button(label="Buy", style=disnake.ButtonStyle.green)
    async def _buy(self, button, inter):

        if button:
            pass

        provinces = list(self.bot.broker.exchanges.keys())
        view = ViewDefault(inter.user)
        view.add_item(SelectProvinces(provinces, self.bot))

        embed = disnake.Embed(description="COMPRADO!")

        await inter.response.edit_message(embed=embed, view=view)

    @disnake.ui.button(label="Sell", style=disnake.ButtonStyle.primary)
    async def _sell(self, button, inter):

        if button:
            pass

        provinces = list(self.bot.broker.exchanges.keys())
        view = ViewDefault(inter.user)
        view.add_item(SelectProvinces(provinces, self.bot))

        embed = disnake.Embed(description="VENDIDO!")

        await inter.response.edit_message(embed=embed, view=view)

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.gray)
    async def _back(self, button, inter):

        if button:
            pass

        provinces = list(self.bot.broker.exchanges.keys())
        view = ViewDefault(inter.user)
        view.add_item(SelectProvinces(provinces, self.bot))

        description = "```\n" \
                      "Legenda das Cores:\n" \
                      "Branco: Todas as ações disponivel\n" \
                      "Verde: Muitas ações disponiveis\n" \
                      "Laranja: Poucas ações disponiveis\n" \
                      "Vermelho: Nenhuma ação disponivel" \
                      "```"

        embed = disnake.Embed(color=self.bot.color, title="BITASH CORRETORA", description=description)
        cd = await self.bot.db.cd("exchanges")
        tot_global, tot, emo = 0, 1000, ['🟢', '🔴', '🟠', '⚪']  # verde / vermelho / laranja / branco

        for exchange in provinces:
            value = self.bot.broker.get_exchange(exchange)
            be = self.bot.broker.format_bitash(value / self.bot.current_rate)
            be_tot = self.bot.broker.format_bitash(value / self.bot.current_rate * tot)
            tot_global += value / self.bot.current_rate * tot

            data = await cd.find_one({"_id": exchange})
            ast, sold = len(data['assets'].keys()), len(data['sold'].keys())

            text = f"`Able:` **{ast}**`/1000`\n" \
                   f"`Sold:` **{sold}**\n" \
                   f"`Value:` **{be}** `BTA`\n" \
                   f"`Total:` **{be_tot}**"

            _emo = emo[3] if ast == tot else emo[0] if 100 <= ast <= 999 else emo[2] if 1 <= ast <= 99 else emo[1]
            embed.add_field(name=f"{_emo} {exchange}", value=text, inline=True)

        embed.set_thumbnail(url=inter.user.display_avatar)
        et = self.bot.broker.format_value(tot_global * self.bot.current_rate)
        bk = self.bot.broker.format_bitash(tot_global)
        embed.set_footer(text=f"Valor Total da bolsa: {bk} BTA (bitash) | {et} ethernyas")

        await inter.response.edit_message(embed=embed, view=view)

    @disnake.ui.button(label="Exit", style=disnake.ButtonStyle.danger)
    async def _exit(self, button, inter):

        if button:
            pass

        msg = "<:confirmed:721581574461587496>│`Voce fechou a corretora!`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await inter.response.edit_message(embed=embed)


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
    @commands.group(name='broker', aliases=['corretora'])
    async def broker(self, ctx):
        if ctx.invoked_subcommand is None:
            provinces = list(self.bot.broker.exchanges.keys())
            view = ViewDefault(ctx.author)
            view.add_item(SelectProvinces(provinces, self.bot))

            description = "```\n" \
                          "Legenda das Cores:\n" \
                          "Branco: Todas as ações disponivel\n" \
                          "Verde: Muitas ações disponiveis\n" \
                          "Laranja: Poucas ações disponiveis\n" \
                          "Vermelho: Nenhuma ação disponivel" \
                          "```"

            embed = disnake.Embed(color=self.bot.color, title="BITASH CORRETORA", description=description)
            cd = await self.bot.db.cd("exchanges")
            tot_global, tot, emo = 0, 1000, ['🟢', '🔴', '🟠', '⚪']  # verde / vermelho / laranja / branco

            for exchange in provinces:
                value = self.bot.broker.get_exchange(exchange)
                be = self.bot.broker.format_bitash(value / self.bot.current_rate)
                be_tot = self.bot.broker.format_bitash(value / self.bot.current_rate * tot)
                tot_global += value / self.bot.current_rate * tot

                data = await cd.find_one({"_id": exchange})
                ast, sold = len(data['assets'].keys()), len(data['sold'].keys())

                text = f"`Able:` **{ast}**`/1000`\n" \
                       f"`Sold:` **{sold}**\n" \
                       f"`Value:` **{be}** `BTA`\n" \
                       f"`Total:` **{be_tot}**"

                _emo = emo[3] if ast == tot else emo[0] if 100 <= ast <= 999 else emo[2] if 1 <= ast <= 99 else emo[1]
                embed.add_field(name=f"{_emo} {exchange}", value=text, inline=True)

            embed.set_thumbnail(url=ctx.author.display_avatar)
            et = self.bot.broker.format_value(tot_global * self.bot.current_rate)
            bk = self.bot.broker.format_bitash(tot_global)
            embed.set_footer(text=f"Valor Total da bolsa: {bk} BTA (bitash) | {et} ethernyas")

            await ctx.send(embed=embed, view=view)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @broker.group(name='wallet', aliases=['w', 'carteira'])
    async def _wallet(self, ctx):
        await ctx.send("Sua carteira está vazia...")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='miner', aliases=['minerador'])
    async def miner(self, ctx):
        if ctx.invoked_subcommand is None:
            self.status()
            embed = disnake.Embed(color=self.color)
            embed.add_field(name="Miner Commands: [BETA TESTE]",
                            value=f"{self.st[117]} `miner create`\n"
                                  f"{self.st[117]} `miner config`\n"
                                  f"{self.st[117]} `miner start`\n"
                                  f"{self.st[117]} `miner stop`\n")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @miner.group(name='create', aliases=['c'])
    async def _create(self, ctx):
        msg = "<:negate:721581573396496464>│`Comando em criação...`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        return await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @miner.group(name='config', aliases=['configurar', 'cf'])
    async def _config(self, ctx):
        msg = "<:negate:721581573396496464>│`Comando em criação...`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        return await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @miner.group(name='start', aliases=['s', 'iniciar', 'inicio'])
    async def _start(self, ctx, limit: int = None):
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
        msg = "<:confirmed:721581574461587496>│`Minerador iniciado com sucesso`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @miner.group(name='stop', aliases=['st'])
    async def _stop(self, ctx):

        if ctx.author.id not in self.bot.minelist.keys():
            msg = "<:negate:721581573396496464>│`Você nao tem um minerador ativo no momento!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.minelist[f"{ctx.author.id}"]["status"] = False
        msg = "<:confirmed:721581574461587496>│`Minerador parado com sucesso`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Miner(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMINER_GROUP\033[1;32m foi carregado com sucesso!\33[m')
