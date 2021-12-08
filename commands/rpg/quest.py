import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice


class QuestClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color
        self.reward = ["soul_crystal_of_love", "soul_crystal_of_hate", "soul_crystal_of_hope", "moon_bag",
                       "fused_diamond", "fused_sapphire", "fused_ruby", "fused_sapphire", "frozen_letter",
                       "stone_of_moon", "unsealed_stone", "melted_artifact", "pass_royal", "teleport_scroll",
                       "gold_cube", "golden_apple", "golden_egg", "lost_parchment", "royal_parchment", "sages_scroll",
                       "seed", "ore_bar", "debris", "coal", "claw", "charcoal", "branch", "braided_hemp",
                       "feather_white", "feather_gold", "feather_black", "herb_red", "herb_green", "herb_blue"]

        self.reward_especial = ["blessed_enchant_skill", "enchant_divine", "armor_divine", "blessed_enchant_hero",
                                "blessed_armor_hero", "blessed_armor_violet", "blessed_armor_inspiron",
                                "blessed_armor_mystic", "blessed_armor_silver"]

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='completed', aliases=['completado', "completar"])
    async def completed(self, ctx):
        """Comando para verificar se voce tem alguma quest que ja foi completada!"""
        if ctx.channel.id != 840007934967808030:
            msg = "<:negate:721581573396496464>│`VOCÊ APENAS PODE USAR ESSE COMANDO NO CANAL:` **QUESTS** " \
                  "`NO SERVIDOR DE SUPORTE DA ASHLEY!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        completed = False
        for quest in update['rpg']['quests'].keys():
            if update['rpg']['quests'][quest]["status"] == "in progress":

                if quest == "the_one_release":
                    if len(update['rpg']['quests'][quest]["unsealed"]) == 1:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 1 Release]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(1):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 10000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_two_loves":
                    if len(update['rpg']['quests'][quest]["loves"]) == 2:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 2 Loves]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(2):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 12000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_three_sacred_scrolls":
                    if len(update['rpg']['quests'][quest]["scroll"]) == 3:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 3 Holy Scrolls]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(3):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_four_crowns":
                    if len(update['rpg']['quests'][quest]["crowns"]) == 4:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 4 Crowns]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(4):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_five_shirts":
                    if len(update['rpg']['quests'][quest]["shirts"]) == 5:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 5 Shirts]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(5):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_six_potions":
                    if len(update['rpg']['quests'][quest]["potions"]) == 6:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 6 Potions]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(6):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_seven_lost_souls":
                    if len(update['rpg']['quests'][quest]["souls"]) == 7:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 7 Lost Souls]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(7):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 15000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_eight_evils_of_the_moon":
                    if len(update['rpg']['quests'][quest]["mini-boss"]) == 8:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 8 Evils of the Moon]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(8):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 25000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ '
                                       f'{response}')

                if quest == "the_nine_villages":
                    if len(update['rpg']['quests'][quest]["villages"]) == 9:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 9 Villages]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(9):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 20000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

                if quest == "the_ten_provinces":
                    if len(update['rpg']['quests'][quest]["provinces"]) == 10:
                        update['rpg']['quests'][quest]["status"], completed = "completed", True
                        await self.bot.db.update_data(data, update, 'users')

                        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` ' \
                              '**[The 10 Provinces]** `foi terminada com sucesso!`'
                        embed = disnake.Embed(color=self.bot.color, description=msg)
                        await ctx.send(embed=embed)

                        reward = list()
                        for _ in range(10):
                            reward.append(choice(self.reward))

                        for _ in range(5):
                            reward.append(choice(self.reward_especial))

                        response = await self.bot.db.add_reward(ctx, reward)
                        answer = await self.bot.db.add_money(ctx, 18000, True)
                        await ctx.send(f'<a:fofo:524950742487007233>│`{ctx.author.name.upper()} GANHOU!` {answer}\n'
                                       f'`VOCÊ TAMBEM GANHOU` ✨ **ITENS DO RPG** ✨ {response}')

        if not completed:
            msg = '<:alert:739251822920728708>│`VOCE NAO TEM NENHUMA QUEST PARA COMPLETAR!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
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
            data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            one, two, three, four, five = False, False, False, False, False
            six, seven, eight, nine, ten = False, False, False, False, False
            for quest in data['rpg']['quests'].keys():
                if data['rpg']['quests'][quest]["status"] == "completed":
                    if quest == "the_one_release":
                        one = True
                    if quest == "the_two_loves":
                        two = True
                    if quest == "the_three_sacred_scrolls":
                        three = True
                    if quest == "the_four_crowns":
                        four = True
                    if quest == "the_five_shirts":
                        five = True
                    if quest == "the_six_potions":
                        six = True
                    if quest == "the_seven_lost_souls":
                        seven = True
                    if quest == "the_eight_evils_of_the_moon":
                        eight = True
                    if quest == "the_nine_villages":
                        nine = True
                    if quest == "the_ten_provinces":
                        ten = True

            emoji = "<:confirmado:519896822072999937>"
            embed = disnake.Embed(color=self.color)
            embed.add_field(name="Quest Commands:",
                            value=f"{self.st[117]} `quest one` [The 1 Release] {emoji if one else ''}\n"
                                  f"{self.st[117]} `quest two` [The 2 Loves] {emoji if two else ''}\n"
                                  f"{self.st[117]} `quest three` [The 3 Holy Scrolls] {emoji if three else ''}\n"
                                  f"{self.st[117]} `quest four` [The 4 Crowns] {emoji if four else ''}\n"
                                  f"{self.st[117]} `quest five` [The 5 Shirts] {emoji if five else ''}\n"
                                  f"{self.st[117]} `quest six` [The 6 Potions] {emoji if six else ''}\n"
                                  f"{self.st[117]} `quest seven` [The 7 Lost Souls] {emoji if seven else ''}\n"
                                  f"{self.st[117]} `quest eight` [The 8 Evils of the Moon] {emoji if eight else ''}\n"
                                  f"{self.st[117]} `quest nine` [The 9 Villages] {emoji if nine else ''}\n"
                                  f"{self.st[117]} `quest ten` [The 10 Provinces] {emoji if ten else ''}")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='one', aliases=['um'])
    async def _one(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_one_release" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_one_release"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 1 Release]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            status = _QUEST["status"]

            description = "Olá caro(a) aventureiro(a), um ferreiro mestre está precisando de um equipamento muito " \
                          "raro de ser conseguido para um grande guerreiro nobre do reino. **Preciso que você vá para" \
                          " qualquer província e tire o selamento de algum equipamento e que venha com alguma das" \
                          " seguintes raridades: Violet e Hero.**"

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 1 Release]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["unsealed"])}/1**\n' \
                  f'<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_one_release = {"unsealed": list(), "status": "in progress"}
        update['rpg']['quests']["the_one_release"] = the_one_release
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 1 Release]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='two', aliases=['dois'])
    async def _two(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_two_loves" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_two_loves"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 2 Loves]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            status = _QUEST["status"]

            description = "Olá caro(a) casado(a), uma feiticeira da capital está querendo fazer uma poção muito" \
                          " difícil de ser criada, mas infelizmente não possui os dois últimos ingredientes para" \
                          " terminar. **Para isso, preciso que você obtenha os seguintes itens: _Heart Right_ e " \
                          "_Heart Left_. Esses dois itens são obtidos a partir do `ash love` com cônjuge, caso você" \
                          " consiga esses itens, use algum dos comandos de membro para progredir na Quest. Exemplo:" \
                          " `ash dance`.**"

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 2 Loves]**\n' \
                  f'`[STATUS]:` **{status}**\n`[PROGRESS]:` ' \
                  f'**{len(_QUEST["loves"])}/2**\n<:afs:530031864350507028> {description}'

            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_two_loves = {"loves": list(), "status": "in progress"}
        update['rpg']['quests']["the_two_loves"] = the_two_loves
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 2 Loves]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='three', aliases=['tres'])
    async def _three(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_three_sacred_scrolls" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_three_sacred_scrolls"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 3 Holy Scrolls]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{str(b).upper()}**" for b in _QUEST["scroll"]]), _QUEST["status"]

            description = "Olá caro(a) aventureiro(a), o rei do reino está precisando de sua ajuda. Recentemente," \
                          " três pergaminhos importantes e antigos foram roubados,  precisamos que você recupere" \
                          " eles para a gente ! **Preciso que você vá para qualquer província e batalhe com monstros" \
                          " (`ash battle`), algum deles comeram cópias dos pergaminhos.**"

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 3 Holy Scrolls]**\n' \
                  f'`[STATUS]:` **{status}**\n`[PROGRESS]:` ' \
                  f'**{len(_QUEST["scroll"])}/3**\n<:afs:530031864350507028> {description}'

            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_three_sacred_scrolls = {"scroll": list(), "status": "in progress"}
        update['rpg']['quests']["the_three_sacred_scrolls"] = the_three_sacred_scrolls
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 3 Holy Scrolls]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='four', aliases=['quatro'])
    async def _four(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_four_crowns" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_four_crowns"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 4 Crowns]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{str(b).upper()}**" for b in _QUEST["crowns"]]), _QUEST["status"]

            description = "Olá  caro(a) guerreiro(a), o conselho de batalha do reino determinou que a capital e os" \
                          " cidadãos correm perigo com os monstros poderosos que estão espalhados pelo reino. " \
                          "**Precisamos que você mate e pegue a Crown dos seguintes bosses: " \
                          "_Dark Magician_, _Obelisk_, _Slifer_ e _White Dragon_.**"

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 4 Crowns]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["crowns"])}/4**\n' \
                  f'`[CROWNS]:`\n{_MB}' \
                  f'\n<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_four_crowns = {"crowns": list(), "status": "in progress"}
        update['rpg']['quests']["the_four_crowns"] = the_four_crowns
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 4 Crowns]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='five', aliases=['cinco'])
    async def _five(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_five_shirts" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_five_shirts"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 5 Shirts]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{str(b).upper()}**" for b in _QUEST["shirts"]]), _QUEST["status"]

            description = "Olá caro(a) aventureiro(a), precisamos urgentemente da sua ajuda. Estamos querendo criar" \
                          " um feitiço para que os monstros não cheguem perto da capital, mas estão faltando 5 itens" \
                          " muito raros de serem conseguidos. **Precisamos que você consiga as 5 Vestes Celestias," \
                          " mas para conseguir elas, você precisará do _Scroll of Shirt_ " \
                          "e ir batalhar no inferno (`ash hell`).**"

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 5 Shirts]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["shirts"])}/5**\n' \
                  f'`[SHIRTS]:`\n{_MB}' \
                  f'\n<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_five_shirts = {"shirts": list(), "status": "in progress"}
        update['rpg']['quests']["the_five_shirts"] = the_five_shirts
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 5 Shirts]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='six', aliases=['seis'])
    async def _six(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_six_potions" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_six_potions"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 6 Potions]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{str(b).upper()}**" for b in _QUEST["potions"]]), _QUEST["status"]

            description = "Olá caro(a) aventureiro(a), precisamos urgentemente da sua ajuda. Estamos querendo criar " \
                          "6 poções paginas afim de conseguirmos o item de defesa máxima, o lendario (SALVATION)." \
                          " Vá ate uma provincia e crafte todas as 6 poções que necessitamos para criar esse item " \
                          "DIVINO!"

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 6 Potions]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["potions"])}/6**\n' \
                  f'`[POTIONS]:`\n{_MB}' \
                  f'\n<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_six_potions = {"potions": list(), "status": "in progress"}
        update['rpg']['quests']["the_six_potions"] = the_six_potions
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 6 Potions]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='seven', aliases=['sete'])
    async def _seven(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_seven_lost_souls" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_seven_lost_souls"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 7 Lost Souls]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            souls = {
                "1": "assassin",
                "2": "necromancer",
                "3": "paladin",
                "4": "priest",
                "5": "warlock",
                "6": "warrior",
                "7": "wizard"
            }

            _MB, status = "\n".join([f"**{str(souls[str(b)]).upper()}**" for b in _QUEST["souls"]]), _QUEST["status"]
            description = "Olá caro(a) guerreiro(a), os melhores magos(a) e ferreiros(a) fizeram uma reunião " \
                          "na capital, eles estavam pensando em uma maneira de fazer as armas terem mais " \
                          "durabilidade e eficiência com magia, mas para isso eles precisam que todas as armas " \
                          "estejam reunidos no mesmo lugar para serem analisados. **Para isso, preciso que você " \
                          "consiga uma arma no `ash battle` de cada classe existente**.\n" \
                          "**`OBS:`** **As armas são a alma de um cavaleiro(a), então será um pouco difícil " \
                          "de conseguir, boa sorte guerreiro(a)**."
            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 7 Lost Souls]**\n' \
                  f'`[STATUS]:` **{status}**\n`[PROGRESS]:` **{len(_QUEST["souls"])}/7**\n' \
                  f'`[SOULS]:`\n{_MB}' \
                  f'\n<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_seven_lost_souls = {"souls": list(), "status": "in progress"}
        update['rpg']['quests']["the_seven_lost_souls"] = the_seven_lost_souls
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 7 Lost Souls]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='eight', aliases=['oito'])
    async def _eight(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_eight_evils_of_the_moon" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_eight_evils_of_the_moon"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 8 Evils of the Moon]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            _MB, status = "\n".join([f"**{str(b).upper()}**" for b in _QUEST["mini-boss"]]), _QUEST["status"]
            description = "Olá caro(a) cavaleiro(a), o nosso time de defesa do reino detectou 8 anomalias muito " \
                          "poderosas dentro do reino. O nosso conselho de batalha teme que essas anomalias sejam " \
                          "monstros muito fortes tentando destruir totalmente o reino. **Precisamos que você derrote" \
                          " todos esses 'Mini-bosses' para que todo o reino não seja destruido.**\n" \
                          "**`OBS`**: **Para batalhar com os mini-bosses, basta usar o `ash battle moon`. " \
                          "Você precisará ter uma `Stone of Moon`.**"
            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 8 Evils of the Moon]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["mini-boss"])}/8**\n' \
                  f'`[MINI-BOSSES]:`\n{_MB}' \
                  f'\n<:ash:834120294469730315> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_eight_evils_of_the_moon = {"mini-boss": list(), "status": "in progress"}
        update['rpg']['quests']["the_eight_evils_of_the_moon"] = the_eight_evils_of_the_moon
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 8 Evils of the Moon]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='nine', aliases=['nove'])
    async def _nine(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_nine_villages" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_nine_villages"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 9 Villages]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            names = ""
            for gui in _QUEST["villages"]:
                names += f"**{str(self.bot.get_guild(gui))}**\n"

            status = _QUEST["status"]
            description = "Olá caro(a) aventureiro(a), após a batalha com os mini-bosses, muitas vilas ficaram com" \
                          " muito prejuizo e algumas foram totalmente destruidas e o rei ficou muito preocupado" \
                          " com isso. **Precisamos que você vá em 9 servidores com mais de 50 membros e use" \
                          " comandos lá.** Isso será de suma importancia para que possamos " \
                          "calcular o tamanho do estrago feito no reino todo."
            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 9 Villages]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["villages"])}/9**\n' \
                  f'`[VILLAGES]`:\n{names}' \
                  f'\n<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_nine_villages = {"villages": list(), "status": "in progress"}
        update['rpg']['quests']["the_nine_villages"] = the_nine_villages
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 9 Villages]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @quest.group(name='ten', aliases=['dez'])
    async def _ten(self, ctx):
        """quest a ser feita no rpg da ashley"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not update['rpg']['active']:
            msg = "<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if "the_ten_provinces" in update['rpg']['quests'].keys():
            _QUEST = update['rpg']['quests']["the_ten_provinces"]
            if _QUEST["status"] == "completed":
                msg = '<:confirmed:721581574461587496>│`A QUEST:` **[The 10 Provinces]** `já foi terminada!`'
                embed = disnake.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            names = ""
            for pro in _QUEST["provinces"]:
                names += f"**{str(self.bot.get_channel(pro))}**\n"

            status = _QUEST["status"]

            description = "Olá caro(a) guerreiro(a), um nobre estava querendo que seus equipamentos fossem mais " \
                          "poderosos que outros no reino, mas o mago mestre que ele visitou, não possui todos os " \
                          "encantamentos possiveis para realizar tal façanha. **Para isso, ele precisa que você vá " \
                          "em cada província e tente criar um encantamento com o `ash create`**."

            msg = f'<:alert:739251822920728708>│`QUEST:` **[The 10 Provinces]**\n' \
                  f'`[STATUS]:` **{status}**\n' \
                  f'`[PROGRESS]:` **{len(_QUEST["provinces"])}/10**\n' \
                  f'`[PROVINCES]`:\n{names}' \
                  f'\n<:afs:530031864350507028> {description}'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        the_ten_provinces = {"provinces": list(), "status": "in progress"}
        update['rpg']['quests']["the_ten_provinces"] = the_ten_provinces
        msg = '<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 `a quest` **[The 10 Provinces]** ' \
              '`foi ativada na sua conta com sucesso!`'
        await self.bot.db.update_data(data, update, 'users')
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(QuestClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mQUESTCLASS\033[1;32m foi carregado com sucesso!\33[m')
