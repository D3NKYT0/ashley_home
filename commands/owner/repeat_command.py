import copy

from discord.ext import commands
from resources.check import check_it
from resources.db import Database


class RepeatCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True, is_owner=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='repeat_command', aliases=['rc'])
    async def repeat_command(self, ctx, times: int, *, command):
        """apenas desenvolvedores"""
        if times < 1:
            return await ctx.send("<:alert:739251822920728708>│`Você precisa dizer uma quantia maior que 0.`")
        msg = copy.copy(ctx.message)
        msg.content = command
        for i in range(times):
            await self.bot.process_commands(msg)


def setup(bot):
    bot.add_cog(RepeatCommand(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mREPEAT_COMMAND\033[1;32m foi carregado com sucesso!\33[m')
