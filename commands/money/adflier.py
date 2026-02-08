import discord

from random import choice, randint
from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.giftmanage import register_code, generate_gift
from resources.utility import convert_item_name
from resources.crypto import encrypt_text, decrypt_text


class Adflier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color
        self.i = self.bot.items

        self._items = ["G-Bollash", "B-Bollash", "O-Bollash", "R-Bollash"]

        self._reward_g = {"xp-book": 9, "skill-book": 8, "Skill_Lv1": 7, "Skill_Lv2": 6, "Skill_Lv3": 5,
                          "Skill_Lv4": 4, "Skill_Lv5": 3, "Skill_Lv6": 2, "Skill_Lv7": 1, "?-Bollash": 55}

        self._reward_b = {"xp-book": 10, "skill-book": 9, "Skill_Lv1": 8, "Skill_Lv2": 7, "Skill_Lv3": 6,
                          "Skill_Lv4": 5, "Skill_Lv5": 4, "Skill_Lv6": 3, "Skill_Lv7": 2, "?-Bollash": 46}

        self._reward_o = {"xp-book": 12, "skill-book": 11, "Skill_Lv1": 10, "Skill_Lv2": 9, "Skill_Lv3": 8,
                          "Skill_Lv4": 7, "Skill_Lv5": 6, "Skill_Lv6": 5, "Skill_Lv7": 4, "?-Bollash": 28}

        self._reward_r = {"xp-book": 14, "skill-book": 13, "Skill_Lv1": 12, "Skill_Lv2": 11, "Skill_Lv3": 10,
                          "Skill_Lv4": 9, "Skill_Lv5": 8, "Skill_Lv6": 7, "Skill_Lv7": 6, "?-Bollash": 10}

        self._reward_adfly = {

            "1": [("fragment_of_crystal_wind", 4),
                  ("fragment_of_crystal_water", 4),
                  ("fragment_of_crystal_fire", 4),
                  ("blessed_fragment_of_crystal_wind", 2),
                  ("blessed_fragment_of_crystal_water", 2),
                  ("blessed_fragment_of_crystal_fire", 2),
                  ("full_heart", 2),
                  ("adamantium", 2)],

            "2": [("fragment_of_crystal_wind", 8),
                  ("fragment_of_crystal_water", 8),
                  ("fragment_of_crystal_fire", 8),
                  ("blessed_fragment_of_crystal_wind", 4),
                  ("blessed_fragment_of_crystal_water", 4),
                  ("blessed_fragment_of_crystal_fire", 4),
                  ("full_heart", 2),
                  ("adamantium", 4)],

            "3": [("fragment_of_crystal_wind", 16),
                  ("fragment_of_crystal_water", 16),
                  ("fragment_of_crystal_fire", 16),
                  ("blessed_fragment_of_crystal_wind", 6),
                  ("blessed_fragment_of_crystal_water", 6),
                  ("blessed_fragment_of_crystal_fire", 6),
                  ("full_heart", 2),
                  ("adamantium", 6)],

            "4": [("fragment_of_crystal_wind", 32),
                  ("fragment_of_crystal_water", 32),
                  ("fragment_of_crystal_fire", 32),
                  ("blessed_fragment_of_crystal_wind", 8),
                  ("blessed_fragment_of_crystal_water", 8),
                  ("blessed_fragment_of_crystal_fire", 8),
                  ("full_heart", 2),
                  ("adamantium", 8)],

            "5": [("stone_of_crystal_wind", 2),
                  ("stone_of_crystal_water", 2),
                  ("stone_of_crystal_fire", 2),
                  ("blessed_fragment_of_crystal_wind", 12),
                  ("blessed_fragment_of_crystal_water", 12),
                  ("blessed_fragment_of_crystal_fire", 12),
                  ("full_heart", 2),
                  ("adamantium", 10)],
        }

    @check_it(no_pm=True)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.cooldown(1, 60.0, commands.BucketType.user)
    @commands.command(name='adfly')
    async def adfly(self, ctx, *, item=None):
        """Comando de mineração de fragmento de Blessed Ethernyas"""
        if item is None:
            _bonus = None
        else:
            item_key = convert_item_name(item, self.bot.items)
            if item_key is None:
                return await ctx.send("<:alert:739251822920728708>│`Item Inválido!`")
            if item_key not in self._items:
                return await ctx.send("<:alert:739251822920728708>│`Você não pode usar esse tipo de item aqui.`")

            data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_user = data_user

            if update_user['config']['playing']:
                return await ctx.send("<:alert:739251822920728708>│`Você está jogando, aguarde para quando"
                                      " vocÊ estiver livre!`")

            if update_user['config']['battle']:
                msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
                embed = discord.Embed(color=self.bot.color, description=msg)
                return await ctx.send(embed=embed)

            item_name = self.bot.items[item_key][1]

            if item_key in data_user['inventory']:
                if data_user['inventory'][item_key] >= 1:
                    update_user['inventory'][item_key] -= 1
                    if update_user['inventory'][item_key] < 1:
                        del update_user['inventory'][item_key]

                    await self.bot.db.update_data(data_user, update_user, 'users')
                    await ctx.send(f'<:confirmed:721581574461587496>│`PARABENS, VC USOU` {self.i[item_name][0]} `1`'
                                   f'**{self.i[item_name][1]}** `COM SUCESSO!`')
                    _bonus = item_name

                else:
                    return await ctx.send(f"<:alert:739251822920728708>│`VOCÊ NÃO TEM ESSA QUANTIDADE DISPONIVEL DE "
                                          f"{item_name.upper()}!`")
            else:
                return await ctx.send(f"<:alert:739251822920728708>│`Você não tem {item_name.upper()} no seu "
                                      f"inventario!`")

        _data = await self.bot.db.get_data("_id", ctx.author.id, "adfly")
        _update = _data
        if _update is not None:
            if _update['pending']:
                text = f'<:alert:739251822920728708>│Você ainda tem esse link pendente:\n{_update["adlink"]["secureShortURL"]}'
                embed = discord.Embed(color=self.color, description=text)
                try:
                    await ctx.author.send(embed=embed)
                    if ctx.message.guild is not None:
                        return await ctx.send('<:send:519896817320591385>│`ENVIADO PARA O SEU PRIVADO!`')
                except discord.Forbidden:
                    return await ctx.send(embed=embed)
            else:
                _code1, _code2 = generate_gift()
                code = encrypt_text(_code1)
                codelink = code[0].replace("/", "denky")
                dataShorlink = self.bot.adlinks(codelink)
                _update['code'] = [code[0], _code2]
                _update['adlink'] = [dataShorlink, dataShorlink]
                _update['bonus'] = _bonus
                _update['pending'] = True
                _update['key'] = code[2]
                _update['iv'] = code[1]
                await self.bot.db.update_data(_data, _update, 'adfly')

                text = f'<:confirmed:721581574461587496>│Clique no link para pegar seu fragmento:\n{dataShorlink["secureShortURL"]}'
                embed = discord.Embed(color=self.color, description=text)
                try:
                    await ctx.author.send(embed=embed)
                    if ctx.message.guild is not None:
                        await ctx.send('<:send:519896817320591385>│`ENVIADO PARA O SEU PRIVADO!`')
                except discord.Forbidden:
                    await ctx.send(embed=embed)

        else:
            _code1, _code2 = generate_gift()
            code = encrypt_text(_code1)
            codelink = code[0].replace("/", "denky")
            dataShorlink = self.bot.adlinks(codelink)
            await register_code(self.bot, ctx.author.id, code[0], _code2, dataShorlink, dataShorlink, _bonus, code[1], code[2])

            text = f'<:confirmed:721581574461587496>│Clique no link para pegar seu fragmento:\n{dataShorlink["secureShortURL"]}'
            embed = discord.Embed(color=self.color, description=text)
            try:
                await ctx.author.send(embed=embed)
                if ctx.message.guild is not None:
                    await ctx.send('<:send:519896817320591385>│`ENVIADO PARA O SEU PRIVADO!`')
            except discord.Forbidden:
                await ctx.send(embed=embed)

    @check_it(no_pm=False)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.cooldown(1, 30.0, commands.BucketType.user)
    @commands.command(name='adlink')
    async def adlink(self, ctx, *, code=None):
        """Comando de resgate de mineração de fragmento de Blessed Ethernyas"""
        if code is None:
            return await ctx.send("<:negate:721581573396496464>│`Você precisa digitar um código para resgatar!`")

        data = await self.bot.db.get_data("_id", ctx.author.id, "adfly")
        update = data

        if update is None:
            return await ctx.send("<:negate:721581573396496464>│`Você ainda não gerou nenhum código com o comando:`"
                                  " **ash adfly**")

        key = decrypt_text(update['code'][0], update['iv'], update['key']) if "-" in code else update['code'][1]
        if key.upper() != code.upper():
            return await ctx.send("<:negate:721581573396496464>│`Não foi você que gerou esse código com o comando:`"
                                  " **ash adfly**")

        if not update['pending']:
            return await ctx.send("<:negate:721581573396496464>│`Esse código já foi utilizado, use o comando:`"
                                  " **ash adfly** `novamente para obter um novo código!`")

        if update['bonus'] is not None:
            if update['bonus'][:1] == "G":
                _reward = list()
                for k in self._reward_g.keys():
                    _reward += [k] * self._reward_g[k]
                _bonus = choice(_reward)
            elif update['bonus'][:1] == "B":
                _reward = list()
                for k in self._reward_b.keys():
                    _reward += [k] * self._reward_b[k]
                _bonus = choice(_reward)
            elif update['bonus'][:1] == "O":
                _reward = list()
                for k in self._reward_o.keys():
                    _reward += [k] * self._reward_o[k]
                _bonus = choice(_reward)
            else:
                _reward = list()
                for k in self._reward_r.keys():
                    _reward += [k] * self._reward_r[k]
                _bonus = choice(_reward)

            data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_user = data_user

            try:
                update_user['inventory'][_bonus] += 1
            except KeyError:
                update_user['inventory'][_bonus] = 1
            await self.bot.db.update_data(data_user, update_user, 'users')
            await ctx.send(f'<:confirmed:721581574461587496>│`PARABENS, VC USOU` {self.i[update["bonus"]][0]} `1`'
                           f' **{self.i[update["bonus"]][1]}** `NA HORA DE GERAR O CODIGO E GANHOU A MAIS` '
                           f'{self.i[_bonus][0]} `1` **{self.i[_bonus][1]}**')

        self.bot.addelete(update['adlink'][0]['idString'])
        update['pending'] = False
        await self.bot.db.update_data(data, update, 'adfly')

        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user

        msg = ""
        frags = randint(1, 2)
        if data_user['config']['vip']:
            msg += "✨ `POR VOCE SER VIP GANHOU FRAGMENTOS A MAIS` ✨\n"
            frags += randint(1, 2)
        if data_guild['vip']:
            msg += "✨ `POR SUA GUILDA SER VIP GANHOU FRAGMENTOS A MAIS` ✨\n"
            frags += randint(1, 2)

        update_user['true_money']['fragment'] += frags
        update_user['true_money']['adfly'] += 1
        lucky = "5" if update_user['true_money']['adfly'] % 10 == 0 else choice(['1', '2', '3', '4'])
        msg_itens = ""

        for item_discovered in self._reward_adfly[lucky]:
            amount = randint(1, item_discovered[1])
            try:
                update_user['inventory'][item_discovered[0]] += amount
            except KeyError:
                update_user['inventory'][item_discovered[0]] = amount

            msg_itens += f"{self.i[item_discovered[0]][0]} `{amount}` **{self.i[item_discovered[0]][1]}**\n"

        await self.bot.db.update_data(data_user, update_user, 'users')
        await ctx.send(f"<a:fofo:524950742487007233>│`VOCÊ GANHOU` ✨ **{frags} FRAGMENTO DE BLESSED ETHERNYA** ✨\n"
                       f"{msg}`Você tambem ganhou:`\n{msg_itens}")


async def setup(bot):
    await bot.add_cog(Adflier(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mADFLY\033[1;32m foi carregado com sucesso!\33[m')
