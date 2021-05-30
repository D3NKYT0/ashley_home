import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import randint, choice
from asyncio import sleep


class MineClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = self.bot.items

        self.chance_mine = [8, 16, 24, 32, 40, 48, 56, 64, 72, 80]
        self.gem = {"copper": 8, "silver": 8, "gold": 8, "platinum": 8, "sapphire": 4,
                    "ruby": 4, "emerald": 4, "amethyst": 4, "onyx": 2, "diamond": 2}

        self.reward = list()
        for k in self.gem.keys():
            self.reward += [k] * self.gem[k]

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='mine', aliases=['minerar'])
    async def mine(self, ctx, amount: int = 1):
        """Comando para minerar pedras preciosas."""
        query = {"_id": 0, "user_id": 1, "inventory": 1, "config": 1}
        data = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        if amount != 1 and data['config']['vip']:
            if amount not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                return await ctx.send('<:alert:739251822920728708>│`A QUANTIDADE DEVE ESTAR ENTRE 1 A 9!`')

        if "Energy" not in data['inventory'].keys():
            _text = '<:negate:721581573396496464>│`VOCE NÃO TEM ENERGIA!`'
            embed = discord.Embed(color=self.bot.color, description=_text)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.minerando:
            return await ctx.send('<:alert:739251822920728708>│`VOCÊ JA ESTÁ MINERANDO...`')

        if data['config']['vip']:
            _amount, _und = 25 * amount if amount != 1 else 25, amount if amount != 1 else 1
        else:
            _amount, _und = 25, 1

        if data['inventory']['Energy'] < _amount:
            return await ctx.send(f'<:alert:739251822920728708>│`VOCÊ PRECISA DE {_amount} ENERGIAS PARA MINERAR`')

        data['inventory']['Energy'] -= _amount
        if data['inventory']['Energy'] < 1:
            del data['inventory']['Energy']

        self.bot.minerando.append(ctx.author.id)
        cl = await self.bot.db.cd("users")
        query = {"$set": {"inventory": data['inventory']}}
        await cl.update_one({"user_id": data["user_id"]}, query, upsert=False)
        quant = 0

        text = "<a:loading:520418506567843860>|`Minerando...`"
        embed = discord.Embed(color=self.bot.color, description=text)
        msg = await ctx.send(embed=embed)

        _items = dict()

        for _ in range(_und):

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[0]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})

            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[1]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[2]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[3]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[4]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[5]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[6]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[7]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[8]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

            if not data['config']['vip']:
                await sleep(5)

            # ========================================================================================
            chance = randint(1, 100)
            if chance < self.chance_mine[9]:
                if chance == 1:
                    quant += 2
                    item = 2
                else:
                    quant += 1
                    item = 1

                reward = choice(self.reward)

                try:
                    _items[reward] += item
                except KeyError:
                    _items[reward] = item

                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": ctx.author.id}, {"$inc": {f"inventory.{reward}": item}})
            # ========================================================================================

        await msg.delete()  # fim da mineração

        miner = ""  # inicio da mineração

        for key in _items.keys():
            miner += f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 {ctx.author.name} `VOCE MINEROU:`\n" \
                     f"`+{_items[key]}` {self.items[key][0]} **{self.items[key][1]}**\n"

        if miner != "":
            await ctx.send(miner)

        # ========================================================================================
        await ctx.send(f"<:confirmed:721581574461587496>│{ctx.author.name} `VOCE MINEROU:`\n"
                       f"`{quant}` **ITENS NO TOTAL.**")
        # ========================================================================================

        self.bot.minerando.remove(ctx.author.id)
        await self.bot.data.add_sts(ctx.author, "mine", 1)


def setup(bot):
    bot.add_cog(MineClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMINE_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
