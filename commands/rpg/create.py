import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice
from asyncio import sleep, TimeoutError


git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class CreateClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.i = self.bot.items
        self.w_s = self.bot.config['attribute']['chance_enchant']
        self.cost = {
            "stone_of_crystal_wind": 1,
            "stone_of_crystal_water": 1,
            "stone_of_crystal_fire": 1,
            "frozen_letter": 1
        }
        self.cost_armor = {
            "stone_of_crystal_wind": 1,
            "stone_of_crystal_water": 1,
            "stone_of_crystal_fire": 1,
            "frozen_letter": 5,
            "lost_parchment": 10,
            "royal_parchment": 10,
            "sages_scroll": 10
        }
        self.cost_enchant = {
            "stone_of_crystal_wind": 1,
            "stone_of_crystal_water": 1,
            "stone_of_crystal_fire": 1,
            "frozen_letter": 5,
            "essence_cover": 10,
            "essence_leather": 10,
            "essence_platinum": 10
        }

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='create', aliases=['criar'])
    async def create(self, ctx, type_enchant=None):
        """Comando especial usado para craftar joias para seu personagem"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        # filtrando qualquer nome diferente
        type_enchant = None if type_enchant != "enchant" and type_enchant != "armor" else type_enchant

        if type_enchant == "enchant":
            _COST = self.cost_enchant
        elif type_enchant == "armor":
            _COST = self.cost_armor
        else:
            _COST = self.cost

        msg = f"\n".join([f"{self.i[k][0]} `{v}` `{self.i[k][1]}`" for k, v in _COST.items()])
        msg += "\n\n**OBS:** `PARA CONSEGUIR OS ITENS VOCE DEVE USAR OS COMANDOS` **ASH RECIPE** `E` **ASH CRAFT**"

        embed = discord.Embed(
            title="O CUSTO PARA VOCE CRIAR UM ENCANTAMENTO:",
            color=self.bot.color,
            description=msg)
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url="{}".format(ctx.author.avatar_url))
        embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        await ctx.send(embed=embed)

        cost = {}
        for i_, amount in _COST.items():
            if i_ in data['inventory']:
                if data['inventory'][i_] < _COST[i_]:
                    cost[i_] = _COST[i_]
            else:
                cost[i_] = _COST[i_]

        if len(cost) > 0:
            msg = f"\n".join([f"{self.i[key][0]} **{key.upper()}**" for key in cost.keys()])
            return await ctx.send(f"<:alert:739251822920728708>│`Lhe faltam esses itens para criar um encantamento:`"
                                  f"\n{msg}\n`OLHE SEU INVENTARIO E VEJA A QUANTIDADE QUE ESTÁ FALTANDO.`")

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        msg = await ctx.send(f"<:alert:739251822920728708>│`VOCE JA TEM TODOS OS ITEM NECESSARIOS, DESEJA CRIAR "
                             f"SUA JOIA AGORA?`\n**1** para `SIM` ou **0** para `NÃO`")
        try:
            answer = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
        if answer.content == "0":
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")

        await msg.edit(content=f"<a:loading:520418506567843860>│`removendo os itens de custo da sua conta...`")
        for i_, amount in _COST.items():
            update['inventory'][i_] -= amount
            if update['inventory'][i_] < 1:
                del update['inventory'][i_]

        await msg.edit(content=f"<:confirmed:721581574461587496>│`itens retirados com sucesso...`")
        await sleep(2)

        await msg.edit(content=f"<a:loading:520418506567843860>│`Sorteando qual encantamento vai ser criado...`")
        await sleep(2)

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        list_items = []
        for i_, amount in self.w_s.items():

            if type_enchant == "enchant" and "enchant" in i_:
                list_items += [i_] * amount

            if type_enchant == "armor" and "armor" in i_:
                list_items += [i_] * amount

            if type_enchant is None:
                list_items += [i_] * amount

        enchant = choice(list_items)

        await msg.edit(content=f"<:confirmed:721581574461587496>│`encantamento sorteado com sucesso...`")
        await sleep(2)

        await msg.edit(content=f"<a:loading:520418506567843860>│`Adicionando` {self.i[enchant][0]} "
                               f"**1 {self.i[enchant][1]}** `para sua conta...`")

        try:
            update['inventory'][enchant] += 1
        except KeyError:
            update['inventory'][enchant] = 1

        await sleep(2)
        await msg.edit(content=f"<:confirmed:721581574461587496>│{self.i[enchant][0]} `1` **{self.i[enchant][1]}** "
                               f"`adicionado ao seu inventario de equipamentos com sucesso...`")

        img = choice(git)
        embed = discord.Embed(color=self.bot.color)
        embed.set_image(url=img)
        await ctx.send(embed=embed)

        if "the_ten_provinces" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_ten_provinces"]
            if _QUEST["status"] == "in progress" and update['config']['provinces'] is not None:
                if ctx.channel.id not in update['rpg']['quests']["the_ten_provinces"]["provinces"]:
                    update['rpg']['quests']["the_ten_provinces"]["provinces"].append(ctx.channel.id)
                    await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                   f'✨ **[The 10 - Provinces]** ✨')

        if "the_five_shirts" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_five_shirts"]
            if _QUEST["status"] == "in progress":
                _NEXT, _INV = False, update["inventory"].keys()
                reward = choice(["shirt_of_earth", "shirt_of_fire", "shirt_of_soul",
                                 "shirt_of_water", "shirt_of_wind"])
                if reward in _INV:
                    update["inventory"][reward] -= 1
                    if update["inventory"][reward] < 1:
                        del update["inventory"][reward]
                    _NEXT = True
                if reward not in update['rpg']['quests']["the_five_shirts"]["shirts"] and _NEXT:
                    update['rpg']['quests']["the_five_shirts"]["shirts"].append(reward)
                    await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                   f'✨ **[The 5 Shirts]** ✨')

        await self.bot.db.update_data(data, update, 'users')
        await self.bot.data.add_sts(ctx.author, "create", 1)


def setup(bot):
    bot.add_cog(CreateClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mCREATE\033[1;32m foi carregado com sucesso!\33[m')
