import copy
import disnake

from io import BytesIO
from disnake.ext import commands
from resources.db import Database
from random import randint, choice
from resources.check import check_it
from asyncio import sleep, TimeoutError
from disnake.ext.commands.core import is_owner
from dungeon.maps import Map, MovePlayer, Player


class DugeonClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color
        self.i = self.bot.items
        self.dgt = self.bot.config['attribute']['dungeons_tower']
        self.dgtl = self.bot.config['attribute']['list_tower']
        self.reward_tc = self.bot.config['attribute']['reward_tower_comum']
        self.reward_te = self.bot.config['attribute']['reward_tower_especial']

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
            embed.add_field(name="Dungeons Commands: [BETA TESTE]",
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

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @dungeon.group(name="tower", aliases=['tw'])
    async def _tower(self, ctx, reset=None):

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "tower" not in update['dungeons'].keys():
            tower = {
                "active": True,
                "position_now": (-1, -1),
                "floor": 0,
                "block_battle": False,
                "locs": list()
            }
            update['dungeons']["tower"] = tower
            msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a dungeon` **[Tower of Alasthor]** ' \
                  '`foi ativada na sua conta com sucesso!`\n**Obs:** `use o comando novamente pra iniciar!`'
            await self.bot.db.update_data(data, update, 'users')
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.explorando:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ NUMA DUNGEON!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if reset is not None:
            update['dungeons']["tower"]["position_now"] = (-1, -1)
            await self.bot.db.update_data(data, update, 'users')
            msg = '<:confirmed:721581574461587496>│`a dungeon` **[Tower of Alasthor]** ' \
                  '`foi resetada sua localização!`\n**Obs:** `use o comando novamente pra iniciar!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        self.bot.explorando.append(ctx.author.id)

        mapper, map_name = Map(), self.dgtl[update['dungeons']['tower']['floor']]
        map_now = mapper.get_map(img_map=map_name)
        matriz, pos = mapper.get_matrix(map_now, self.dgt[map_name])
        x, y = pos[1][1], pos[1][0]

        position_now = update['dungeons']['tower']['position_now']
        if position_now[0] == -1 and position_now[1] == -1:
            update['dungeons']['tower']['position_now'] = (x, y)
            await self.bot.db.update_data(data, update, 'users')
        else:
            x, y = update['dungeons']['tower']['position_now'][0], update['dungeons']['tower']['position_now'][1]

        vision = mapper.get_vision(map_now, [x, y])
        _map = mapper.create_map(vision, "vision_map")
        _emoji, emo = "<:picket:928779628041080853>", "<:confirmed:721581574461587496>"
        _style = [disnake.ButtonStyle.gray, disnake.ButtonStyle.primary, disnake.ButtonStyle.green]

        move = MovePlayer(ctx.author)
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(emoji="⬆️", style=_style[1]))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(label="❌", style=disnake.ButtonStyle.red))
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

        player = Player(ctx, map_now, matriz, [x, y], "tower")
        player.battle = data["dungeons"]["tower"]["block_battle"]

        while not ctx.bot.is_closed():

            loop = False

            def check(m):
                if m.user.id == ctx.author.id and m.channel.id == ctx.channel.id and m.message.id == msg.id:
                    return True
                return False

            try:
                inter = await self.bot.wait_for('interaction', timeout=30.0, check=check)
            except TimeoutError:
                await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
                await msg.delete()
                break

            if player.battle:

                cl = await self.bot.db.cd("users")
                dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1})
                pos = [player.x, player.y]
                if pos not in dg_data["dungeons"]["tower"]["locs"]:
                    dg_data["dungeons"]["tower"]["locs"].append(pos)
                    await cl.update_one({"user_id": ctx.author.id}, {"$set": dg_data})

                _msg = "<:alert:739251822920728708>│`Você ganhou uma batalha especial!`\n" \
                       "**Obs:** `use o comando` **ASH BT TOWER**"
                await ctx.send(_msg, delete_after=5.0)

                player.battle = False

            if str(inter.component.emoji) == "❌":
                await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
                await msg.delete()
                break

            if str(inter.component.emoji) == _emoji:
                loop = True

                if int(player.matriz[player.y][player.x]) in [1, 2, 4, 5]:  # caminho
                    cl = await self.bot.db.cd("users")
                    dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1, "inventory": 1})

                    pos, num = [player.x, player.y], int(player.matriz[player.y][player.x])
                    if pos not in dg_data["dungeons"]["tower"]["locs"]:
                        dg_data["dungeons"]["tower"]["locs"].append(pos)

                        _msg = "<a:loading:520418506567843860>│`Procurando alguma coisa...`"
                        await inter.response.send_message(_msg, delete_after=2.0)

                        await sleep(2)

                        find = True if randint(1, 100) <= 20 else True if num == 5 else False
                        text = "VOCE ENCONTROU ALGO!" if find else "NÃO FOI ENCONTRADO NADA NESSE CHUNCK!"
                        emoji = ["<:confirmed:721581574461587496>", "<:negate:721581573396496464>"]
                        await ctx.send(f"{emoji[0] if find else emoji[1]}│`{text}`", delete_after=2.0)

                        if find:
                            it, qt = choice(self.reward_tc), randint(1, 3)
                            if num == 5:
                                it = choice(self.reward_te)
                            if it in dg_data["inventory"].keys():
                                dg_data["inventory"][it] += qt
                            else:
                                dg_data["inventory"][it] = qt
                            await ctx.send(f"{emo}│{self.i[it][0]} `{qt}` **{self.i[it][1]}**")

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": dg_data})

                    else:

                        _msg = "<:alert:739251822920728708>│`Você ja procurou algo nessa chunck!`"
                        await inter.response.send_message(_msg, delete_after=2.0)

                if int(player.matriz[player.y][player.x]) == 3:  # objetivo

                    cl = await self.bot.db.cd("users")
                    dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1})
                    query = {
                        "dungeons.tower": {
                            "active": True,
                            "position_now": (-1, -1),
                            "floor": dg_data["dungeons"]["tower"]["floor"] + 1,
                            "block_battle": False,
                            "locs": list()
                        }
                    }
                    await cl.update_one({"user_id": ctx.author.id}, {"$set": query})

                    _msg = "<a:fofo:524950742487007233>│`PARABENS VOCÊ FINALIZOU O ANDAR DA DUNGEON:`\n" \
                           "✨ **[Tower of Alasthor]** ✨\n**Obs:** `use o comando de novo para explorar o novo andar!`"
                    await inter.response.send_message(_msg)

            if str(inter.component.emoji) == "⬆️":
                loop = True

                moviment = await player.move('up')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            elif str(inter.component.emoji) == "⬇️":
                loop = True

                moviment = await player.move('down')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            elif str(inter.component.emoji) == "⬅️":
                loop = True

                moviment = await player.move('left')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            elif str(inter.component.emoji) == "➡️":
                loop = True

                moviment = await player.move('right')
                if isinstance(moviment, disnake.File):
                    await msg.delete()
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await ctx.send(embed=embed, view=move)
                else:
                    await inter.response.defer()

            await sleep(1)

            if not loop:
                break

        if ctx.author.id in self.bot.explorando:
            self.bot.explorando.remove(ctx.author.id)


def setup(bot):
    bot.add_cog(DugeonClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mDUNGEONCLASS\033[1;32m foi carregado com sucesso!\33[m')
