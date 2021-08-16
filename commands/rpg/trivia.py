import discord

from discord.ext import commands
from resources.db import Database
from resources.check import check_it


class Trivias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='trivia', aliases=['tutorial', 't'])
    async def trivia(self, ctx):
        """comando usado pra enviar uma frase do pensador
        Use ash thinker"""
        msg = """
```markdown
[1]: Faça sua primeira batalha
<Comando: ash bt>

[2]: Olhe seu painel de skill (habilidades)
<Comando: ash skill>

[3]: Melhore seus atributos
<Comando: ash skill add atk 2>

[4]: Veja seu painel de Equipamentos
<Comando: ash e>

[5]: Use todos os comandos diarios disponiveis
<Comando: ash daily>

[6]: Jogue os mini-games:
# ash jkp; ash moeda; ash adivinhe; ash card;
# ash pokemon; ash forca; ash charada.

[7]: Compre fichas na loja de itens.
<Comando: ash shop 5 fichas>

[8]: Vote nos dois top que a ashley participa.
<Comando: ash vote>

[9]: Compre uma "algel stone" na loja da moeda do voto.
<Comando: ash sv 1 angel stone>

[10]: Olhe seu painel de encantamentos.
<Comando: ash enchant>

[11]: Melhore sua habilidade 5, encantando ela para +1
<Comando: ash enchant add 5>
```"""
        embed = discord.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Trivias(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mTRIVIAS\033[1;32m foi carregado com sucesso!\33[m')
