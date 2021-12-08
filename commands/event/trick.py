import disnake

from random import choice, randint
from disnake.ext import commands
from resources.db import Database
from resources.check import check_it
from asyncio import sleep


class TrickTreat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

        self.bag_good = {
            "blessed_enchant_skill": [4, 2],
            "melted_artifact": [5, 2],
            "angel_stone": [6, 4],
            "angel_wing": [10, 5],
            "frozen_letter": [4, 3],
            "quest_part_1": [1, 1],
            "quest_part_2": [1, 1],
            "quest_part_3": [1, 1],
            "quest_part_4": [1, 1],
            "quest_part_5": [1, 1],
            "quest_part_6": [1, 1],
            "quest_part_7": [1, 1],
            "quest_part_final": [1, 1],
        }

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='trickortreat', aliases=['trick'])
    async def trick_treat(self, ctx, amount=None):
        """Comando para sortear um presente para você"""
        if amount is None:
            return await ctx.send('<:alert:739251822920728708>│`Insira a quantidade de Trick or Treat Bag que deseja'
                                  ' usar!`\n**NOTA:** `Quanto mais voce usar, mais chance de ganhar!`')

        try:
            amount_test = int(amount)
        except ValueError:
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você precisa dizer um numero.` '
                                  '**COMANDO CANCELADO**')

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if "ttbag" not in update['inventory'].keys():
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você não tem Trick or Treat Bag no'
                                  ' seu inventario.` **COMANDO CANCELADO**')

        update['inventory']["ttbag"] -= amount_test
        if update['inventory']["ttbag"] < 1:
            del update['inventory']["ttbag"]
        await self.bot.db.update_data(data, update, 'users')

        # ESCOLHENDO O PREMIO:
        list_items, data = list()
        reward = choice(list_items)

        numbers, bonus = [int(n) for n in str(data[1]).replace(".", "")], 0
        for n in numbers:
            bonus += n

        if randint(1, 100) + amount_test + bonus > 95:  # 5% + bonus + amount

            msg = f"{self.bot.items[reward][0]} `{1}` `{self.bot.items[reward][1]}`"
            embed = disnake.Embed(title='🎊 **PARABENS** 🎉 VOCÊ DROPOU', color=self.bot.color, description=msg)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            await ctx.send(embed=embed)

            msg = await ctx.send("<a:loading:520418506567843860>│`SALVANDO SEU PREMIO...`")
            await sleep(3)
            await msg.delete()

            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update = data
            try:
                update['inventory'][reward] += 1
            except KeyError:
                update['inventory'][reward] = 1
            await self.bot.db.update_data(data, update, 'users')
            await ctx.send(f"<:confirmed:721581574461587496>│`PREMIO SALVO COM SUCESSO!`", delete_after=5.0)

        else:
            await ctx.send(f"> `VOCE NAO ACHOU NADA DENTRO DA(S)` **{amount_test}** `TRICK OR TREAT BAG(S)`",
                           delete_after=30.0)
