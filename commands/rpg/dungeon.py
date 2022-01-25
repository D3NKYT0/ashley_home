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
        self.dgp = self.bot.config['attribute']['dungeons_pyramid']
        self.dgtl = self.bot.config['attribute']['list_tower']
        self.dgpl = self.bot.config['attribute']['list_pyramid']
        self.reward_tc = self.bot.config['attribute']['reward_tower_comum']
        self.reward_te = self.bot.config['attribute']['reward_tower_especial']
        self.reward_ce = self.bot.config['attribute']['reward_chunck_especial']

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
                                  f"{self.st[117]} `dg pyramid` [Pyramid of Aka'Du]")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @dungeon.group(name="tower", aliases=['tw'])
    async def _tower(self, ctx, action=None):

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "tower" not in update['dungeons'].keys():
            tower = {
                "active": True,
                "position_now": [-1, -1],
                "floor": 0,
                "battle": 0,
                "special_chunks": 10,
                "map": False,
                "miniboss": False,
                "miniboss_final": False,
                "locs": list()
            }
            update['dungeons']["tower"] = tower
            msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a dungeon` **[Tower of Alasthor]** ' \
                  '`foi ativada na sua conta com sucesso!`\n**Obs:** `use o comando novamente pra iniciar!`'
            await self.bot.db.update_data(data, update, 'users')
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if not update['dungeons']['tower']['active']:
            msg = "<:negate:721581573396496464>│`VOCÊ JA FINALIZOU ESSA DUNGEON`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if action is not None:

            if action == "map" and update["dungeons"]['tower']["map"]:
                map_name = self.bot.config['attribute']['list_tower'][update["dungeons"]['tower']["floor"]]
                msg = f"`MAPA DA DUNGEON` **Tower of Alasthor** ✨ **ANDAR: {map_name.upper()}!** ✨"
                file = disnake.File(f"dungeon/maps/{map_name}.png", filename="map.gif")
                embed = disnake.Embed(title=msg, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_image(url="attachment://map.gif")
                await ctx.send(file=file, embed=embed)

            elif action == "map" and not update["dungeons"]['tower']["map"]:
                msg = '<:negate:721581573396496464>│`Você nao tem o mapa desse andar da dungeon` ' \
                      '**[Tower of Alasthor]**\n**Obs:** `use o comando (ash bt tw) para tentar conseguir o mapa!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            elif action in ["reset", "r"]:

                update['dungeons']["tower"]["position_now"] = [-1, -1]
                await self.bot.db.update_data(data, update, 'users')
                msg = '<:confirmed:721581574461587496>│`a dungeon` **[Tower of Alasthor]** ' \
                      '`resetou sua localização!`\n**Obs:** `use o comando (ash dg tw) novamente pra iniciar!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            else:
                msg = '<:negate:721581573396496464>│`ESSA AÇÃO NAO EXISTE!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        if update['dungeons']['tower']['floor'] > 0:

            if update['dungeons']['tower']['position_now'] == [-1, -1]:
                if update['dungeons']['tower']['battle'] > 0:
                    _bt = update['dungeons']['tower']['battle']
                    msg = f'<:negate:721581573396496464>│`VOCE PRECISA BATALHAR {_bt}x ANTES DE PROSSEGUIR NA ' \
                          f'DUNGEON!`\n**Obs:** `use o comando` **ASH BT TOWER** `para batalhar`'
                    embed = disnake.Embed(color=self.bot.color, description=msg)
                    return await ctx.send(embed=embed)

            if not update['dungeons']['tower']['miniboss']:
                msg = '<:negate:721581573396496464>│`VOCE PRECISA BATALHAR COM UM MINIBOSS ANTES DE PROSSEGUIR NA' \
                      ' DUNGEON!`\n**Obs:** `use o comando` **ASH BT MOON TW** `para batalhar com um miniboss`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        self.bot.explorando.append(ctx.author.id)

        mapper, map_name = Map(self.dgt), self.dgtl[update['dungeons']['tower']['floor']]
        map_now = mapper.get_map(img_map=map_name)
        matriz, pos = mapper.get_matrix(map_now, self.dgt[map_name])
        x, y = pos[1][1], pos[1][0]

        position_now = update['dungeons']['tower']['position_now']
        if position_now[0] == -1 and position_now[1] == -1:
            update['dungeons']['tower']['position_now'] = [x, y]
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
        move.add_item(disnake.ui.Button(emoji="❌", style=disnake.ButtonStyle.red))
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

        player = Player(ctx, map_now, matriz, [x, y], "tower", self.dgt)

        while not ctx.bot.is_closed():
        
            try:
                if int(player.matriz[player.y][player.x]) == 1:
                    pass
            except IndexError:
                x, y = player.x, player.y
                player.x =  y
                player.y = x

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

            try:
                await inter.response.defer()  # respondendo a interação
            except disnake.errors.NotFound:
                pass

            if player.battle:

                cl = await self.bot.db.cd("users")
                dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1})
                pos = [player.x, player.y]
                if pos not in dg_data["dungeons"]["tower"]["locs"]:
                    dg_data["dungeons"]["tower"]["locs"].append(pos)
                    await cl.update_one({"user_id": ctx.author.id}, {"$set": dg_data})

                await ctx.send("<:alert:739251822920728708>│`Você acumulou uma batalha!`", delete_after=5.0)

                player.battle = False

            if str(inter.component.emoji) == "❌" and not player.battle:
                await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
                await msg.delete()
                break

            if str(inter.component.emoji) == _emoji:

                if int(player.matriz[player.y][player.x]) in [1, 2, 4, 5]:  # caminho
                    cl = await self.bot.db.cd("users")
                    dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1, "inventory": 1})

                    pos, num = [player.x, player.y], int(player.matriz[player.y][player.x])
                    if pos not in dg_data["dungeons"]["tower"]["locs"]:
                        dg_data["dungeons"]["tower"]["locs"].append(pos)

                        await sleep(1)

                        find = True if randint(1, 100) <= 15 else True if num == 5 else False
                        text = "VOCE ENCONTROU ALGO!" if find else "NÃO FOI ENCONTRADO NADA NESSE CHUNCK!"
                        emoji = ["<:confirmed:721581574461587496>", "<:negate:721581573396496464>"]
                        _msg = f"{emoji[0] if find else emoji[1]}│`{text}`"
                        await ctx.send(_msg, delete_after=2.0)

                        if find:
                            it, qt = choice(self.reward_tc), randint(1, 2)
                            if num == 5:
                                it, qt = choice(self.reward_te), 1

                            chunck_special = ""
                            if randint(1, 100) <= 20 and dg_data["dungeons"]["tower"]["special_chunks"] > 0:
                                dg_data["dungeons"]["tower"]["special_chunks"] -= 1
                                it, qt, chunck_special = choice(self.reward_ce), 1, "`CHUNCK ESPECIAL`"

                            if it in dg_data["inventory"].keys():
                                dg_data["inventory"][it] += qt
                            else:
                                dg_data["inventory"][it] = qt
                            await ctx.send(f"{emo}│{self.i[it][0]} `{qt}` **{self.i[it][1]}** {chunck_special}")

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": dg_data})

                    else:

                        if int(player.matriz[player.y][player.x]) == 4:
                            _msg = "<:negate:721581573396496464>│`Você não pode dar loot numa chunck de batalha!`"
                            await ctx.send(_msg, delete_after=2.0)

                        else:
                            _msg = "<:alert:739251822920728708>│`Você ja procurou algo nessa chunck!`"
                            await ctx.send(_msg, delete_after=2.0)

                if int(player.matriz[player.y][player.x]) == 3:  # objetivo

                    cl = await self.bot.db.cd("users")
                    dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1, "inventory": 1})

                    if dg_data['dungeons']['tower']['floor'] == 10:

                        if dg_data['dungeons']['tower']['battle'] > 0:
                            _bt = dg_data['dungeons']['tower']['battle']
                            msg = f'<:negate:721581573396496464>│`VOCE PRECISA BATALHAR {_bt}x ANTES DE PROSSEGUIR' \
                                  f' NA DUNGEON!`\n' \
                                  f'**Obs:** `use o comando` **ASH BT TOWER** `para batalhar`'
                            embed = disnake.Embed(color=self.bot.color, description=msg)
                            await ctx.send(embed=embed)
                            break

                        if not dg_data['dungeons']['tower']['miniboss_final']:
                            msg = '<:negate:721581573396496464>│`VOCE PRECISA BATALHAR COM UM MINIBOSS ANTES' \
                                  ' DE PROSSEGUIR NA DUNGEON!`\n' \
                                  '**Obs:** `use o comando` **ASH BT MOON TW** `para batalhar com um miniboss`'
                            embed = disnake.Embed(color=self.bot.color, description=msg)
                            await ctx.send(embed=embed)
                            break

                        _msg = "<a:fofo:524950742487007233>│`PARABENS VOCÊ FINALIZOU TODA A DUNGEON:`\n" \
                               "✨ **[Tower of Alasthor]** ✨\n" \
                               "**Obs:** `Você ganhou por completar toda a DUNGEON uma` **Key of Hell**"
                        await ctx.send(_msg)

                        query = {
                            "dungeons.tower": {
                                "active": False,
                                "position_now": [-1, -1],
                                "floor": 0,
                                "battle": 0,
                                "special_chunks": 10,
                                "map": False,
                                "miniboss": False,
                                "miniboss_final": False,
                                "locs": list()
                            }}

                        inventory = {
                            "inventory.key_of_hell": 1
                        }

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": query, "$inc": inventory})

                    else:

                        _msg = "<a:fofo:524950742487007233>│`PARABENS VOCÊ FINALIZOU O ANDAR DA DUNGEON:`\n" \
                               "✨ **[Tower of Alasthor]** ✨\n" \
                               "**Obs:** `use o comando de novo para explorar o novo andar!`"
                        await ctx.send(_msg)

                        query = {
                            "dungeons.tower": {
                                "active": True,
                                "position_now": [-1, -1],
                                "floor": dg_data["dungeons"]["tower"]["floor"] + 1,
                                "battle": dg_data["dungeons"]["tower"]["battle"],
                                "special_chunks": 10,
                                "map": False,
                                "miniboss": False,
                                "miniboss_final": False,
                                "locs": list()
                            }}

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": query})

                    await msg.delete()
                    break

            if str(inter.component.emoji) == "⬆️":

                moviment = await player.move('up')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

            elif str(inter.component.emoji) == "⬇️":

                moviment = await player.move('down')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

            elif str(inter.component.emoji) == "⬅️":

                moviment = await player.move('left')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

            elif str(inter.component.emoji) == "➡️":

                moviment = await player.move('right')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

        if ctx.author.id in self.bot.explorando:
            self.bot.explorando.remove(ctx.author.id)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @dungeon.group(name="pyramid", aliases=['pm'])
    async def _pyramid(self, ctx, action=None):

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE JÁ ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "pyramid" not in update['dungeons'].keys():
            pyramid = {
                "active": True,
                "position_now": [-1, -1],
                "floor": 0,
                "battle": 0,
                "special_chunks": 10,
                "map": False,
                "miniboss": False,
                "miniboss_final": False,
                "locs": list()
            }
            update['dungeons']["pyramid"] = pyramid
            msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a dungeon` **[Pyramid of Aka\'Du]** ' \
                  '`foi ativada na sua conta com sucesso!`\n**Obs:** `use o comando novamente pra iniciar!`'
            await self.bot.db.update_data(data, update, 'users')
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if not update['dungeons']['pyramid']['active']:
            pyramid = {
                "active": True,
                "position_now": [-1, -1],
                "floor": 0,
                "battle": 0,
                "special_chunks": 10,
                "map": False,
                "miniboss": False,
                "miniboss_final": False,
                "locs": list()
            }
            update['dungeons']["pyramid"] = pyramid
            msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a dungeon` **[Pyramid of Aka\'Du]** ' \
                  '`foi resetada na sua conta com sucesso!`\n**Obs:** `use o comando novamente pra iniciar!`'
            await self.bot.db.update_data(data, update, 'users')
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if action is not None:

            if action == "map" and update["dungeons"]['pyramid']["map"]:
                map_name = self.bot.config['attribute']['list_pyramid'][update["dungeons"]['pyramid']["floor"]]
                msg = f"`MAPA DA DUNGEON` **Pyramid of Aka'Du** ✨ **ANDAR: {map_name.upper()}!** ✨"
                file = disnake.File(f"dungeon/maps/{map_name}.png", filename="map.gif")
                embed = disnake.Embed(title=msg, color=self.bot.color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
                embed.set_image(url="attachment://map.gif")
                await ctx.send(file=file, embed=embed)

            elif action == "map" and not update["dungeons"]['pyramid']["map"]:
                msg = '<:negate:721581573396496464>│`Você nao tem o mapa desse andar da dungeon` ' \
                      '**[Pyramid of Aka\'Du]**\n**Obs:** `use o comando (ash bt py) para tentar conseguir o mapa!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            elif action in ["reset", "r"]:

                update['dungeons']["pyramid"]["position_now"] = [-1, -1]
                await self.bot.db.update_data(data, update, 'users')
                msg = '<:confirmed:721581574461587496>│`a dungeon` **[Pyramid of Aka\'Du]** ' \
                      '`resetou sua localização!`\n**Obs:** `use o comando (ash dg tw) novamente pra iniciar!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            else:
                msg = '<:negate:721581573396496464>│`ESSA AÇÃO NAO EXISTE!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        if update['dungeons']['pyramid']['floor'] > 0:

            if update['dungeons']['pyramid']['position_now'] == [-1, -1]:
                if update['dungeons']['pyramid']['battle'] > 0:
                    _bt = update['dungeons']['pyramid']['battle']
                    msg = f'<:negate:721581573396496464>│`VOCE PRECISA BATALHAR {_bt}x ANTES DE PROSSEGUIR NA ' \
                          f'DUNGEON!`\n**Obs:** `use o comando` **ASH BT PYRAMID** `para batalhar`'
                    embed = disnake.Embed(color=self.bot.color, description=msg)
                    return await ctx.send(embed=embed)

            if not update['dungeons']['pyramid']['miniboss']:
                msg = '<:negate:721581573396496464>│`VOCE PRECISA BATALHAR COM UM MINIBOSS ANTES DE PROSSEGUIR NA' \
                      ' DUNGEON!`\n**Obs:** `use o comando` **ASH BT MOON PM** `para batalhar com um miniboss`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

        self.bot.explorando.append(ctx.author.id)

        mapper, map_name = Map(self.dgp), self.dgpl[update['dungeons']['pyramid']['floor']]
        map_now = mapper.get_map(img_map=map_name)
        matriz, pos = mapper.get_matrix(map_now, self.dgp[map_name])
        x, y = pos[1][1], pos[1][0]

        position_now = update['dungeons']['pyramid']['position_now']
        if position_now[0] == -1 and position_now[1] == -1:
            update['dungeons']['pyramid']['position_now'] = [x, y]
            await self.bot.db.update_data(data, update, 'users')
        else:
            x, y = update['dungeons']['pyramid']['position_now'][0], update['dungeons']['pyramid']['position_now'][1]

        vision = mapper.get_vision(map_now, [x, y])
        _map = mapper.create_map(vision, "vision_map")
        _emoji, emo = "<:picket:928779628041080853>", "<:confirmed:721581574461587496>"
        _style = [disnake.ButtonStyle.gray, disnake.ButtonStyle.primary, disnake.ButtonStyle.green]

        move = MovePlayer(ctx.author)
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(emoji="⬆️", style=_style[1]))
        move.add_item(disnake.ui.Button(label="‏", style=_style[0], disabled=True))
        move.add_item(disnake.ui.Button(emoji="❌", style=disnake.ButtonStyle.red))
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

        player = Player(ctx, map_now, matriz, [x, y], "pyramid", self.dgp)

        while not ctx.bot.is_closed():
        
            try:
                if int(player.matriz[player.y][player.x]) == 1:
                    pass
            except IndexError:
                x, y = player.x, player.y
                player.x =  y
                player.y = x

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

            try:
                await inter.response.defer()  # respondendo a interação
            except disnake.errors.NotFound:
                pass

            if player.battle:

                cl = await self.bot.db.cd("users")
                dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1})
                pos = [player.x, player.y]
                if pos not in dg_data["dungeons"]["pyramid"]["locs"]:
                    dg_data["dungeons"]["pyramid"]["locs"].append(pos)
                    await cl.update_one({"user_id": ctx.author.id}, {"$set": dg_data})

                await ctx.send("<:alert:739251822920728708>│`Você acumulou uma batalha!`", delete_after=5.0)

                player.battle = False

            if str(inter.component.emoji) == "❌" and not player.battle:
                await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
                await msg.delete()
                break

            if str(inter.component.emoji) == _emoji:
                if int(player.matriz[player.y][player.x]) in [1, 2, 4, 5]:  # caminho
                    cl = await self.bot.db.cd("users")
                    dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1, "inventory": 1})

                    pos, num = [player.x, player.y], int(player.matriz[player.y][player.x])
                    if pos not in dg_data["dungeons"]["pyramid"]["locs"]:
                        dg_data["dungeons"]["pyramid"]["locs"].append(pos)

                        await sleep(1)

                        find = True if randint(1, 100) <= 15 else True if num == 5 else False
                        text = "VOCE ENCONTROU ALGO!" if find else "NÃO FOI ENCONTRADO NADA NESSE CHUNCK!"
                        emoji = ["<:confirmed:721581574461587496>", "<:negate:721581573396496464>"]
                        _msg = f"{emoji[0] if find else emoji[1]}│`{text}`"
                        await ctx.send(_msg, delete_after=2.0)

                        if find:
                            it, qt = choice(self.reward_tc), randint(1, 2)
                            if num == 5:
                                it, qt = choice(self.reward_te), 1

                            chunck_special = ""
                            if randint(1, 100) <= 20 and dg_data["dungeons"]["pyramid"]["special_chunks"] > 0:
                                dg_data["dungeons"]["pyramid"]["special_chunks"] -= 1
                                it, qt, chunck_special = choice(self.reward_ce), 1, "`CHUNCK ESPECIAL`"

                            if it in dg_data["inventory"].keys():
                                dg_data["inventory"][it] += qt
                            else:
                                dg_data["inventory"][it] = qt
                            await ctx.send(f"{emo}│{self.i[it][0]} `{qt}` **{self.i[it][1]}** {chunck_special}")

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": dg_data})

                    else:

                        if int(player.matriz[player.y][player.x]) == 4:
                            _msg = "<:negate:721581573396496464>│`Você não pode dar loot numa chunck de batalha!`"
                            await ctx.send(_msg, delete_after=2.0)

                        else:
                            _msg = "<:alert:739251822920728708>│`Você ja procurou algo nessa chunck!`"
                            await ctx.send(_msg, delete_after=2.0)

                if int(player.matriz[player.y][player.x]) == 3:  # objetivo

                    cl = await self.bot.db.cd("users")
                    dg_data = await cl.find_one({"user_id": ctx.author.id}, {"dungeons": 1, "inventory": 1})

                    if dg_data['dungeons']['pyramid']['floor'] == 4:

                        if dg_data['dungeons']['pyramid']['battle'] > 0:
                            _bt = dg_data['dungeons']['pyramid']['battle']
                            msg = f'<:negate:721581573396496464>│`VOCE PRECISA BATALHAR {_bt}x ANTES DE PROSSEGUIR' \
                                  f' NA DUNGEON!`\n' \
                                  f'**Obs:** `use o comando` **ASH BT PYRAMID** `para batalhar`'
                            embed = disnake.Embed(color=self.bot.color, description=msg)
                            await ctx.send(embed=embed)
                            break

                        if not dg_data['dungeons']['pyramid']['miniboss_final']:
                            msg = '<:negate:721581573396496464>│`VOCE PRECISA BATALHAR COM UM MINIBOSS ANTES' \
                                  ' DE PROSSEGUIR NA DUNGEON!`\n' \
                                  '**Obs:** `use o comando` **ASH BT MOON PM** `para batalhar com um miniboss`'
                            embed = disnake.Embed(color=self.bot.color, description=msg)
                            await ctx.send(embed=embed)
                            break

                        _msg = "<a:fofo:524950742487007233>│`PARABENS VOCÊ FINALIZOU TODA A DUNGEON:`\n" \
                               "✨ **[Pyramid of Aka'Du]** ✨\n" \
                               "**Obs:** `Você ganhou por completar toda a DUNGEON uma` **Blessed Armor Divine**"
                        await ctx.send(_msg)

                        query = {
                            "dungeons.pyramid": {
                                "active": False,
                                "position_now": [-1, -1],
                                "floor": 0,
                                "battle": 0,
                                "special_chunks": 10,
                                "map": False,
                                "miniboss": False,
                                "miniboss_final": False,
                                "locs": list()
                            }}

                        inventory = {
                            "inventory.blessed_armor_divine": 1
                        }

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": query, "$inc": inventory})

                    else:

                        _msg = "<a:fofo:524950742487007233>│`PARABENS VOCÊ FINALIZOU O ANDAR DA DUNGEON:`\n" \
                               "✨ **[Pyramid of Aka'Du]** ✨\n" \
                               "**Obs:** `use o comando de novo para explorar o novo andar!`"
                        await ctx.send(_msg)

                        query = {
                            "dungeons.pyramid": {
                                "active": True,
                                "position_now": [-1, -1],
                                "floor": dg_data["dungeons"]["pyramid"]["floor"] + 1,
                                "battle": dg_data["dungeons"]["pyramid"]["battle"],
                                "special_chunks": 10,
                                "map": False,
                                "miniboss": False,
                                "miniboss_final": False,
                                "locs": list()
                            }}

                        await cl.update_one({"user_id": ctx.author.id}, {"$set": query})

                    await msg.delete()
                    break

            if str(inter.component.emoji) == "⬆️":

                moviment = await player.move('up')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

            elif str(inter.component.emoji) == "⬇️":

                moviment = await player.move('down')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

            elif str(inter.component.emoji) == "⬅️":

                moviment = await player.move('left')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

            elif str(inter.component.emoji) == "➡️":

                moviment = await player.move('right')
                if isinstance(moviment, disnake.File):
                    embed = disnake.Embed(color=self.bot.color)
                    embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
                    embed.set_image(file=moviment)
                    msg = await msg.edit(embed=embed, view=move)
                else:
                    await ctx.send("<:alert:739251822920728708>│`Tente outra direção`", delete_after=5.0)

        if ctx.author.id in self.bot.explorando:
            self.bot.explorando.remove(ctx.author.id)


def setup(bot):
    bot.add_cog(DugeonClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mDUNGEONCLASS\033[1;32m foi carregado com sucesso!\33[m')
