import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from asyncio import TimeoutError
from random import choice
from datetime import datetime

git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class MarriedSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='marry', aliases=['casar', 'casamento'])
    async def marry(self, ctx, member: discord.Member = None):
        """Comando usado pra pedir alguem em casamento
        Use ash marry <@pessoa desejada>"""
        query = {"_id": 0, "user_id": 1, "user": 1, "ship": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        if data_user['user']['married']:
            return await ctx.send('<:alert:739251822920728708>│`VOCE JÁ ESTA CASADO(A)!`')

        if ctx.author.id in self.bot.casando:
            return await ctx.send('<:alert:739251822920728708>│`VOCÊ JÁ ESTÁ EM PROCESSO DE CASAMENTO!`')

        if member is None:
            return await ctx.send('<:alert:739251822920728708>│`VOCÊ PRECISA MENCIONAR ALGUEM.`')

        if member.id == ctx.author.id:
            return await ctx.send('<:alert:739251822920728708>│`VOCE NÃO PODE CASAR CONSIGO MESMO!`')

        query = {"_id": 0, "user_id": 1, "user": 1, "ship": 1}
        data_member = await (await self.bot.db.cd("users")).find_one({"user_id": member.id}, query)

        if data_member is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO**: `esse usuário não está cadastrado!` '
                                  '**Você so pode se casar com membros cadastrados!**', delete_after=5.0)

        if data_member['user']['married'] is True:
            return await ctx.send('<:alert:739251822920728708>│`ELE(A) JÁ ESTA CASADO(A)!`')

        if member.id in self.bot.casando:
            return await ctx.send(f'<:alert:739251822920728708>│{member.mention} `JÁ ESTÁ EM PROCESSO DE CASAMENTO!`')

        if str(member.id) not in data_user['ship'].keys():
            t1 = "Você"
            t2 = "use"
            return await ctx.send(f"<:alert:739251822920728708>│`{t1} ainda nao interagiu com essa pessoa, então não"
                                  f" tem` **ship** `com ela ainda, para ter ship {t2} os seguintes comandos:`\n```\n"
                                  f"ash dance\nash hug\nash kick\nash kiss\nash lick\nash punch\nash push\nash slap```")

        if str(ctx.author.id) not in data_member['ship'].keys():
            t1 = "Esse membro"
            t2 = "Ele deve usar"
            return await ctx.send(f"<:alert:739251822920728708>│`{t1} ainda nao interagiu com essa pessoa, então não"
                                  f" tem` **ship** `com ela ainda, para ter ship {t2} os seguintes comandos:`\n```\n"
                                  f"ash dance\nash hug\nash kick\nash kiss\nash lick\nash punch\nash push\nash slap```")

        if data_user['ship'][str(member.id)] <= 600:
            return await ctx.send(f'<:alert:739251822920728708>│{ctx.author.mention} `Voce precisa ter todos os '
                                  f'corações no comando:` **ash ship** `para casar com` {member.mention}')

        if data_member['ship'][str(ctx.author.id)] <= 600:
            return await ctx.send(f'<:alert:739251822920728708>│{member.mention} `Voce precisa ter todos os '
                                  f'corações no comando:` **ash ship** `para casar com` {ctx.author.mention}')

        self.bot.casando.append(ctx.author.id)
        self.bot.casando.append(member.id)

        await ctx.send(f'<a:vergonha:525105074398167061>│{member.mention}, `VOCÊ RECEBEU UM PEDIDO DE '
                       f'CASAMENTO DE` {ctx.author.mention} `DIGITE` **SIM** `OU` **NÃO**')

        def check(m):
            return m.author.id == member.id and m.content.upper() in ['SIM', 'NÃO', 'S', 'N', 'NAO', 'CLARO']

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)

        except TimeoutError:
            self.bot.casando.remove(ctx.author.id)
            self.bot.casando.remove(member.id)
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, ele(a) demorou muito pra responder:` '
                                  '**COMANDO CANCELADO**')

        if answer.content.upper() not in ['SIM', 'S', 'CLARO']:
            self.bot.casando.remove(ctx.author.id)
            self.bot.casando.remove(member.id)
            return await ctx.send(f'<:negate:721581573396496464>│{ctx.author.mention} `VOCE FOI REJEITADO...`')

        data_user['user']['married'] = True
        data_user['user']['married_at'] = member.id
        data_user['user']['married_in'] = datetime.today()

        data_member['user']['married'] = True
        data_member['user']['married_at'] = ctx.author.id
        data_member['user']['married_in'] = datetime.today()

        cl = await self.bot.db.cd("users")
        query = {"$set": {"user": data_user['user']}}
        await cl.update_one({"user_id": data_user["user_id"]}, query, upsert=False)

        cl = await self.bot.db.cd("users")
        query = {"$set": {"user": data_member['user']}}
        await cl.update_one({"user_id": data_member["user_id"]}, query, upsert=False)

        self.bot.casando.remove(ctx.author.id)
        self.bot.casando.remove(member.id)

        embed = discord.Embed(color=self.color)
        embed.set_image(url=choice(git))
        await ctx.send(embed=embed)
        await ctx.send(f"🎊 **PARABENS** 🎉 {ctx.author.mention} **e** {member.mention} **vocês estão casados!**")

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='divorce', aliases=['separar', 'separação', 'divorcio', 'separaçao', 'divorciar'])
    async def divorce(self, ctx):
        """Comando usado pra se divorciar
        Use ash divorce <@prostiranha em questão>"""

        query = {"_id": 0, "user_id": 1, "user": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)

        if not data_user['user']['married']:
            return await ctx.send('<:alert:739251822920728708>│`VOCE NÃO É CASADO(A)!`')

        date_old = data_user['user']['married_in']
        date_now = datetime.today()
        days = abs((date_old - date_now).days)
        if days < 7:
            d1 = date_old.strftime("%d-%m-%Y")
            msg = f"**Data de casamento:** `{d1}`\n" \
                  f"**Faz{'em' if days > 1 else ''}:** `{days} dia{'s' if days > 1 else ''}`\n" \
                  f"`Você deve esperar pelo menos` **7 dias** `para se separar!`"
            embed = discord.Embed(color=self.bot.color, description=msg)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            hour = datetime.now().strftime("%H:%M:%S")
            embed.set_footer(text="{} • {}".format(ctx.author, hour))
            return await ctx.send(embed=embed)

        member = self.bot.get_user(data_user['user']['married_at'])

        cl = await self.bot.db.cd("users")
        query = {"_id": 0, "user_id": 1, "user": 1}
        data_member = await cl.find_one({"user_id": data_user['user']['married_at']}, query)

        data_user['user']['married'] = False
        data_user['user']['married_at'] = None

        data_member['user']['married'] = False
        data_member['user']['married_at'] = None

        cl = await self.bot.db.cd("users")
        query = {"$set": {"user": data_user['user']}}
        await cl.update_one({"user_id": data_user["user_id"]}, query, upsert=False)

        cl = await self.bot.db.cd("users")
        query = {"$set": {"user": data_member['user']}}
        await cl.update_one({"user_id": data_member["user_id"]}, query, upsert=False)

        member = member.name if member is not None else "NINGUEM!"
        await ctx.send(f"😢 **QUE PENA** 😢 {ctx.author.mention} **e** {member} **estão SEPARADOS!**"
                       f" `ESCOLHAM MELHOR DA PROXIMA VEZ!`")


def setup(bot):
    bot.add_cog(MarriedSystem(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mMARRIED_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
