import discord

from discord.ext import commands
from resources.db import Database
from resources.check import check_it
from resources.utility import include, reward_broken, convert_item_name
from random import randint


class BrokenClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        self.equips = equips_list
        self.slots = ["breastplate", "leggings", "boots", "gloves", "shoulder"]
        self.rarities = ["silver", "mystic", "inspiron", "violet", "hero"]
        self.legend = {
            "uncommon": "silver",
            "rare": "mystic",
            "super rare": "inspiron",
            "ultra rare": "violet",
            "secret": "hero",
        }
        self.jewel = {
            "essence_cover": "jewel_cover",
            "essence_leather": "jewel_leather",
            "essence_platinum": "jewel_platinum",
        }
        self.reward = reward_broken

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='broken', aliases=['quebrar'])
    async def broken(self, ctx, *, item=None):
        if item is None:
            return await ctx.send("<:negate:721581573396496464>│`Você precisa colocar o nome de um item que deseja "
                                  "quebrar:` **ash broken <nome_do_item>** `voce consegue ver os itens "
                                  "usando o comando:` **ash es**")

        if item not in [i[1]["name"] for i in self.equips]:
            if "sealed" in item:
                return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM ESTÁ SELADO, ANTES DISSO TIRE O SELO "
                                      "USANDO O COMANDO:` **ASH LIBERAR** `E USE O NOME DO COMANDO:` "
                                      "**ASH INVENTORY EQUIP** `OU` **ASH I E**")

            return await ctx.send("<:negate:721581573396496464>│`ESSE ITEM NAO EXISTE...`\n"
                                  "`Verifique se vc digitou o comando corretamente:`\n"
                                  "`Ex:` **ash e i EARRING OF DIAMOND - HERO**")

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        data_item, data_key = None, None
        for i in self.equips:
            if i[1]["name"] == item:
                data_item, data_key = i[1], i[0]

        if data_item is None or data_key is None:
            msg = "<:negate:721581573396496464>│`COMANDO CANCELADO: HOUVE UM ERRO INESPERADO!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if data_item["slot"] not in self.slots or not include(item, self.rarities):
            msg = "<:negate:721581573396496464>│`COMANDO CANCELADO: ESSE EQUIPAMENTO NAO PODE SER QUEBRADO!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if data_key not in update['rpg']["items"].keys():
            msg = "<:negate:721581573396496464>│`VOCE NAO TEM ESSE ITEM...`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        # aqui esta tirando o item do inventario
        update['rpg']['items'][data_key] -= 1
        if update['rpg']['items'][data_key] < 1:
            del update['rpg']['items'][data_key]

        if "leather" in data_item["name"]:
            equip_type = "leather"
        elif "platinum" in data_item["name"]:
            equip_type = "platinum"
        else:
            equip_type = "cover"

        rarity = self.legend[data_item["rarity"]]
        reward = self.reward[equip_type][data_item["slot"]][rarity]

        msg = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `Por quebrar o item` **{item}** `voce recebeu:`\n"
        for key, amount in reward:
            msg += f"✨ {self.bot.items[key][0]} ✨ `{amount}` **{self.bot.items[key][1]}**\n"
            try:
                update['inventory'][key] += amount
            except KeyError:
                update['inventory'][key] = amount

        await self.bot.db.update_data(data, update, 'users')
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='essence', aliases=['essencia'])
    async def essence(self, ctx, *, item=None):
        if item is None:
            return await ctx.send("<:negate:721581573396496464>│`Você precisa colocar o nome de um item que deseja "
                                  "usar:` **ash essence <nome_do_item>** `voce consegue ver os itens "
                                  "usando o comando:` **ash i**")

        key = convert_item_name(item, self.bot.items)
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if key not in self.jewel.keys():
            msg = '<:negate:721581573396496464>│`NÃO EXISTE ESSA ESSENCIA!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if item not in data['inventory'].keys():
            return await ctx.send("<:negate:721581573396496464>│`Voce não tem esse item no seu invetário...`\n"
                                  "**Obs:** `VOCE CONSEGUE AS ESSENCIA, USANDO O COMANDO` **ASH BROKEN**"
                                  " `E O COMANDO` **ASH ES** `PARA PEGAR OS NOMES DOS EQUIPAMENTOS.`")

        update['inventory'][key] -= 1
        if update['inventory'][key] < 1:
            del update['inventory'][key]

        chance, msg = randint(1, 1000), '<:negate:721581573396496464>│`INFELIZMENTE SUA ESSENCIA ESCAPOU`'
        if chance <= 50 + update["rpg"]["intelligence"]:
            msg = f"<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `voce recebeu:` " \
                  f"✨ {self.bot.items[self.jewel[key]][0]} ✨ `1` **{self.bot.items[self.jewel[key]][1]}**\n"
            try:
                update['inventory'][self.jewel[key]] += 1
            except KeyError:
                update['inventory'][self.jewel[key]] = 1

        await self.bot.db.update_data(data, update, 'users')
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BrokenClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mBROKEN\033[1;32m foi carregado com sucesso!\33[m')
