import discord

from discord.ext import commands


class MemberBanClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        data = await self.bot.db.get_data("guild_id", guild.id, "guilds")

        if not data:
            return

        try:
            if data['func_config']['cont_users']:
                numbers = ['<:0_:578615675182907402>', '<:1_:578615669487304704>', '<:2_:578615674109165568>',
                           '<:3_:578615683424976916>', '<:4_:578615679406833685>', '<:5_:578615684708171787>',
                           '<:6_:578617070309343281>', '<:7_:578615679041798144>', '<:8_:578617071521497088>',
                           '<:9_:578617070317469708>']
                canal = self.bot.get_channel(data['func_config']['cont_users_id'])
                if canal is None:
                    return
                text = str(len(guild.members))
                list_ = list()
                for letter in text:
                    list_.append(numbers[int(letter)])
                list_ = ''.join(list_)
                ashley = canal.guild.get_member(self.bot.user.id)
                perms = canal.permissions_for(ashley)
                if perms.send_messages and perms.read_messages:
                    if not perms.embed_links or not perms.attach_files:
                        await canal.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` "
                                         "**ADICIONAR LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR"
                                         " CORRETAMENTE!**")
                    else:
                        await canal.edit(topic="<a:caralho:525105064873033764> **Membros:**  " + list_)
        except discord.Forbidden:
            pass
        except discord.errors.NotFound:
            pass

        data = data["log_config"]

        if data['log'] and data['member_ban']:
            canal = self.bot.get_channel(data['log_channel_id'])

            if not canal:
                return

            embed = discord.Embed(color=self.color,
                                  title=":star2: **Membro Banido**",
                                  description=f"**Membro:** {user.name}")
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")

            ashley = canal.guild.get_member(self.bot.user.id)
            perms = canal.permissions_for(ashley)
            if perms.send_messages and perms.read_messages:
                if not perms.embed_links or not perms.attach_files:
                    await canal.send("<:negate:721581573396496464>│`PRECISO DA PERMISSÃO DE:` "
                                     "**ADICIONAR LINKS E DE ADICIONAR IMAGENS, PARA PODER FUNCIONAR"
                                     " CORRETAMENTE!**")
                else:
                    await canal.send(embed=embed)


def setup(bot):
    bot.add_cog(MemberBanClass(bot))
    print('\033[1;33m( 🔶 ) | O evento \033[1;34mMEMBER_BAN\033[1;33m foi carregado com sucesso!\33[m')
