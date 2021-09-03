import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice


class QuestClass(commands.Cog):
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
    @commands.group(name='completed', aliases=['completado', "completar"])
    async def completed(self, ctx):
        if ctx.channel.id != 840007934967808030:
            msg = "<:negate:721581573396496464>│`VOCÊ APENAS PODE USAR ESSE COMANDO NO CANAL:` **QUESTS** " \
                  "`NO SERVIDOR DE SUPORTE DA ASHLEY!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

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

        completed = False
        for quest in update['rpg']['quests'].keys():
            if update['rpg']['quests'][quest]["status"] == "in progress":

                if quest == "the_eight_evils_of_the_moon":
                    if len(update['rpg']['quests'][quest]["mini-boss"]) == 8:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 8 Evils of the Moon]** `foi terminada com sucesso!`'
                        embed = discord.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(10):
                            reward.append(choice(["soul_crystal_of_love", "soul_crystal_of_love", "fused_sapphire",
                                                  "soul_crystal_of_love", "soul_crystal_of_hope", "fused_diamond",
                                                  "soul_crystal_of_hope", "soul_crystal_of_hope",  "fused_diamond",
                                                  "soul_crystal_of_hate", "soul_crystal_of_hate", "fused_ruby",
                                                  "soul_crystal_of_hate", "fused_ruby", "fused_sapphire", "gold_cube",
                                                  "fused_sapphire",  "fused_emerald", "fused_emerald", "golden_apple",
                                                  "unsealed_stone", "melted_artifact", "golden_egg", "stone_of_moon"]))
                        reward.append("blessed_enchant_skill")
                        reward.append("enchant_divine")
                        reward.append("armor_divine")
                        reward.append("blessed_enchant_hero")
                        reward.append("blessed_armor_hero")
                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 25000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       f'{response}')

                if quest == "the_three_sacred_scrolls":
                    if len(update['rpg']['quests'][quest]["scroll"]) == 3:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 3 Holy Scrolls]** `foi terminada com sucesso!`'
                        embed = discord.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(5):
                            reward.append(choice(["soul_crystal_of_love", "soul_crystal_of_love", "fused_sapphire",
                                                  "soul_crystal_of_love", "soul_crystal_of_hope", "fused_diamond",
                                                  "soul_crystal_of_hope", "soul_crystal_of_hope",  "fused_diamond",
                                                  "soul_crystal_of_hate", "soul_crystal_of_hate", "fused_ruby",
                                                  "soul_crystal_of_hate", "fused_ruby", "fused_sapphire", "gold_cube",
                                                  "fused_sapphire",  "fused_emerald", "fused_emerald", "golden_apple",
                                                  "unsealed_stone", "melted_artifact", "golden_egg", "stone_of_moon"]))
                        reward.append("blessed_enchant_skill")
                        reward.append("enchant_divine")
                        reward.append("armor_divine")
                        reward.append("blessed_enchant_hero")
                        reward.append("blessed_armor_hero")
                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       f'{response}')

                if quest == "the_seven_lost_souls":
                    if len(update['rpg']['quests'][quest]["souls"]) == 7:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 7 Lost Souls]** `foi terminada com sucesso!`'
                        embed = discord.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(5):
                            reward.append(choice(["soul_crystal_of_love", "soul_crystal_of_love", "fused_sapphire",
                                                  "soul_crystal_of_love", "soul_crystal_of_hope", "fused_diamond",
                                                  "soul_crystal_of_hope", "soul_crystal_of_hope",  "fused_diamond",
                                                  "soul_crystal_of_hate", "soul_crystal_of_hate", "fused_ruby",
                                                  "soul_crystal_of_hate", "fused_ruby", "fused_sapphire", "gold_cube",
                                                  "fused_sapphire",  "fused_emerald", "fused_emerald", "golden_apple",
                                                  "unsealed_stone", "melted_artifact", "golden_egg", "stone_of_moon"]))
                        reward.append("blessed_enchant_skill")
                        reward.append("enchant_divine")
                        reward.append("armor_divine")
                        reward.append("blessed_enchant_hero")
                        reward.append("blessed_armor_hero")
                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       f'{response}')

        if not completed:
            msg = '<:alert:739251822920728708>│`VOCE NAO TEM NENHUMA QUEST PARA COMPLETAR!`'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='quest', aliases=['q'])
    async def quest(self, ctx):
        """Comando usado pra retornar a lista de subcomandos de quest
                Use ash quest"""
        if ctx.invoked_subcommand is None:
            self.status()
            embed = discord.Embed(color=self.color)
            embed.add_field(name="Quest Commands:",
                            value=f"{self.st[117]} `quest eight` [The 8 Evils of the Moon]\n"
                                  f"{self.st[117]} `quest three` [The 3 Holy Scrolls]\n"
                                  f"{self.st[117]} `quest seven` [The 7 Lost Souls]")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='eight', aliases=['oito'])
    async def _eight(self, ctx):
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

        if "the_eight_evils_of_the_moon" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_eight_evils_of_the_moon"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 8 Evils of the Moon]** `já foi terminada!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{b.upper()}**" for b in _QUEST["mini-boss"]]), _QUEST["status"]
            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 8 Evils of the Moon]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["mini-boss"])}/8**\n' \
                  f'`[MINI-BOSSES]:`\n' \
                  f'{_MB}'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_eight_evils_of_the_moon = {"mini-boss": list(), "status": "in progress"}
        update['rpg']['quests']["the_eight_evils_of_the_moon"] = the_eight_evils_of_the_moon
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 8 Evils of the Moon]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='three', aliases=['tres'])
    async def _three(self, ctx):
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

        if "the_three_sacred_scrolls" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_three_sacred_scrolls"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 3 Holy Scrolls]** `já foi terminada!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{b.upper()}**" for b in _QUEST["scroll"]]), _QUEST["status"]
            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 3 Holy Scrolls]**\n' \
                  f'`[STATUS]:` **{status}**\n`[PROGRESS]:` **{len(_QUEST["scroll"])}/3**\n'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_three_sacred_scrolls = {"scroll": list(), "status": "in progress"}
        update['rpg']['quests']["the_three_sacred_scrolls"] = the_three_sacred_scrolls
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 3 Holy Scrolls]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='seven', aliases=['sete'])
    async def _seven(self, ctx):
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

        if "the_seven_lost_souls" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_seven_lost_souls"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 7 Lost Souls]** `já foi terminada!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{b.upper()}**" for b in _QUEST["souls"]]), _QUEST["status"]
            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 7 Lost Souls]**\n' \
                  f'`[STATUS]:` **{status}**\n`[PROGRESS]:` **{len(_QUEST["souls"])}/7**\n'
            embed = discord.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_seven_lost_souls = {"scroll": list(), "status": "in progress"}
        update['rpg']['quests']["the_seven_lost_souls"] = the_seven_lost_souls
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 7 Lost Souls]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(QuestClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mQUESTCLASS\033[1;32m foi carregado com sucesso!\33[m')
