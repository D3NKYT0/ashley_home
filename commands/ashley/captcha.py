import discord

from discord.ext import commands
from resources.db import Database
from resources.check import check_it
from resources.utility import captcha as cap
from asyncio import TimeoutError


class CaptchaClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 30.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='captcha', aliases=['cap'])
    async def captcha(self, ctx):
        """comando pra verificar se você é humano
        Use ash captcha"""
        query_u = {"_id": 0, "user_id": 1, "security": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query_u)

        if not data_user["security"]["self_baned"]:
            return await ctx.send('<:alert:739251822920728708>│`Você nao precisa provar que é um humano!`')

        cap(data_user["security"]["captcha_code"])
        await ctx.send(file=discord.File('captcha.png'), content="> `DIGITE O CODIGO DA IMAGEM`")

        def check(m):
            return m.author.id == ctx.author.id

        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito pra responder:` '
                                  '**COMANDO CANCELADO**')

        if answer.content.upper() == data_user["security"]["captcha_code"].upper():
            query_user = {"$set": {}}
            query_user["$set"]["security.self_baned"] = False
            query_user["$set"]["security.captcha_code"] = None
            cl = await self.bot.db.cd("users")
            await cl.update_one({"user_id": data_user["user_id"]}, query_user)
            await ctx.send(f'<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention}'
                           f'`VOCÊ ACERTOU O CÓDIGO!` **AGORA PARE DE USAR MACRO OU SERÁ BANIDO DEFINITIVAMENTE!**')
        else:
            await ctx.send('<:negate:721581573396496464>│`O Código que você utilizou está errado!`')


def setup(bot):
    bot.add_cog(CaptchaClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mCAPTCHA\033[1;32m foi carregado com sucesso!\33[m')
