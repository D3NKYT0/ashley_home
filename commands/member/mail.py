from typing import ItemsView
import discord

from discord.ext import commands
from ast import literal_eval
from resources.check import check_it
from resources.db import Database
from resources.utility import paginator
from resources.img_edit import equips
from asyncio import sleep, TimeoutError
from resources.utility import create_id
from zlib import compress, decompress


class MailClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='mail', aliases=['email'])
    async def mail(self, ctx):
        if ctx.invoked_subcommand is None:
            mail = 0
            all_data = [data async for data in self.bot.mails.find()]
            mails = list()
            item_mails = dict()
            for data in all_data:
                if data['global'] == True and ctx.author.id not in data['received'] or ctx.author.id in data['benefited']:
                    mail += 1
                    for k, v in data.items():
                        if k == 'title':
                            mails.append(v)
                            item_mails[v] = data
                            item_mails[v]['_id'] = mail
                            
                elif ctx.author.id in data['received']:
                    mail += 1
                    for k, v in data.items():
                        if k == 'title':
                            mails.append(f"{v} [Lido]")
                            item_mails[f"{v} [Lido]"] = data
                            item_mails[f"{v} [Lido]"]['_id'] = mail
            
            if mail == 0:
                return await ctx.send(f"<:negate:721581573396496464>|`VOCÊ NÃO POSSUI NENHUM EMAIL.`")

            embed = [':e_mail: Caixa de e-mails:', self.bot.color, ""]
            await paginator(self.bot, item_mails, mails, embed, ctx, None)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @mail.command(name='read', aliases=['ler'])
    async def _readmail(self, ctx, *, id: str = None):
        id = id.upper() if id else None
        mails = list()
        item_mails = dict()
        items = list()
        mail = 0
        if id is None:
            return await ctx.send(f'<:negate:721581573396496464>|`VOCÊ PRECISA INSERIR UM ID DE EMAIL PARA EU LER')
        data_user = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update_user = data_user
        all_data = [data async for data in self.bot.mails.find()]
        for data in all_data:
            mail += 1
            original_id = data['_id']
            data['_id'] = str(mail)
            if id in data['_id']:
                if data['global'] is True and ctx.author.id not in data['received'] or ctx.author.id in data['benefited']:
                    for k, v in data.items():
                        if k == '_id':
                            item_mails[v] = data
                elif ctx.author.id in data['received']:
                    for k, v in data.items():
                        if k == '_id':
                            item_mails[v] = data
                    item_mails[id]['title'] = f"{item_mails[id]['title']} [Lido]"
                else:
                    return await ctx.send(f'<:negate:721581573396496464>|`VOCÊ NÃO POSSUI ESSE EMAIL`')

        embed = discord.Embed(title = item_mails[id]["title"], color=self.bot.color)
        embed.description = decompress(item_mails[id]["text"]).decode('utf-8')
        a = "\n"
        if len(item_mails[id]['gift']) > 0:
            for item in item_mails[id]['gift']:
                if item[0] in self.bot.items:
                    items.append(f'{self.bot.items[item[0]][0]} `{item[1]}` `{self.bot.items[item[0]][1]}`')
            embed.description += f'\n\n**__PRESENTES ANEXADOS:__**\n{a.join(items)}'

        issuer = await self.bot.fetch_user(item_mails[id]['issuer'])
        embed.set_footer(text=f'Enviado por: {issuer} | {original_id}', icon_url=issuer.avatar_url)
        message = await ctx.send(embed=embed)
        if item_mails[id]['global'] is True and ctx.author.id not in item_mails[id]['received'] or ctx.author.id in item_mails[id]['benefited']:
            await message.add_reaction('📬')    

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: u.id == ctx.author.id)
        except TimeoutError:
            return await message.delete()

        print(reaction.emoji)

        if reaction.emoji == '📬':
            await message.delete()
            loading = await ctx.send(f'<a:loading:520418506567843860>│`ADICIONANDO ITENS A SUA CONTA...`')
            await sleep(3)
            for data in all_data:
                if id in data['_id']:
                    if data['global'] is True and ctx.author.id not in data['received'] or ctx.author.id in data['benefited']:
                        if data['global'] is False:
                            data['benefited'].remove(ctx.author.id)
                        data['received'].append(ctx.author.id)
                        await self.bot.mails.update_one({"_id": original_id}, {"$set": {"received": data['received'], "benefited": data['benefited']}})
                        break
                    else:
                        return await loading.edit(content=f'<:negate:721581573396496464>│`VOCÊ JÁ RESGATOU OS PRESENTES DESSE EMAIL !!`')
            for item in item_mails[id]['gift']:
                if item[0] in self.bot.items:
                    try:
                        update_user['inventory'][item[0]] += item[1]
                    except KeyError:
                        update_user['inventory'][item[0]] = item[1]

            await self.bot.db.update_data(data_user, update_user, 'users')
            await loading.delete()
            embed = discord.Embed(title='🎊 VOCÊ PEGOU OS SEGUINTES ITENS ANEXADOS:', color=self.bot.color, description="\n".join(items))
            return await ctx.send(embed = embed)


    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @mail.command(name='create', aliases=['criar'])
    async def _createmail(self, ctx):
        asks = {'_id': None, 'issuer': ctx.author.id, 'title': None, 'text': None, 'gift': [], 'global': False, 'benefited': [], 'received': []}

        embed = discord.Embed(color=self.bot.color,
                              description=f"<a:blue:525032762256785409>|`QUAL O TITULO DO E-MAIL ?`"
                            )
        msg = await ctx.send(embed=embed)
        try:
            titulo = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if titulo.content.lower() == 'cancelar':
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        asks['title'] = titulo.content

        embed = discord.Embed(color=self.bot.color,
                              description=f"<a:blue:525032762256785409>|`QUAL O CONTEUDO DO E-MAIL ?`"
                            )

        msg = await ctx.send(embed=embed)

        try:
            text = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if text.content.lower() == 'cancelar':
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        asks['text'] = compress(bytes(text.content, encoding='utf-8'))

        embed = discord.Embed(color=self.bot.color,
                              description=f"<a:blue:525032762256785409>|`QUAL O ITEM QUE DESEJA ADICIONAR AO PRESENTE ?`"
                            )
        msg = await ctx.send(embed=embed)

        try:
            item = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if item.content.lower() == 'cancelar':
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        asks['gift'].append(literal_eval(item.content))

        embed = discord.Embed(color=self.bot.color,
                              description=f"<a:blue:525032762256785409>|`QUAL OS ID DOS USUARIOS QUE RECEBERAM O PRESENTE ?`"
                            )

        msg = await ctx.send(embed=embed)

        try:
            id = await self.bot.wait_for('message', timeout=60, check=lambda message: message.author == ctx.author)
        except TimeoutError:
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if id.content.lower() == 'cancelar':
            embed = discord.Embed(color=self.bot.color, description=f'<:negate:721581573396496464>│ Comando Cancelado')
            return await ctx.send(embed=embed)

        if id.content.lower() == 'global':
            asks['global'] = True
            asks['benefited'] = []
            asks['received'] = []
        else:
            id = id.content.split(', ')
            ids = []
            [ids.append(int(i)) for i in id]
            asks['benefited'] = ids

        asks['_id'] = create_id()
        await self.bot.mails.insert_one(asks)

        embed = discord.Embed(color=self.bot.color,
                              description=f"<:confirmed:721581574461587496>│`E-MAIL CRIADO COM SUCESSO !`"
                            )
        return await ctx.send(embed=embed)


    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @mail.command(name='delete', aliases=['excluir'])
    async def _deletemail(self, ctx, id: str):
        await self.bot.mails.delete_one({'_id': id})
        embed = discord.Embed(color=self.bot.color,
                              description=f"<:confirmed:721581574461587496>│`E-MAIL EXCLUIDO COM SUCESSO !`"
                            )
        return await ctx.send(embed=embed)    
        


def setup(bot):
    bot.add_cog(MailClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMAIL_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')