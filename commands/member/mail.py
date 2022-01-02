import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.utility import paginator
from asyncio import sleep, TimeoutError
from zlib import compress, decompress


class MailClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='mail', aliases=['email'])
    async def mail(self, ctx):
        """Sistema de Correios da ashley!"""
        if ctx.invoked_subcommand is None:
            mail = 0
            mail_collection = await self.bot.db.cd("mails")
            all_data = [data async for data in mail_collection.find()]
            data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            mails = list()
            item_mails = dict()
            for data in all_data:

                # verificação do mail
                if "active" in data.keys():
                    if not data["active"]:
                        continue

                try:
                    mail_user = data_user['mails'][data['_id']]
                except KeyError:
                    mail_user = None
                mail_guild = data_user["guild_id"] in data['guilds_benefited'] if data['guilds_benefited'] else None
                _bn = data['benefited']
                if data['global'] and not mail_user or ctx.author.id in _bn or mail_guild and not mail_user:
                    mail += 1
                    for k, v in data.items():
                        if k == 'title':
                            mails.append(v)
                            item_mails[v] = data
                            
                elif mail_user:
                    mail += 1
                    for k, v in data.items():
                        if k == 'title':
                            mails.append(f"{v} [Lido]")
                            item_mails[f"{v} [Lido]"] = data
            
            if mail == 0:
                return await ctx.send(f"<:negate:721581573396496464>|`VOCÊ NÃO POSSUI NENHUMA CORRESPONDÊNCIA.`")

            embed = [':e_mail: Caixa de correio:', self.bot.color, ""]
            await paginator(self.bot, item_mails, mails, embed, ctx, None)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @mail.command(name='read', aliases=['ler'])
    async def _read_mail(self, ctx, *, id_mail: str = None):
        """Leia suas correnpondecias, para ver os IDs olhe o comando 'ash mail' la tem uma lista!"""
        id_mail = id_mail.upper() if id_mail else None
        mails, item_mails, items, find_id = list(), dict(), list(), False
        if id_mail is None:
            msg = f'<:negate:721581573396496464>|`VOCÊ PRECISA INSERIR UM ID DE UMA CORRESPONDÊNCIA PARA VOCÊ LER`'
            return await ctx.send(msg)
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        mail_collection = await self.bot.db.cd("mails")
        data, mail_user, mail_guild = dict(), False, dict()
        all_data = [data async for data in mail_collection.find()]
        for d in all_data:
            data = d
            try:
                mail_user = data_user['mails'][data['_id']]
            except KeyError:
                mail_user = False
            mail_guild = data_user["guild_id"] in data['guilds_benefited'] if data['guilds_benefited'] else None
            _bn = data['benefited']
            if id_mail in data['_id']:
                find_id = True
                if data['global'] and not mail_user or ctx.author.id in _bn or mail_guild and not mail_user:
                    for k, v in data.items():
                        if k == '_id':
                            item_mails[v] = data
                    item_mails[id_mail]['status'] = True
                elif mail_guild or mail_user:
                    for k, v in data.items():
                        if k == '_id':
                            item_mails[v] = data
                    item_mails[id_mail]['title'] = f"{item_mails[id_mail]['title']} [Lido]"
                    item_mails[id_mail]['status'] = False
                else:
                    return await ctx.send(f'<:negate:721581573396496464>|`VOCÊ NÃO POSSUI ESSA CORRESPONDÊNCIA.`')

        if not find_id:
            return await ctx.send(f'<:negate:721581573396496464>|`ID INVALIDO!`')

        embed = disnake.Embed(title=item_mails[id_mail]["title"], color=self.bot.color)
        embed.description = decompress(item_mails[id_mail]["text"]).decode('utf-8')
        a = "\n"
        if item_mails[id_mail]['gift']:
            for item in item_mails[id_mail]['gift']:
                if item[0] in self.bot.items:
                    items.append(f'{self.bot.items[item[0]][0]} `{item[1]}` `{self.bot.items[item[0]][1]}`')
            embed.description += f'\n\n**__PRESENTES ANEXADOS:__**\n{a.join(items)}'

        issuer = await self.bot.fetch_user(item_mails[id_mail]['issuer'])
        embed.set_footer(text=f'Enviado por: {issuer} | {data["_id"]}', icon_url=issuer.display_avatar)
        message = await ctx.send(embed=embed)

        benefited = item_mails[id_mail]['benefited']
        if item_mails[id_mail]['global'] and not mail_user or ctx.author.id in benefited:
            if item_mails[id_mail]['status']:
                await message.add_reaction('📬')

        def check_reaction(react, member):
            try:
                if react.message.id == message.id:
                    if member.id == ctx.author.id:
                        return True
                return False
            except AttributeError:
                return False

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
        except TimeoutError:
            return await message.delete()

        if reaction.emoji == '📬' and item_mails[id_mail]['status']:
            await message.delete()
            loading = await ctx.send(f'<a:loading:520418506567843860>│`LENDO CORRESPONDÊNCIA...`')
            await sleep(3)
            if mail_user:
                return await loading.edit(content=f'<:negate:721581573396496464>│`VOCÊ JÁ LEU ESSA CORRESPONDÊNCIA !!`')
            for data in all_data:
                if id_mail in data['_id']:
                    _bn = data['benefited']
                    if data['global'] and not mail_user or ctx.author.id in _bn or mail_guild and not mail_user:
                        if not data['global']:
                            data['benefited'].remove(ctx.author.id)
                            record = {"$set": {"benefited": data['benefited']}}
                            await mail_collection.update_one({"_id": data['_id']}, record)
                        update_user['mails'][data['_id']] = True
                        await self.bot.db.update_data(data_user, update_user, 'users')
                        break
                    else:
                        msg = f'<:negate:721581573396496464>│`VOCÊ JÁ RESGATOU OS PRESENTES DESSA CORRESPONDÊNCIA !!`'
                        return await loading.edit(content=msg)
            if item_mails[id_mail]['gift']:
                await loading.edit(content=f'<a:loading:520418506567843860>│`ADICIONANDO ITENS A SUA CONTA...`')
                await sleep(3)
                for item in item_mails[id_mail]['gift']:
                    if item[0] in self.bot.items:
                        try:
                            update_user['inventory'][item[0]] += item[1]
                        except KeyError:
                            update_user['inventory'][item[0]] = item[1]

                await self.bot.db.update_data(data_user, update_user, 'users')
                msg = f"🎊 **VOCÊ PEGOU OS SEGUINTES ITENS ANEXADOS:**\n"
                msg += "\n".join(items)
            else:
                msg = f"🎊 **CORRESPONDÊNCIA LIDA COM SUCESSO !!**"
            await loading.delete()
            embed = disnake.Embed(title='📄 CORRESPONDÊNCIA', color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @mail.command(name='create', aliases=['criar'])
    async def _create_mail(self, ctx):
        """apenas para DEVS criarem uma correspondencia para os jogadores"""
        asks = {'_id': None, "active": True, 'issuer': ctx.author.id, 'title': None, 'text': None, 'gift': None,
                'global': False, 'benefited': [], 'guilds_benefited': []}

        msg = f"<a:blue:525032762256785409>|`QUAL O TITULO DO E-MAIL ?`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)
        try:
            tittle = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if tittle.content.lower() == 'cancelar':
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        asks['title'] = tittle.content
        msg = f"<a:blue:525032762256785409>|`QUAL O CONTEUDO DO E-MAIL ?`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

        try:
            text = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if text.content.lower() == 'cancelar':
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        asks['text'] = compress(bytes(text.content, encoding='utf-8'))

        msg = f"<a:blue:525032762256785409>|`QUAL O ITEM QUE DESEJA ADICIONAR AO PRESENTE ?`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

        try:
            item = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if item.content.lower() == 'cancelar':
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if item.content.lower() in ['nenhum', 'nada']:
            asks['gift'] = False
        else:
            asks['gift'] = eval(item.content)

        msg = f"<a:blue:525032762256785409>|`QUAL OS ID DOS USUARIOS QUE RECEBERÃO O PRESENTE ?`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

        try:
            resp = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if resp.content.lower() == 'cancelar':
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if resp.content.lower() == 'global':
            asks['global'] = True
            asks['benefited'] = []
        else:
            resp = resp.content.split(', ')
            ids = []
            for i in resp:
                try:
                    ids.append(int(i))
                except ValueError:
                    _msg = f'<:negate:721581573396496464>│ Comando Cancelado\n' \
                           f'`use: global ou os IDs dos membros separados por virgula`'
                    embed = disnake.Embed(color=self.bot.color, description=_msg)
                    return await ctx.send(embed=embed)
            asks['benefited'] = ids

        msg = f"<a:blue:525032762256785409>|`QUAL OS ID DOS SERVIDORES QUE RECEBERÃO O PRESENTE ?`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)

        try:
            resp = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if resp.content.lower() == 'cancelar':
            embed = disnake.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if resp.content.lower() == 'global':
            asks['guilds_benefited'] = list()
        else:
            resp = resp.content.split(', ')
            ids = []
            for i in resp:
                try:
                    ids.append(int(i))
                except ValueError:
                    _msg = f'<:negate:721581573396496464>│ Comando Cancelado\n' \
                           f'`use: global ou os IDs das guildas separados por virgula`'
                    embed = disnake.Embed(color=self.bot.color, description=_msg)
                    return await ctx.send(embed=embed)
            asks['guilds_benefited'] = ids

        mail_collection = await self.bot.db.cd("mails")
        _id = await mail_collection.count_documents({}) + 1
        asks["_id"] = str(_id)
        await mail_collection.insert_one(asks)

        msg = f"<:confirmed:721581574461587496>│`E-MAIL CRIADO COM SUCESSO !`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        return await ctx.send(embed=embed)

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @mail.command(name='delete', aliases=['excluir'])
    async def _delete_mail(self, ctx, id_mail: str):
        """Apenas para DEVs desativarem uma correspondencia criada!"""
        mail_collection = await self.bot.db.cd("mails")
        data = await mail_collection.find_one({'_id': id_mail.upper()})
        if data is None:
            msg = f"<:confirmed:721581574461587496>│`ID INVALIDO`"
            embed = disnake.Embed(color=self.bot.color, description=msg)
            return await ctx.send(embed=embed)
        await mail_collection.update_one({'_id': id_mail.upper()}, {"$set": {"active": False}})
        msg = f"<:confirmed:721581574461587496>│`E-MAIL DESABILITADO COM SUCESSO!`"
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MailClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMAIL_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
