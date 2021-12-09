import ast
import disnake
import traceback
import import_expression

from io import BytesIO
from disnake.ext import commands
from resources.db import Database
from resources.check import check_it
from resources.utility import pretty

with open("data/auth.json") as security:
    _auth = disnake.utils.json.loads(security.read())


class View(disnake.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
    
    async def interaction_check(self, interaction):
        if interaction.author.id != self.author.id:
            return False
        else:
            return True

    @staticmethod
    async def close(inter):
        return await inter.message.delete()


class EvalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def insert_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

        if isinstance(body[-1], ast.For):
            self.insert_returns(body[-1].body)

        if isinstance(body[-1], ast.While):
            self.insert_returns(body[-1].body)

        if isinstance(body[-1], ast.Try):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].finalbody)
            self.insert_returns(body[-1].handlers)

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='eval')
    async def _eval(self, ctx, *, code: str):
        """Apenas Devs"""
        function = "_eval_function"
        view = View(ctx.author)
        button = disnake.ui.Button(emoji="<:negate:721581573396496464>", style=disnake.ButtonStyle.danger)
        button.callback = view.close
        view.add_item(button)

        if code.startswith('```py'):
            code = code[5:]
        elif code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        code = '\n'.join(f'    {i}' for i in code.splitlines())
        body = f'async def {function}():\n{code}'
        parsed = import_expression.parse(body)
        body = parsed.body[0].body
        self.insert_returns(body)
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'disnake': disnake,
            'commands': commands,
            'author': ctx.author,
            'channel': ctx.channel,
            'guild': ctx.guild,
            'message': ctx.message,
        }
        try:
            exec(import_expression.compile(parsed, filename="<ast>", mode="exec"), env)
            result = await import_expression.eval(f'{function}()', env)
        except Exception:
            error = str(traceback.format_exc())
            if len(error) > 2000:
                file = disnake.file(filename="error.py", fp=BytesIO(error.encode('utf-8')))
                await ctx.send(content="Error:", file=file, view=view, delete_after=120)
            else:
                embed = disnake.Embed(title="Error:", description=f"```py\n{error}```", colour=disnake.Colour.red())
                await ctx.send(embed=embed, view=view, delete_after=120)
        else:
            if result:
                result = pretty(result, auth=_auth)
                if len(result) > 2000:
                    await ctx.send(file=disnake.File(filename='result.py', fp=BytesIO(result.encode('utf-8'))),
                                   view=view, delete_after=120)
                else:
                    await ctx.send(f"```py\n{result}```", view=view, delete_after=120)


def setup(bot):
    bot.add_cog(EvalCog(bot))
