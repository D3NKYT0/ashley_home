import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database
from PIL import Image
from resources.img_edit import get_avatar


class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.command(name='ship', aliases=['s', 'chip'])
    async def ship(self, ctx, member_1: disnake.Member = None, member_2: disnake.Member = None):
        """Comando de Ship entre duas pessoas
        Use ash ship"""

        m1 = member_1
        m2 = member_2

        if member_1 is None:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa mencionar a primeira pessoa!`")

        if member_2 is None:

            if member_1.id != ctx.author.id:
                m1 = ctx.author
                m2 = member_1

            else:
                return await ctx.send("<:alert:739251822920728708>│`Você precisa mencionar uma segunda pessoa tambem!`")

        data = await self.bot.db.get_data("user_id", m1.id, "users")
        if data is None:
            return await ctx.send('<:alert:739251822920728708>│**ATENÇÃO** : '
                                  '`esse usuário não está cadastrado!`', delete_after=5.0)

        msg = await ctx.send("<a:loading:520418506567843860>│ `AGUARDE, ESTOU PROCESSANDO SEU PEDIDO!`")

        try:
            ship = data['ship'][str(m2.id)]
            if 10 <= ship <= 25:
                ship = 1
            elif 25 <= ship <= 50:
                ship = 2
            elif 50 <= ship <= 75:
                ship = 3
            elif 75 <= ship <= 100:
                ship = 4
            elif 100 <= ship <= 150:
                ship = 5
            elif 150 <= ship <= 200:
                ship = 6
            elif 200 <= ship <= 250:
                ship = 7
            elif 250 <= ship <= 300:
                ship = 8
            elif 300 <= ship <= 350:
                ship = 9
            elif 350 <= ship <= 400:
                ship = 10
            elif 400 <= ship <= 450:
                ship = 11
            elif 450 <= ship <= 500:
                ship = 12
            elif 500 <= ship <= 600:
                ship = 13
            elif ship > 600:
                ship = 14
            else:
                ship = 0
        except KeyError:
            await msg.delete()
            t1 = "Você" if m1.id == ctx.author.id else "Esse membro"
            t2 = "use" if m1.id == ctx.author.id else "Ele deve usar"
            return await ctx.send(f"<:alert:739251822920728708>│`{t1} ainda nao interagiu com essa pessoa, então não"
                                  f" tem` **ship** `com ela ainda, para ter ship {t2} os seguintes comandos:`\n```\n"
                                  f"ash dance\nash hug\nash kick\nash kiss\nash lick\nash punch\nash push\nash slap```")

        image = Image.open(f"images/ship/ship{ship}.png").convert('RGBA')

        avatar_1 = await get_avatar(m1.display_avatar.with_format("png"), 165, 165)
        image.paste(avatar_1, (42, 118), avatar_1)

        avatar_2 = await get_avatar(m2.display_avatar.with_format("png"), 165, 165)
        image.paste(avatar_2, (393, 118), avatar_2)

        image.save('ship.png')
        await msg.delete()
        await ctx.send(file=disnake.File('ship.png'))


def setup(bot):
    bot.add_cog(Ship(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mSHIP\033[1;32m foi carregado com sucesso!\33[m')
