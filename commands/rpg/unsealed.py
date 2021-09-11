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


class MeltedClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.i = self.bot.items
        self.se = self.bot.config['equips']

        self.rarity = {
            "uncommon": 100,
            "rare": 50,
            "super rare": 30,
            "ultra rare": 19,
            "secret": 1
        }

        self.cost = {
            "melted_artifact": 1,
            "unsealed_stone": 2,
            "Discharge_Crystal": 10,
            "Acquittal_Crystal": 10,
            "Crystal_of_Energy": 10
        }

        self.cost_celestial = {
            "Discharge_Crystal": 125,
            "Acquittal_Crystal": 125,
            "Crystal_of_Energy": 125,

            "melted_artifact": 10,
            "unsealed_stone": 50,

            "golden_egg": 19,
            "golden_apple": 14,
            "gold_cube": 2,

            "seed": 25,
            "ore_bar": 25,
            "debris": 25,
            "coal": 25,
            "claw": 25,
            "charcoal": 25,
            "branch": 25,
            "braided_hemp": 25,

            "feather_white": 35,
            "feather_gold": 35,
            "feather_black": 35,

            "herb_red": 35,
            "herb_green": 35,
            "herb_blue": 35
        }

        self.celestial = {
            "celestial necklace sealed": "116",
            "celestial earring sealed": "117",
            "celestial ring sealed": "118"
        }

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='unsealed', aliases=['liberar', 'libertar'])
    async def unsealed(self, ctx, *, equip=None):
        """Comando especial para liberar/remover o selo de uma armadura."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if equip is None:
            return await ctx.send("<:negate:721581573396496464>│`VOCE PRECISA DIZER O NOME DE UM EQUIPAMENTO!`")

        equip = equip.replace("_", " ")
        if equip.lower() not in [k.lower() for k in self.i.keys() if self.i[k][3] == 9]:
            return await ctx.send("<:negate:721581573396496464>│`VOCE PRECISA DIZER UM EQUIPAMENTO VALIDO!`")

        _COST = self.cost if equip not in self.celestial.keys() else self.cost_celestial

        msg = f"\n".join([f"{self.i[k][0]} `{v}` `{self.i[k][1]}`" for k, v in _COST.items()])
        msg += "\n\n**OBS:** `PARA CONSEGUIR OS ITENS VOCE PRECISA USAR OS COMANDOS` " \
               "**ASH MELTED, ASH STONE**  `E` **ASH BOX**"

        embed = discord.Embed(
            title="O CUSTO PARA VOCE TIRAR O SELO DE UM EQUIPAMENTO:",
            color=self.bot.color,
            description=msg)
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url="{}".format(ctx.author.avatar_url))
        embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        await ctx.send(embed=embed)

        if equip not in data['inventory'].keys():
            return await ctx.send("<:negate:721581573396496464>│`Voce não tem esse equipamento no seu invetário...`\n"
                                  "**Obs:** `VOCE CONSEGUE OS EQUIPAMENTOS CRAFTANDO, USANDO O COMANDO` **ASH CRAFT**"
                                  " `E O COMANDO` **ASH RECIPE** `PARA PEGAR AS RECEITAS DOS CRAFTS.`")

        cost = {}
        for i_, amount in _COST.items():
            if i_ in data['inventory']:
                if data['inventory'][i_] < _COST[i_]:
                    cost[i_] = _COST[i_]
            else:
                cost[i_] = _COST[i_]

        if len(cost) > 0:
            msg = f"\n".join([f"{self.i[key][0]} **{key.upper()}**" for key in cost.keys()])
            return await ctx.send(f"<:alert:739251822920728708>│`Lhe faltam esses itens para tirar o selo do item:`"
                                  f"\n{msg}\n`OLHE SEU INVENTARIO E VEJA A QUANTIDADE QUE ESTÁ FALTANDO.`")

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        msg = await ctx.send(f"<:alert:739251822920728708>│`VOCE JA TEM TODOS OS ITEM NECESSARIOS, DESEJA TIRAR O SELO"
                             f" DO SEU EQUIMENTO AGORA?`\n**1** para `SIM` ou **0** para `NÃO`")
        try:
            answer = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
        if answer.content == "0":
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
        await msg.delete()

        msg = await ctx.send("<a:loading:520418506567843860>│`Selecionamento o equipamento para tirar o selo...`")
        await sleep(2)
        await msg.edit(content=f"<a:loading:520418506567843860>│`removendo os itens de custo e o equipamento da sua "
                               f"conta...`")

        await sleep(2)
        await msg.edit(content=f"<a:loading:520418506567843860>│`removendo itens...`")

        for i_, amount in _COST.items():
            update['inventory'][i_] -= amount
            if update['inventory'][i_] < 1:
                del update['inventory'][i_]

        await sleep(2)
        await msg.edit(content=f"<a:loading:520418506567843860>│`removendo equipamento...`")

        update['inventory'][equip] -= 1
        if update['inventory'][equip] < 1:
            del update['inventory'][equip]

        await msg.edit(content=f"<:confirmed:721581574461587496>│`itens retirados com sucesso...`")
        await sleep(2)

        # agora o item vai ser transformado em equipamento...

        await msg.edit(content=f"<a:loading:520418506567843860>│`Tirando o selo da sua armadura...`")

        if equip not in self.celestial.keys():

            list_rarity = []
            for i_, amount in self.rarity.items():
                list_rarity += [i_] * amount
            rarity = choice(list_rarity)

            legend = {
                "uncommon": "silver",
                "rare": "mystic",
                "super rare": "inspiron",
                "ultra rare": "violet",
                "secret": "hero"
            }

            reward_equip = None
            item_reward = equip.lower()
            item_reward = item_reward.replace("sealed", legend[rarity])

            if "leather" in equip:
                for k, v in self.se[f'set dynasty leather {rarity}'].items():
                    if v['name'] == item_reward:
                        reward_equip = (k, v)

            elif "platinum" in equip:
                for k, v in self.se[f'set dynasty platinum {rarity}'].items():
                    if v['name'] == item_reward:
                        reward_equip = (k, v)

            elif "cover" in equip:
                for k, v in self.se[f'set dynasty cover {rarity}'].items():
                    if v['name'] == item_reward:
                        reward_equip = (k, v)

            try:
                update['rpg']['items'][reward_equip[0]] += 1
            except KeyError:
                update['rpg']['items'][reward_equip[0]] = 1

            msg_return = f"<:confirmed:721581574461587496>│{reward_equip[1]['icon']} `1` " \
                         f"**{reward_equip[1]['name']}** `adicionado ao seu inventario com sucesso...`"

            reward_equip = reward_equip[1]

        else:

            try:
                update['rpg']['items'][self.celestial[equip]] += 1
            except KeyError:
                update['rpg']['items'][self.celestial[equip]] = 1

            reward_equip = self.bot.config['equips']["jewels"][self.celestial[equip]]

            msg_return = f"<:confirmed:721581574461587496>│{reward_equip['icon']} `1` " \
                         f"**{reward_equip['name']}** `adicionado ao seu inventario com sucesso...`"

        await sleep(2)
        await msg.edit(content=msg_return)
        img = choice(git)
        embed = discord.Embed(color=self.bot.color)
        embed.set_image(url=img)
        await ctx.send(embed=embed)

        if "the_one_release" in update['rpg']['quests'].keys():
            _QUEST, _NAME = update['rpg']['quests']["the_one_release"], reward_equip["name"]
            if _QUEST["status"] == "in progress" and update['config']['provinces'] is not None:
                if len(update['rpg']['quests']["the_one_release"]["unsealed"]) == 0:
                    if "violet" in _NAME or "hero" in _NAME or "divine" in _NAME:
                        update['rpg']['quests']["the_one_release"]["unsealed"].append(reward_equip["name"])
                        await ctx.send(f'<a:fofo:524950742487007233>│`PARABENS POR PROGREDIR NA QUEST:`\n'
                                       f'✨ **[The 1 Release]** ✨')

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
        await self.bot.data.add_sts(ctx.author, "unsealed", 1)


def setup(bot):
    bot.add_cog(MeltedClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mUNSEALED\033[1;32m foi carregado com sucesso!\33[m')
