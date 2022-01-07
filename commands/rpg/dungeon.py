import copy
import disnake
import asyncio

from io import BytesIO
from asyncio import sleep
from random import randint
from disnake.ext import commands
from resources.db import Database
from resources.check import check_it
from disnake.ext.commands.core import is_owner
from dungeon.maps import Map, MovePlayer, Player


GUNDEONS = {
            "start_floor": [11, 30],
            "floor-1": [11, 30],
            "floor-2": [11, 30],
            "floor-3": [11, 30],
            "floor-4": [11, 30],
            "floor-5": [11, 30],
            "floor-6": [30, 30],
            "floor-7": [30, 30],
            "floor-8": [30, 30],
            "floor-9": [30, 30],
            "last-floor": [30, 30]
        }


class DugeonClass(commands.Cog):
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
    @commands.group(name="dungeon", aliases=['dg'])
    async def dungeon(self, ctx):
        if ctx.invoked_subcommand is None:
            self.status()
            embed = disnake.Embed(color=self.color)
            embed.add_field(name="Dungeons Commands:",
                            value=f"{self.st[117]} `dg tower` [Tower of Alhastor]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]\n"
                                  f"{self.st[117]} `dg -` [...]")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @dungeon.group(name="tower", aliases=['tw'])
    async def _tower(self, ctx):

        if ctx.author.id in self.bot.explorando:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ NUMA DUNGEON!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.explorando.append(ctx.author.id)

        # area da data do jogador
        #
        # -----------------------

        mapper = Map()
        map_now = mapper.get_map(img_map='start_floor')
        matriz, pos = mapper.get_matrix(map_now, GUNDEONS['start_floor'])
        x, y = pos[1][1], pos[1][0]
        vision = mapper.get_vision(map_now, [x, y])
        _map = mapper.create_map(vision, "vision_map")
        _emoji = "<:picket:928779628041080853>"
        _style = [disnake.ButtonStyle.gray, disnake.ButtonStyle.primary, disnake.ButtonStyle.green]

        move = MovePlayer(ctx.author)
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(emoji="⬆️", style=_style[1]))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(emoji="⬅️", style=_style[1], row=1))
        move.add_item(disnake.ui.Button(emoji=_emoji, style=_style[2], row=1))
        move.add_item(disnake.ui.Button(emoji="➡️", style=_style[1], row=1))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True, row=3))
        move.add_item(disnake.ui.Button(emoji="⬇️", style=_style[1], row=3))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True, row=3))

        with BytesIO() as file:
            _map.save(file, 'PNG')
            file.seek(0)
            embed = disnake.Embed(color=self.bot.color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
            embed.set_image(file=disnake.File(file, 'map.png'))
            msg = await ctx.send(embed=embed, view=move)

        player = Player(map_now, matriz, [x, y], ctx)

        while not ctx.bot.is_closed():

            def check(m):
                if m.user.id == ctx.author.id and m.channel.id == ctx.channel.id:
                    return True
                return False

            try:
                inter = await self.bot.wait_for('interaction', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
                await msg.delete()
                break

            if player.battle and ctx.author.id not in self.bot.dg_battle and ctx.author.id not in self.bot.batalhando:

                await inter.response.defer()
                item = await ctx.send("<:alert:739251822920728708>│`Você precisa batalhar para se mover!`")
                await sleep(2)
                await item.delete()

                msg = copy.copy(ctx.message)
                msg.content = "ash battle"
                _ctx = await self.bot.get_context(msg)
                await self.bot.invoke(_ctx)
                self.bot.dg_battle.append(ctx.author.id)
                self.bot.dg_battle_now.append(ctx.author.id)
                self.bot.batalhando.append(ctx.author.id)

            elif player.battle and ctx.author.id in self.bot.dg_battle_loser and\
                    ctx.author.id not in self.bot.batalhando:

                await inter.response.defer()
                item = await ctx.send("<:alert:739251822920728708>│`Como voce perdeu vai precisar batalhar novamente!`")
                await sleep(2)
                await item.delete()

                msg = copy.copy(ctx.message)
                msg.content = "ash battle"
                _ctx = await self.bot.get_context(msg)
                await self.bot.invoke(_ctx)
                self.bot.dg_battle.append(ctx.author.id)
                self.bot.dg_battle_now.append(ctx.author.id)
                self.bot.batalhando.append(ctx.author.id)
                self.bot.dg_battle_loser.remove(ctx.author.id)

            elif player.battle and ctx.author.id not in self.bot.dg_battle and ctx.author.id in self.bot.dg_battle_now:
                player.battle = False
                self.bot.dg_battle_now.remove(ctx.author.id)

            elif player.battle and ctx.author.id in self.bot.dg_battle and ctx.author.id in self.bot.batalhando:

                await inter.response.defer()
                item = await ctx.send("<:alert:739251822920728708>│`Termine sua batalha primeiro, para se mover!`")
                await sleep(2)
                await item.delete()

            if str(inter.component.emoji) == _emoji and not player.battle:
                await inter.response.defer()

                if int(player.matriz[player.y][player.x]) in [1, 2, 5]:  # caminho

                    pos, num = (player.x, player.y), int(player.matriz[player.y][player.x])
                    if pos not in player.locs:
                        player.locs.append(pos)

                        item = await ctx.send("<a:loading:520418506567843860>│`Procurando alguma coisa...`")
                        await sleep(2)
                        await item.delete()

                        find = True if randint(1, 100) <= 25 else True if num == 5 else False
                        text = "VOCE ENCONTROU ALGO!" if find else "NÃO FOI ENCONTRADO NADA NESSE CHUNCK!"
                        emoji = ["<:confirmed:721581574461587496>", "<:negate:721581573396496464>"]
                        item = await ctx.send(f"{emoji[0] if find else emoji[1]}│`{text}`")
                        await sleep(2)
                        await item.delete()

                    else:

                        item = await ctx.send("<:alert:739251822920728708>│`Você ja procurou algo nessa chunck!`")
                        await sleep(2)
                        await item.delete()

                if int(player.matriz[player.y][player.x]) == 3:  # objetivo
                    item = await ctx.send('<a:fofo:524950742487007233>│`PARABENS VOCÊ FINALIZOU O ANDAR DA DUNGEON:`\n'
                                          '✨ **[Tower of Alasthor]** ✨')
                    await sleep(2)
                    await item.delete()

            if str(inter.component.emoji) == "⬆️" and not player.battle:
                moviment = player.move('up')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            elif str(inter.component.emoji) == "⬇️" and not player.battle:
                moviment = player.move('down')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            elif str(inter.component.emoji) == "⬅️" and not player.battle:
                moviment = player.move('left')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            elif str(inter.component.emoji) == "➡️" and not player.battle:
                moviment = player.move('right')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

        if ctx.author.id in self.bot.explorando:
            self.bot.explorando.remove(ctx.author.id)


def setup(bot):
    bot.add_cog(DugeonClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mDUNGEONCLASS\033[1;32m foi carregado com sucesso!\33[m')
