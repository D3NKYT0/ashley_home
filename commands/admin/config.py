import disnake

from asyncio import sleep, TimeoutError
from disnake.ext import commands
from resources.check import check_it
from resources.utility import ERRORS
from resources.db import Database


class ConfigClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.st = []
        self.color = self.bot.color

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='config', aliases=['configuração'])
    async def config(self, ctx):
        """Comando usado pra configurar alguns settings da ashley
        Use ash config pra ver as configurações disponiveis"""
        if ctx.invoked_subcommand is None:
            self.status()
            top = disnake.Embed(color=self.color)
            top.add_field(name="Config Commands:",
                          value=f"{self.st[0]} `config action_log` Registra as ações do servidor.\n"
                                f"{self.st[0]} `config member_count` Exibe a quantidade de membros.\n"
                                f"{self.st[0]} `config level_up` Mostra quando um membro sobe de level.\n"
                                f"{self.st[0]} `config join_member` Mostra quando um membro entrou.\n"
                                f"{self.st[0]} `config remove_member` Mostra quando um membro saiu.\n"
                                f"{self.st[0]} `config draw_member` Sistema de sorteio da Ashley.\n"
                                f"{self.st[0]} `config interaction` Sistema de IA da Ashley.\n"
                                f"{self.st[0]} `config report` Canal de report para STAFF.\n")
            top.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            top.set_thumbnail(url=self.bot.user.display_avatar)
            top.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=top)

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='action_log', aliases=['al'])
    async def _action_log(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_channel(m):
            return m.author == ctx.author and m.channel_mentions[0].id

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o ActionLog?` \n'
                       '```O ActionLog serve para você verificar tudo o que ocorre no seu servidor atravez de'
                       ' um canal de registro de ações.```\n'
                       '**1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do ActionLog!`')
            try:
                resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            await msg.delete()
            await ctx.send('<:confirmed:721581574461587496>│`ActionLog ativado!`')
            update['log_config']["log"] = True
            update['log_config']["log_channel_id"] = resp_2.channel_mentions[0].id
        else:
            await ctx.send('<:confirmed:721581574461587496>│`ActionLog desativado!`')
            update['log_config']["log"] = False
            update['log_config']["log_channel_id"] = None
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='member_count', aliases=['mc'])
    async def _member_count(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_channel(m):
            return m.author == ctx.author and m.channel_mentions[0].id

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o Contador de membros?` \n'
                       '```O Contador de membros é um recurso onde a ashley edita um canal para mostrar '
                       'quantos membros existem em seu servidor, em tempo real.```\n'
                       '**1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do Contador de membros!`')
            try:
                resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            await msg.delete()

            try:
                numbers = ['<:0_:578615675182907402>', '<:1_:578615669487304704>', '<:2_:578615674109165568>',
                           '<:3_:578615683424976916>', '<:4_:578615679406833685>', '<:5_:578615684708171787>',
                           '<:6_:578617070309343281>', '<:7_:578615679041798144>', '<:8_:578617071521497088>',
                           '<:9_:578617070317469708>']
                channel_ = self.bot.get_channel(resp_2.channel_mentions[0].id)
                text = str(len(ctx.guild.members))
                list_ = list()
                for letter in text:
                    list_.append(numbers[int(letter)])
                await channel_.edit(topic="<a:caralho:525105064873033764> **Membros:** " + ''.join(list_))

                await ctx.send('<:confirmed:721581574461587496>│`Contador de membros ativado!`')
            except disnake.Forbidden:
                await ctx.send("<:negate:721581573396496464>│`Não tenho permissão para editar canais "
                               "nesse servidor!`", delete_after=5.0)

            update['func_config']["cont_users"] = True
            update['func_config']["cont_users_id"] = resp_2.channel_mentions[0].id
        else:
            await ctx.send('<:confirmed:721581574461587496>│`Contador de membros desativado!`')
            update['log_config']["log"] = False
            update['log_config']["log_channel_id"] = None
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='level_up', aliases=['lvl'])
    async def _level_up(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_channel(m):
            return m.author == ctx.author and m.channel_mentions[0].id

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o Registro de level up?` \n'
                       '```Esse recurso registra quando um membro sobre de level social na ashley```\n'
                       '**1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do Registro de Level up!`')
            try:
                resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            await msg.delete()
            await ctx.send('<:confirmed:721581574461587496>│`Registro de level up ativado!`')
            update['func_config']["level_up_channel"] = True
            update['func_config']["level_up_channel_id"] = resp_2.channel_mentions[0].id
        else:
            await ctx.send('<:confirmed:721581574461587496>│`Registro de level up desativado!`')
            update['func_config']["level_up_channel"] = False
            update['func_config']["level_up_channel_id"] = None
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='join_member', aliases=['jm'])
    async def _join_member(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_channel(m):
            return m.author == ctx.author and m.channel_mentions[0].id

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o Registro de entrada de '
                       'membros?` \n'
                       '```Esse recurso registra em um canal a entrada de novos membros, quando ele entrou, '
                       'etc```\n'
                       '**1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do Registro de Entrada de Membros!`')
            try:
                resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            await msg.delete()
            await ctx.send('<:confirmed:721581574461587496>│`Registro de Entrada de Membros ativado!`')
            update['func_config']["member_join"] = True
            update['func_config']["member_join_id"] = resp_2.channel_mentions[0].id
        else:
            await ctx.send('<:confirmed:721581574461587496>│`Registro de Entrada de Membros desativado!`')
            update['func_config']["member_join"] = False
            update['func_config']["member_join_id"] = None
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='remove_member', aliases=['rm'])
    async def _remove_member(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_channel(m):
            return m.author == ctx.author and m.channel_mentions[0].id

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o '
                       'Registro de Saida de membros?`\n'
                       '```Esse recurso registra em um canal a sainda de membros, quando ele saiu, '
                       'etc```\n'
                       ' **1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do Registro de Sainda de Membros!`')
            try:
                resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            await msg.delete()
            await ctx.send('<:confirmed:721581574461587496>│`Registro de Saida de Membros ativado!`')
            update['func_config']["member_remove"] = True
            update['func_config']["member_remove_id"] = resp_2.channel_mentions[0].id
        else:
            await ctx.send('<:confirmed:721581574461587496>│`Registro de Saida de Membros desativado!`')
            update['func_config']["member_remove"] = False
            update['func_config']["member_remove_id"] = None
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='draw_member', aliases=['dm'])
    async def _draw_member(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        def check_channel(m):
            return m.author == ctx.author and m.channel_mentions[0].id

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o Sorteio de Membros?` \n'
                       '```O Sorteio de Membros serve para escolher um dos seus membros para receber premios '
                       'da ashley, todo aqueles registrados em nossos sistemas vao ter muitas regalias.\n'
                       'OBS: essa função apenas entrará em vigor em servidores com 50 ou mais membros e 10 '
                       'ou mais membros cadastrados na ashley```\n'
                       '**1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do Sorteio de Membros!`')
            try:
                resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            await msg.delete()
            await ctx.send('<:confirmed:721581574461587496>│`Sorteio de Membros ativado!`')
            update['bot_config']["ash_draw"] = True
            update['bot_config']["ash_draw_id"] = resp_2.channel_mentions[0].id
        else:
            await ctx.send('<:confirmed:721581574461587496>│`Sorteio de Membros desativado!`')
            update['bot_config']["ash_draw"] = False
            update['bot_config']["ash_draw_id"] = None
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='interaction', aliases=['i'])
    async def _interaction(self, ctx):
        """Ativa ou desativa a função"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o meu '
                       'Serviço de Interação com Membros (SIM)?`\n'
                       '```Esse serviço ativa as minhas interações com Inteligencia Artifical,'
                       'meu sistema de perguntas e respostas alem de varias outras coisas legais e '
                       'divertidas que eu posso fazer.```\n'
                       ' **1** para `SIM` ou **0** para `NÃO`')

        try:
            resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
        if resp_1.content == '1':
            await ctx.send('<:confirmed:721581574461587496>│`Serviço de Interação com Membros ativado!`')
            update['ia_config']["auto_msg"] = True
        else:
            await ctx.send('<:confirmed:721581574461587496>│`Serviço de Interação com Membros desativado!`')
            update['ia_config']["auto_msg"] = False
        await self.bot.db.update_data(data, update, "guilds")
        msg = await ctx.send("<a:loading:520418506567843860>│`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")
        await sleep(2)
        await msg.delete()
        await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : `CONFIGURAÇÃO REALIZADA COM SUCESSO!`')

    @check_it(no_pm=True, manage_guild=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @config.command(name='report', aliases=['reportar'])
    async def _report(self, ctx):
        """Comando usado pra configurar o report da Ashley
        Use ash config report e siga as instruções do comando(use # pra marcar os canais)"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update = data
        if data is not None:
            values = list()
            await ctx.send('<:send:519896817320591385>│`PRECISO QUE VOCÊ RESPONDA A ALGUMAS PERGUNTAS!`',
                           delete_after=5.0)

            def check_option(m):
                return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

            def check_channel(m):
                return m.author == ctx.author and m.channel_mentions[0].id

            msg = await ctx.send('<a:blue:525032762256785409>│`Você deseja ativar o Report?` '
                                 '**1** para `SIM` ou **0** para `NÃO`')

            try:
                resp_1 = await self.bot.wait_for('message', check=check_option, timeout=30.0)
            except TimeoutError:
                return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
            values.append(resp_1.content)
            if resp_1.content == '1':
                await msg.delete()
                msg = await ctx.send('<a:blue:525032762256785409>│`Marque o canal do Report!`')

                try:
                    resp_2 = await self.bot.wait_for('message', check=check_channel, timeout=30.0)
                except TimeoutError:
                    return await ctx.send("<:negate:721581573396496464>│`Tempo esgotado, por favor tente novamente.`")
                values.append(resp_2.channel_mentions[0].id)
                await msg.delete()

                msg = await ctx.send('<:confirmed:721581574461587496>│`Report ativado!`')
                await sleep(2)
            else:
                values.append(-1)
            await msg.delete()

            keys = ['report', 'report_id']
            c = 0

            msg = await ctx.send("<a:loading:520418506567843860>│"
                                 "`AGUARDE, ESTOU PROCESSANDO SEU CADASTRO!`")

            for key in keys:
                if c % 2 == 0:
                    if c == 0:
                        update['func_config'][key] = bool(int(values[c]))
                    c += 1
                else:
                    if values[c] == -1:
                        if c == 1:
                            update['func_config'][key] = None
                    else:
                        if c == 1:
                            update['func_config'][key] = values[c]
                    c += 1

            await self.bot.db.update_data(data, update, "guilds")
            await sleep(2)
            await msg.delete()

            await ctx.send('<:confirmed:721581574461587496>│**PARABENS** : '
                           '`CONFIGURAÇÃO REALIZADA COM SUCESSO!`', delete_after=5.0)

    @_action_log.error
    async def _action_log_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[15]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')

    @_member_count.error
    async def _member_count_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[14]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')

    @_join_member.error
    async def _join_member_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[16]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')

    @_remove_member.error
    async def _remove_member_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[17]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')

    @_draw_member.error
    async def _draw_member_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[18]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')

    @_interaction.error
    async def _interaction_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[19]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')

    @_report.error
    async def _report_error(self, ctx, error):
        if error.__str__() in ERRORS[4]:
            return await ctx.send('<:negate:721581573396496464>│`Você não marcou um canal de texto:` '
                                  '**COMANDO CANCELADO**')
        if error.__str__() in ERRORS[7]:
            return await ctx.send('<:negate:721581573396496464>│`Você precisa de uma permissão especifica:` '
                                  '**manage_guild / Gerenciar Servidor**')


def setup(bot):
    bot.add_cog(ConfigClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mCONFIG\033[1;32m foi carregado com sucesso!\33[m')
