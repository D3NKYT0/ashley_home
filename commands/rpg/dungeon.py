import disnake
import asyncio

from io import BytesIO
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
        move.add_item(disnake.ui.Button(emoji="⬆️", style=_style[1], custom_id="Up"))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(emoji="⬅️", style=_style[1], row=1, custom_id="Left"))
        move.add_item(disnake.ui.Button(emoji=_emoji, style=_style[2], row=1, custom_id="Action"))
        move.add_item(disnake.ui.Button(emoji="➡️", style=d_style[1], row=1))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True, row=3, custom_id="Right"))
        move.add_item(disnake.ui.Button(emoji="⬇️", style=_style[1], row=3, custom_id="Down"))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True, row=3))

        with BytesIO() as file:
            _map.save(file, 'PNG')
            file.seek(0)
            embed = disnake.Embed(title=f"Dungeon: {ctx.author.name}", color=self.bot.color)
            embed.set_image(file=disnake.File(file, 'map.png'))
            msg = await ctx.send(embed=embed, view=Move)

        player = Player(map_now, matriz, [x, y], ctx)

        while not ctx.bot.is_closed():

            def check(m):
                if m.user.id == ctx.author.id and m.channel.id == ctx.channel.id:
                    return True
                return False

            try:
                inter = await self.bot.wait_for('interaction', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Tempo esgotado")
                await msg.delete()
                break

            if str(inter.component.emoji) == "⬆️":
                moviment = player.move('up')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(title=f"Dungeon: {ctx.author.name}", color=self.bot.color)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=Move)
                else:
                    inter.response.is_done()

            elif str(inter.component.emoji) == "⬇️":
                moviment = player.move('down')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(title=f"Dungeon: {ctx.author.name}", color=self.bot.color)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=Move)
                else:
                    inter.response.is_done()

            elif str(inter.component.emoji) == "⬅️":
                moviment = player.move('left')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(title=f"Dungeon: {ctx.author.name}", color=self.bot.color)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=Move)
                else:
                    inter.response.is_done()

            elif str(inter.component.emoji) == "➡️":
                moviment = player.move('right')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(title=f"Dungeon: {ctx.author.name}", color=self.bot.color)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=Move)
                else:
                    inter.response.is_done()


def setup(bot):
    bot.add_cog(DugeonClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mDUNGEONCLASS\033[1;32m foi carregado com sucesso!\33[m')
