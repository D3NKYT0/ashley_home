import disnake

from disnake.ext import commands
from resources.check import check_it
from resources.db import Database


class WikiClass(commands.Cog):
    def __init__(self, bot):
        super(WikiClass, self).__init__()
        self.bot = bot
        self.color = self.bot.color

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='wiki', aliases=['pesquisar'])
    async def _wiki(self, ctx, *, item=None):
        """Comando com o catalogo de informações sobre o bot/rpg"""
        wiki, equip, file, emoji, tier = self.bot.config['wiki'], self.bot.config['equips'], None, None, ""

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        if item is not None:
            item = item.replace("_", " ").lower()
            if item in wiki.keys():
                wiki = wiki[item]
                desc, rare, how, typew = wiki['description'], wiki['rare'], wiki['how'], wiki['type']
                try:
                    why = wiki['why']
                except KeyError:
                    why = None
                try:
                    emoji = wiki['emoji']
                except KeyError:
                    pass
                img = wiki['image']
                item = f"{emoji} {item.title()}" if emoji is not None else item
                item = "exódia, o proibido" if item == "exodia" else item
                if rare == "Enchant":
                    srare = item.split()[-1]
                    if not srare == "Skill":
                        rare += f"\n**Tier:** {srare}"
                description = f'{item.title()}\n' \
                              f'\u200b\n' \
                              f'**Descrição**: {desc}\n' \
                              f'**Tipo**: {typew}\n' \
                              f'**Raridade**: {rare}\n' \
                              f'**Como adquirir**: {how}\n' \
                              f'{f"**Como usar**: {why}" if why is not None else ""}'
                embed = disnake.Embed(
                    title=f"Wikipedia",
                    color=self.bot.color,
                    description=description
                )
                embed.set_thumbnail(url="http://sisadm2.pjf.mg.gov.br/imagem/ajuda.png")
                embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                if img:
                    file = disnake.File(img, filename="image.png")
                    embed.set_image(url=f'attachment://image.png')
                await ctx.send(embed=embed, file=file)
            elif item in [i[1]["name"] for i in equips_list]:
                equip = [i[1] for i in equips_list if i[1]['name'] == item][0]
                modifier = equip['modifier']
                icon, name = equip['icon'], equip['name'].split()
                mdef, pdef = equip['mdef'], equip['pdef']
                con, prec, agi, atk = modifier['con'], modifier['prec'], modifier['agi'], modifier['atk']
                rare, classe = equip['rarity'], equip['class']
                if "silver" in name:
                    requisito = "11"
                elif "mystic" in name:
                    requisito = "21"
                elif "inspiron" in name:
                    requisito = "41"
                elif "violet" in name:
                    requisito = "61"
                else:
                    requisito = "80"

                if len(classe) > 1:
                    classe = ', '.join(classe)
                else:
                    classe = classe[0]
                if name[-1].startswith("+"):
                    tier = name[-2]
                elif name[-1].startswith("consumable"):
                    tier = name[-3]
                else:
                    tier = name[-1]
                description = f'{icon} {item.title()}\n' \
                              f'\u200b\n' \
                              f'**Classe(s)**: {classe.title()}\n' \
                              f'**Raridade**: {rare.title()} \n' \
                              f'**Tier**: {tier.title()}\n' \
                              f'**Requisito:** Level `{requisito}` ou maior\n' \
                              f'```Markdown\n' \
                              f'{"="*5} Defesa {"="*5}\n' \
                              f'MDEF:⠀⠀{mdef}⠀⠀PDEF:⠀⠀{pdef}\n' \
                              f'{"="*5} Status {"="*5}\n' \
                              f'ACC: {prec}\nCON: {con}\n' \
                              f'ATK: {atk}\nDEX: {agi}```'
                embed = disnake.Embed(
                    title=f"Wikipedia Equips",
                    color=self.bot.color,
                    description=description
                )
                embed.set_thumbnail(url="http://sisadm2.pjf.mg.gov.br/imagem/ajuda.png")
                embed.set_footer(text="Ashley ® Todos os direitos reservados.")
                await ctx.send(embed=embed)
            else:
                await ctx.send('<:negate:721581573396496464>|`DIGITE UM NOME DE UM ITEM OU EQUIPAMENTO VÁLIDO.`')
        else:
            await ctx.send('<:negate:721581573396496464>|`Digite um nome de um item ou equipamento.`')


def setup(bot):
    bot.add_cog(WikiClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mWIKI_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
