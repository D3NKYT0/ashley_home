import disnake

from disnake.ext import commands
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
        """comando usado pra enviar uma lista de tarefas para os novatos no rpg da ASHLEY
        Use ash trivia"""
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

[12]: Olhe seu perfil
<Comando: ash perfil>

[13]: Obtenha seu primeiro artefato:
<Comando: ash rifa>

[14]: Olhe seu perfil novamente
<Comando: ash perfil>

[15]: Olhe sua carteira
<Comando: ash carteira>

[16]: Obtenha sua primeira pedra do selamento
<Comando: ash stone>

[17]: olhe o seu inventario de itens
<Comando: ash i>

[18]: Olhe a lista dos itens craftaveis
<Comando: ash recipe>

[19]: Crafte seu primeiro item
<Comando: ash craft>

[20]: chegue no level 11 do rpg
<Comando: ash bt>

[21]: olhe o seu inventario de equipamentos
<Comando: ash es>

[22]: Equipe sua armadura (esta no iventario de equipamentos)
<Comando: ash e i nome_do_item>

[23]: Olhe seu painel de equipamentos
<Comando: ash e>

[24]: Tenha sua primeira batalha com um BOSS
<Comandos: ash boss>

[25]: Para mais informações use:
<Comandos: ash help ; ash wiki nome_do_item>
```"""
        embed = disnake.Embed(color=self.bot.color, description=msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Trivias(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mTRIVIAS\033[1;32m foi carregado com sucesso!\33[m')
