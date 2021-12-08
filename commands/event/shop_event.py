import disnake
import copy

from asyncio import TimeoutError
from disnake.ext import commands
from resources.db import Database
from resources.check import check_it
from resources.utility import paginator


class ShopEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

        equips_dict = dict()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_dict[k] = v

        self.eq = equips_dict

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='eventshop', aliases=['ev'])
    async def event_shot(self, ctx):
        """Comando para comprar itens com moeda de evento"""
        if not self.bot.event_special:
            return await ctx.send(f"<:negate:721581573396496464>│`ATUALMENTE NAO TEM NENHUM EVENTO ESPECIAL!`")
            
        if ctx.invoked_subcommand is None:
            recipes = copy.deepcopy(self.bot.config['events'])
            await ctx.send(f"<:alert:739251822920728708>│`ITENS DISPONIVEIS PARA COMPRA ABAIXO`\n"
                           f"**EXEMPLO:** `USE` **ASH HALLOWEEN CRAFT MELTED ARTIFACT** "
                           f"`PARA COMPRAR UM MELTED ARTIFACT!`")
            embed = ['🎃 **LOJA HALLOWEEN** 🎃', self.bot.color, '']
            await paginator(self.bot, self.bot.items, recipes, embed, ctx)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @event_shot.command(name='craft', aliases=['criar', 'c'])
    async def _event_craft(self, ctx, *, item: str = None):
        """Comando usado pra comprar um item usando item de evento."""
        if ctx.author.id in self.bot.comprando:
            return await ctx.send('<:alert:739251822920728708>│`VOCE JA ESTA EM PROCESSO DE COMPRA...`')

        self.bot.comprando.append(ctx.author.id)
        recipes = copy.deepcopy(self.bot.config['events'])
        query_user = {"$inc": {}}
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        if item is not None:
            item = item.lower()
            if item in recipes.keys():
                recipe = recipes[item]
                description = '**Custo:**'
                maximo = None
                quant = 0

                for c in recipe['cost']:
                    try:
                        quant = data['inventory'][c[0]]
                    except KeyError:
                        quant = 0
                    description += f'\n{self.bot.items[c[0]][0]} **{c[1]}**/`{quant}` `{self.bot.items[c[0]][1]}`'

                description += '\n\n**Recompensa:**'

                for c in recipe['reward']:
                    try:
                        quant = data['inventory'][c[0]]
                    except KeyError:
                        quant = 0
                    description += f'\n{self.bot.items[c[0]][0]} **{c[1]}**/`{quant}` `{self.bot.items[c[0]][1]}`'

                _msg = "`Itens faltantes:`\n"
                for c in recipe['cost']:
                    try:
                        tempmax = data['inventory'][c[0]] // c[1]
                        if tempmax == 0:
                            _msg += f'<:alert:739251822920728708>|`Você não tem o item` ' \
                                    f'**{self.bot.items[c[0]][1]}** `suficiente no seu inventario.`\n'

                    except KeyError:
                        tempmax = 0
                        _msg += f'<:alert:739251822920728708>|`Você não tem o item` **{self.bot.items[c[0]][1]}** ' \
                                f'`suficiente no seu inventario.`\n'
                    if maximo is None or maximo > tempmax:
                        maximo = tempmax
                if _msg != "`Itens faltantes:`\n":
                    await ctx.send(_msg)

                description += '\n\n**Maximo que você pode craftar:** `{}`' \
                               '\n▶ **Craftar** `1`\n⏩ **Craftar** `2+`' \
                               '\n⏭ **Craftar o Maximo**\n❌ **Fechar**'.format(maximo)

                embed = disnake.Embed(
                    title='🎃 **CRAFT HALLOWEEN** 🎃\n(Custo/Quantidade no inventario)',
                    color=self.bot.color,
                    description=description)

                msg = await ctx.send(embed=embed)
                emojis = ['▶', '⏩', '⏭', '❌']

                for c in emojis:
                    await msg.add_reaction(c)

                def check_reaction(react, member):
                    try:
                        if react.message.id == msg.id:
                            if member.id == ctx.author.id:
                                return True
                        return False
                    except AttributeError:
                        return False

                try:
                    reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                except TimeoutError:
                    self.bot.comprando.remove(ctx.author.id)
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito! Comando '
                                          'cancelado.`', delete_after=5.0)

                if reaction[0].emoji == '▶' and reaction[0].message.id == msg.id:
                    try:
                        for c in recipe['cost']:
                            if data['inventory'][c[0]] >= c[1]:
                                data['inventory'][c[0]] -= c[1]
                                if data['inventory'][c[0]] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = dict()
                                    query_user["$unset"][f"inventory.{c[0]}"] = ""
                                    if f"inventory.{c[0]}" in query_user["$inc"].keys():
                                        del query_user["$inc"][f"inventory.{c[0]}"]
                                else:
                                    query_user["$inc"][f"inventory.{c[0]}"] = -c[1]
                            else:
                                self.bot.comprando.remove(ctx.author.id)
                                return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                                      'necessarios.`')
                    except KeyError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    for c in recipe['reward']:
                        query_user["$inc"][f"inventory.{c[0]}"] = c[1]

                elif reaction[0].emoji == '⏩' and reaction[0].message.id == msg.id:

                    def check_recipe(m):
                        if m.author.id == ctx.author.id and m.channel.id == ctx.channel.id:
                            if m.content.isdigit():
                                if int(m.content) > 0:
                                    return True
                        return False

                    msg_num = await ctx.send('<:alert:739251822920728708>│`Quantas receitas você quer fazer?`')
                    try:
                        resp = await self.bot.wait_for('message', check=check_recipe, timeout=60.0)
                    except TimeoutError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito:` **COMANDO'
                                              ' CANCELADO**')

                    while not self.bot.is_closed():
                        if int(resp.content) <= maximo:
                            break
                        await msg_num.delete()
                        msg_num = await ctx.send('<:alert:739251822920728708>│`Você nao consegue craftar essa '
                                                 'quantidade!`\n**Digite outro valor:**')
                        try:
                            resp = await self.bot.wait_for('message', check=check_recipe, timeout=60.0)
                        except TimeoutError:
                            self.bot.comprando.remove(ctx.author.id)
                            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito:` '
                                                  '**COMANDO CANCELADO**')

                    quant = int(resp.content)

                    try:
                        for c in recipe['cost']:
                            if data['inventory'][c[0]] >= c[1]:
                                data['inventory'][c[0]] -= c[1] * quant
                                if data['inventory'][c[0]] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = dict()
                                    query_user["$unset"][f"inventory.{c[0]}"] = ""
                                    if f"inventory.{c[0]}" in query_user["$inc"].keys():
                                        del query_user["$inc"][f"inventory.{c[0]}"]
                                else:
                                    query_user["$inc"][f"inventory.{c[0]}"] = -c[1] * quant
                            else:
                                self.bot.comprando.remove(ctx.author.id)
                                return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                                      'necessarios.`')
                    except KeyError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    for c in recipe['reward']:
                        query_user["$inc"][f"inventory.{c[0]}"] = c[1] * quant

                elif reaction[0].emoji == '⏭' and reaction[0].message.id == msg.id:
                    if maximo < 1:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    try:
                        for c in recipe['cost']:
                            if data['inventory'][c[0]] >= c[1]:
                                data['inventory'][c[0]] -= c[1] * maximo
                                if data['inventory'][c[0]] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = dict()
                                    query_user["$unset"][f"inventory.{c[0]}"] = ""
                                    if f"inventory.{c[0]}" in query_user["$inc"].keys():
                                        del query_user["$inc"][f"inventory.{c[0]}"]
                                else:
                                    query_user["$inc"][f"inventory.{c[0]}"] = -c[1] * maximo
                            else:
                                self.bot.comprando.remove(ctx.author.id)
                                return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                                      'necessarios.`')
                    except KeyError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    for c in recipe['reward']:
                        query_user["$inc"][f"inventory.{c[0]}"] = c[1] * maximo

                if reaction[0].emoji == "❌" and reaction[0].message.id == msg.id:
                    await msg.delete()
                    self.bot.comprando.remove(ctx.author.id)
                    return

                quantidade = 1
                if reaction[0].emoji == '⏩' and reaction[0].message.id == msg.id:
                    quantidade = quant
                if reaction[0].emoji == '⏭' and reaction[0].message.id == msg.id:
                    quantidade = maximo

                await msg.delete()
                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": data["user_id"]}, query_user, upsert=False)
                await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 `O ITEM` ✨ **{item.upper()}** ✨ "
                               f"`FOI CRAFTADO` **{quantidade}X** `COM SUCESSO!`")
                await self.bot.data.add_sts(ctx.author, "craft", 1)
        else:
            await ctx.send('<:negate:721581573396496464>|`DIGITE UM NOME DE UM ITEM. CASO NAO SAIBA USE O COMANDO:`'
                           ' **ASH HALLOWEEN** `PARA VER A LISTA DE ITENS DISPONIVEIS!`')
        self.bot.comprando.remove(ctx.author.id)


def setup(bot):
    bot.add_cog(ShopEvent(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mSHOP_EVENT\033[1;32m foi carregado com sucesso!\33[m')
