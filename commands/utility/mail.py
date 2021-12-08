import disnake

from disnake.ext import commands
from resources.check import check_it

mail_now = list()


class View(disnake.ui.View):

    def __init__(self, mail, cor):
        self.mail = mail
        self.cor = cor
        self.title = ""
        self.text = ""

    options_list = [disnake.SelectOption(label=data["title"]) for data in mail_now]

    @disnake.ui.select(placeholder="Seus Mails", options=options_list)
    async def callback(self, select, interaction):
        for m in self.mail:
            if m["title"] == select.label[0]:
                self.title = m["title"]
                self.text = m["text"]
        await interaction.response.send_message(embed=disnake.Embed(
            color=self.cor,
            description=f"Mail: " + self.title + "\n" + self.text
        ))


class Mail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @check_it(no_pm=True, is_owner=True)
    @commands.command(name="mail")
    async def _mail(self, ctx):
        global mail_now
        data = await self.bot.db.get_all_data("mails")
        mail = list()
        if len(data) > 0:
            for key in data:
                if ctx.author.id in key['benefited']:
                    mail.append(key)

        mail_now = mail
        await ctx.send("ok", view=View(mail, self.bot.color))


def setup(bot):
    bot.add_cog(Mail(bot))
