import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.img_edit import skill_points
from asyncio import TimeoutError
from resources.utility import create_id


class SkillClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botmsg = {}
        self.he = self.bot.help_emoji

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='skill', aliases=['habilidade'])
    async def skill(self, ctx):
        """Comando usado pra ver seus status no rpg da Ashley
        Use ash skill"""
        if ctx.invoked_subcommand is None:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                member = ctx.author

            perms = ctx.channel.permissions_for(ctx.me)
            if not perms.add_reactions:
                return await ctx.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` **ADICIONAR "
                                    "REAÇÕES, PARA PODER FUNCIONAR CORRETAMENTE!**")

            try:
                if self.he[ctx.author.id]:
                    if str(ctx.command) in self.he[ctx.author.id].keys():
                        pass
                    else:
                        self.he[ctx.author.id][str(ctx.command)] = False
            except KeyError:
                self.he[ctx.author.id] = {str(ctx.command): False}

            data = await self.bot.db.get_data("user_id", member.id, "users")
            if data is None:
                embed = disnake.Embed(
                    color=self.bot.color,
                    description='<:negate:721581573396496464>│`MEMBRO NAO CADASTRADO!`')
                return await ctx.send(embed=embed)

            if not data['rpg']['active']:
                embed = disnake.Embed(
                    color=self.bot.color,
                    description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
                return await ctx.send(embed=embed)

            _class = data["rpg"]["class_now"]
            _db_class = data["rpg"]["sub_class"][_class]

            db = {
                "name": member.name,
                "avatar_member": member.display_avatar.with_format("png"),
                "class_now": data['rpg']["class_now"],
                "sub_class": data['rpg']["sub_class"],
                "atk": str(data['rpg']["sub_class"][_class]['status']['atk']),
                "dex": str(data['rpg']["sub_class"][_class]['status']['agi']),
                "acc": str(data['rpg']["sub_class"][_class]['status']['prec']),
                "con": str(data['rpg']["sub_class"][_class]['status']['con']),
                "luk": str(data['rpg']["sub_class"][_class]['status']['luk']),
                "pdh": str(data['rpg']["sub_class"][_class]['status']['pdh']),
                "int": str(data['rpg']['intelligence']),
            }

            await skill_points(db)

            _id = create_id()
            self.botmsg[_id] = await ctx.send(file=disnake.File('skill_points.png'),
                                              content="> `CLIQUE NA IMAGEM PARA MAIORES DETALHES`")
            if not self.he[ctx.author.id][str(ctx.command)]:
                await self.botmsg[_id].add_reaction('<a:help:767825933892583444>')
                await self.botmsg[_id].add_reaction(self.bot.config['emojis']['arrow'][4])

            text = "`--==ENTENDA O QUE OS ATRIBUTOS ALTERAM NO SEU PERSONAGEM==--`\n" \
                   ">>> >>> `ATK` - **O ATK é somado ao seu dano de Skill e ao dano critico**\n" \
                   ">>> `DEX` - **O DEX aumenta sua chance de esquiva.**\n" \
                   ">>> `ACC` - **O ACC aumenta sua chance de acerto da Skill.**\n" \
                   ">>> `CON` - **O CON aumenta seu HP e sua MANA total.**\n" \
                   ">>> `LUK` - **LUK aumenta a chance de efeito da Skill e a chance de critico.**\n" \
                   "```Markdown\n[>>]: PARA ADICIONAR PONTOS DE HABILIDADE USE" \
                   " O COMANDO\n<ASH SKILL ADD>\n[>>]: PARA RESETAR OS PONTOS DE " \
                   "HABILIDADE USE O COMANDO\n<ASH SKILL RESET>```"

            again = False
            msg = None
            if not self.he[ctx.author.id][str(ctx.command)]:
                self.he[ctx.author.id][str(ctx.command)] = True
                while not self.bot.is_closed():
                    try:
                        def check(react, m):
                            try:
                                if react.message.id == self.botmsg[_id].id:
                                    if m.id == ctx.author.id:
                                        return True
                                return False
                            except AttributeError:
                                return False

                        reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

                        emo = "<a:help:767825933892583444>"
                        emoji = str(emo).replace('<a:', '').replace(emo[emo.rfind(':'):], '')
                        emo_2 = self.bot.config['emojis']['arrow'][4]
                        emoji_2 = str(emo_2).replace('<:', '').replace(emo_2[emo_2.rfind(':'):], '')

                        try:
                            try:
                                _reaction = reaction[0].emoji.name
                            except AttributeError:
                                _reaction = reaction[0].emoji

                            if _reaction == emoji and reaction[0].message.id == self.botmsg[_id].id and not again:
                                if reaction[1].id == ctx.author.id:
                                    again = True
                                    perms = ctx.channel.permissions_for(ctx.me)
                                    if perms.manage_messages:
                                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>",
                                                                               ctx.author)
                                    msg = await ctx.send(text)

                            elif _reaction == emoji and reaction[0].message.id == self.botmsg[_id].id and again:
                                if reaction[1].id == ctx.author.id:
                                    again = False
                                    perms = ctx.channel.permissions_for(ctx.me)
                                    if perms.manage_messages:
                                        await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>",
                                                                               ctx.author)
                                    await msg.delete()

                            if _reaction == emoji_2 and reaction[0].message.id == self.botmsg[_id].id:
                                if reaction[1].id == ctx.author.id:
                                    self.he[ctx.author.id][str(ctx.command)] = False
                                    perms = ctx.channel.permissions_for(ctx.me)
                                    if perms.manage_messages:
                                        await self.botmsg[_id].remove_reaction(
                                            self.bot.config['emojis']['arrow'][4], ctx.me)
                                        await self.botmsg[_id].remove_reaction(
                                            "<a:help:767825933892583444>", ctx.me)
                                    return

                        except AttributeError:
                            pass
                    except TimeoutError:
                        self.he[ctx.author.id][str(ctx.command)] = False
                        perms = ctx.channel.permissions_for(ctx.me)
                        if perms.manage_messages:
                            await self.botmsg[_id].remove_reaction(self.bot.config['emojis']['arrow'][4], ctx.me)
                            await self.botmsg[_id].remove_reaction("<a:help:767825933892583444>", ctx.me)
                        return

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @skill.command(name='add', aliases=['adicionar'])
    async def _add(self, ctx, status: str = None, n: int = 1):
        """Comando usado pra distribuir seus status no rpg da Ashley
        Use ash skill add e siga as instruções do comando"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if n < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")

        if not data['rpg']['active']:
            embed = disnake.Embed(
                color=self.bot.color,
                description='<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`')
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if status is None:
            return await ctx.send("<:negate:721581573396496464>│`Você precisa colocar o nome do atributo que deseja "
                                  "adicionar o ponto:` **ash skill add con 1**")

        if status.lower() not in ['con', 'atk', 'acc', 'dex', 'luk']:
            return await ctx.send('<:negate:721581573396496464>│`Não existe esse atributo!`')

        if status.lower() == "acc":
            status = "prec"
        if status.lower() == "dex":
            status = "agi"

        _class = update["rpg"]["class_now"]

        if update['rpg']["sub_class"][_class]['status']['pdh'] < 0:
            return await ctx.send('<:negate:721581573396496464>│`Você não tem pontos de habilidades disponiveis!`')
        if update['rpg']["sub_class"][_class]['status']['pdh'] < n:
            return await ctx.send(f'<:negate:721581573396496464>│`Você não {n} pontos de habilidades disponiveis!`')

        if status.lower() == "con" and update['rpg']["sub_class"][_class]['status']['con'] + n > 50:
            msg = '<:negate:721581573396496464>│`VOCE NAO PODE PASSAR DE 50 PONTOS NESSE ATRIBUTO`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if status.lower() == "prec" and update['rpg']["sub_class"][_class]['status']['prec'] + n > 50:
            msg = '<:negate:721581573396496464>│`VOCE NAO PODE PASSAR DE 50 PONTOS NESSE ATRIBUTO`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if status.lower() == "agi" and update['rpg']["sub_class"][_class]['status']['agi'] + n > 50:
            msg = '<:negate:721581573396496464>│`VOCE NAO PODE PASSAR DE 50 PONTOS NESSE ATRIBUTO`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if status.lower() == "atk" and update['rpg']["sub_class"][_class]['status']['atk'] + n > 50:
            msg = '<:negate:721581573396496464>│`VOCE NAO PODE PASSAR DE 50 PONTOS NESSE ATRIBUTO`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if status.lower() == "luk" and update['rpg']["sub_class"][_class]['status']['luk'] + n > 20:
            msg = '<:negate:721581573396496464>│`VOCE NAO PODE PASSAR DE 20 PONTOS NESSE ATRIBUTO`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        update['rpg']["sub_class"][_class]['status'][status.lower()] += n
        update['rpg']["sub_class"][_class]['status']['pdh'] -= n
        await self.bot.db.update_data(data, update, "users")

        if status.lower() == "prec":
            status = "acc"
        if status.lower() == "agi":
            status = "dex"

        await ctx.send(f'<:confirmed:721581574461587496>│`Ponto de Habilidade adicionado com sucesso em:` '
                       f'**{status.upper()}**')

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @skill.command(name='reset', aliases=['resetar'])
    async def _reset(self, ctx):
        """Comando usado pra resetar seus status
        Use ash skill reset"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if not data['rpg']['active']:
            msg = '<:negate:721581573396496464>│`USE O COMANDO` **ASH RPG** `ANTES!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        if ctx.author.id in self.bot.batalhando:
            msg = '<:negate:721581573396496464>│`VOCE ESTÁ BATALHANDO!`'
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

        _class = data["rpg"]["class_now"]
        _db_class = data["rpg"]["sub_class"][_class]

        update['rpg']["sub_class"][_class]['status']['con'] = 5
        update['rpg']["sub_class"][_class]['status']['prec'] = 5
        update['rpg']["sub_class"][_class]['status']['agi'] = 5
        update['rpg']["sub_class"][_class]['status']['atk'] = 5
        update['rpg']["sub_class"][_class]['status']['luk'] = 0
        update['rpg']["sub_class"][_class]['status']['pdh'] = _db_class['level']

        await self.bot.db.update_data(data, update, "users")
        await ctx.send('<:confirmed:721581574461587496>│`Status resetados com sucesso!`')


def setup(bot):
    bot.add_cog(SkillClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mSKILLCLASS\033[1;32m foi carregado com sucesso!\33[m')
