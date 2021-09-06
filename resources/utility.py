import discord
import operator
import datetime

from pytz import timezone
from config import data as config
from random import choice
from asyncio import TimeoutError
from captcha.image import ImageCaptcha

responses = config['answers']
questions = config['questions']
color_embed = None
legend = {"-": -1, "Comum": 0, "Incomum": 1, "Raro": 2, "Super Raro": 3, "Ultra Raro": 4, "Secret": 5, "Legendary": 6,
          "Heroic": 7, "Divine": 8, "Sealed": 9, "For Pet": 10, "God": 11, "Event": 12, "Enchant": 13, "Quest": 14}


def include(string_, list_):
    if isinstance(string_, list):
        test = list(set(string_).intersection(list_))
        if test == string_:
            return True
    else:
        for i in list_:
            if i.lower() in string_.lower():
                return True
    return False


def rank_definition(data):
    tot_rank = 0
    try:
        tot_rank += data['user']['level'] * 10000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['treasure']['money'] // 1000000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['treasure']['bronze'] // 10000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['treasure']['silver'] // 5000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['treasure']['gold'] // 1000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['config']['points'] * 10
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['user']['commands'] * 500
    except ZeroDivisionError:
        pass
    for cl in data['rpg']["sub_class"].keys():
        try:
            tot_rank += data['rpg']["sub_class"][cl]['level'] * 20000
        except ZeroDivisionError:
            pass
    try:
        tot_rank += data['user']['raid'] * 10000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['inventory']['medal'] * 1000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['inventory']['rank_point'] * 500
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['user']['patent'] * 10000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['user']['stars'] * 5000
    except ZeroDivisionError:
        pass
    try:
        tot_rank += data['user']['rec'] * 2000
    except ZeroDivisionError:
        pass
    return tot_rank


def base36encode(number):
    base36, sign, alphabet = str(), str(), '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36


def create_id():
    actual_datetime = datetime.datetime.now()
    actual_datetime = actual_datetime.strftime("1%d%m%y%H%M%S%f")
    return base36encode(int(actual_datetime))


def CreateCaptcha():
    actual_datetime = datetime.datetime.now()
    actual_datetime = actual_datetime.strftime("1%M%S%f")
    return base36encode(int(actual_datetime))


def captcha(_captcha):
    image = ImageCaptcha(fonts=['fonts/arial.ttf', 'fonts/arial.ttf'])
    image.generate(_captcha)
    image.write(_captcha, 'captcha.png')


def get_content(content):
    answer = content.replace("`", "[censored]").replace("*", "[censored]").replace("_", "[censored]") \
        .replace("~", "[censored]").replace("@", "[censored]").replace("here", "[censored]") \
        .replace("everyone", "[censored]").replace("ash ", "[censored]").replace("ash.", "[censored]")
    return answer


def choice_etherny():
    list_amount = {"yellow": 75, "purple": 20, "black": 5}
    list_items = []
    for i_, amount in list_amount.items():
        list_items += [i_] * amount
    answer = choice(list_items)
    return answer


def quant_etherny(amount):
    answer = {"amount": 0, "list": [0, 0, 0]}
    for _ in range(amount):
        etherny = choice_etherny()
        if etherny == "yellow":
            answer['amount'] += 1
            answer['list'][0] += 1
        elif etherny == "purple":
            answer['amount'] += 10
            answer['list'][1] += 1
        else:
            answer['amount'] += 100
            answer['list'][2] += 1
    return answer


def embed_creator(description, img_url, monster, hp_max, hp, monster_img, monster_name):
    global color_embed
    color = [0xff0000, 0xffcc00, 0x00cc00]
    if monster:
        color_embed = 0xf15a02
    else:
        color_value = int(hp / (hp_max / 100))
        checkpoints = [0, 31, 71]
        for c in range(0, 3):
            if color_value >= checkpoints[c]:
                color_embed = color[c]
    embed = discord.Embed(
        description=description,
        color=color_embed
    )
    if img_url is not None:
        embed.set_thumbnail(url=img_url)
    embed.set_author(name=monster_name, icon_url=monster_img)
    return embed


def patent_calculator(rank_point, medal):
    amount_rp = 200
    amount_medal = 0
    count_medal = 0
    count_patent = 1
    patent = 0
    if 100 < rank_point < 200:
        patent += 1
    elif rank_point >= 200:
        while True:
            if rank_point >= amount_rp and medal >= amount_medal:
                amount_medal += count_medal
                amount_rp += 100
                count_medal += 1
                count_patent += 1
            else:
                patent = count_patent
                if patent >= 30:
                    patent = 30
                break
    return patent


def convert_item_name(item, db_items):
    for key in db_items.keys():
        if item.lower() in ['ficha', 'medalha', 'rank point']:
            item += "s"
        if item.lower() == db_items[key][1].lower():
            return key
    return None


async def paginator(bot, items, inventory, embed, ctx, page=None, equips=None):
    descriptions = []
    cont = 0
    cont_i = 0
    description = ''
    jewel = ['101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115',
             '116', '117', '188']
    soulshots = ['soushot_platinum_silver', 'soushot_platinum_mystic', 'soushot_platinum_inspiron',
                 'soushot_platinum_violet', 'soushot_platinum_hero', 'soushot_leather_silver',
                 'soushot_leather_mystic', 'soushot_leather_inspiron', 'soushot_leather_violet',
                 'soushot_leather_hero', 'soushot_cover_silver', 'soushot_cover_mystic',
                 'soushot_cover_inspiron', 'soushot_cover_violet', 'soushot_cover_hero',
                 'soushot_leather_divine', 'soushot_platinum_divine', 'soushot_cover_divine']
    cons = ['summon_box_sr', 'summon_box_ur', 'summon_box_secret']
    shield = ["01", "02", "03", "001", "002", "003", "005", "006", "007", "008", "010", "011", "012", "013", "015",
              "1D", "2C", "3B", "4A", "5S", "6R", "016", "017", "018"]

    if str(ctx.command) == "inventory":
        dict_ = dict()
        for _ in inventory.keys():
            dict_[_] = items[_][3]
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        list_i = [sorted_x[x][0] for x in range(len(inventory.keys()))]

    elif str(ctx.command) == "merchant" or str(ctx.command) == "merc list":
        list_i = inventory

    elif str(ctx.command) in ["shop", "shopping", "shop_vote"]:
        list_i = inventory

    elif str(ctx.command) == "equips":
        dict_ = dict()
        for _ in inventory.keys():
            if _ in cons:
                dict_[_] = items[_]['rarity']
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        consumable = [sorted_x[x][0] for x in range(len(dict_.keys()))]

        dict_ = dict()
        for _ in inventory.keys():
            if _ in soulshots:
                dict_[_] = items[_]['rarity']
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        soulshot = [sorted_x[x][0] for x in range(len(dict_.keys()))]

        dict_ = dict()
        for _ in inventory.keys():
            if _ in shield:
                dict_[_] = items[_]['rarity']
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        shield = [sorted_x[x][0] for x in range(len(dict_.keys()))]

        dict_ = dict()
        for _ in inventory.keys():
            if _ in jewel:
                dict_[_] = items[_]['rarity']
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        jewel = [sorted_x[x][0] for x in range(len(dict_.keys()))]

        dict_ = dict()
        for _ in inventory.keys():
            try:
                test = int(_)
            except ValueError:
                test = 0
            if _ not in shield and _ not in jewel and test == 0 and _ not in cons and _ not in soulshots:
                dict_[_] = items[_]['rarity']
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        weapon = [sorted_x[x][0] for x in range(len(dict_.keys()))]

        dict_ = dict()
        for _ in inventory.keys():
            try:
                test = int(_)
            except ValueError:
                test = 0
            if _ not in shield and _ not in jewel and test != 0 and _ not in cons and _ not in soulshots:
                dict_[_] = items[_]['rarity']
        sorted_x = sorted(dict_.items(), key=operator.itemgetter(1), reverse=False)
        armor = [sorted_x[x][0] for x in range(len(dict_.keys()))]

        list_i = consumable + soulshot + shield + jewel + weapon + armor

    else:
        list_i = inventory.keys()

    for key in list_i:
        if cont == 0:
            description = embed[2]

        if str(ctx.command) == "inventory":
            try:
                rarity = list(legend.keys())[list(legend.values()).index(items[key][3])]
                string = f'{items[key][0]} `{inventory[key]}{("⠀" * (5 - len(str(inventory[key]))))}` ' \
                         f'`{items[key][1]}{(" " * (30 - len(items[key][1])))}` **{rarity.lower()}**\n'
            except KeyError:
                string = f"<:negate:721581573396496464> `{key.upper()}: ITEM NÃO ENCONTRADO!`"

        elif str(ctx.command) == "shop":
            string = f"[>>]: {key.upper()}\n<1 UND = {list_i[key]} ETHERNYAS>\n\n"

        elif str(ctx.command) == "shopping":
            string = f"[>>]: {key.upper()}\n<1 UND = {list_i[key]} BLESSED ETHERNYAS>\n\n"

        elif str(ctx.command) == "shop_vote":
            string = f"[>>]: {key.upper()}\n<1 UND = {list_i[key]} VOTE COINS>\n\n"

        elif str(ctx.command) == "merchant" or str(ctx.command) == "merc list":
            a = '{:,.2f}'.format(float(key['value']))
            b = a.replace(',', 'v')
            c = b.replace('.', ',')
            d = c.replace('v', '.')

            if key['type'] == "craft":
                item_now = bot.items[key["item"]]
                icon, name = item_now[0], item_now[1]

            else:
                item_now = [i[1] for i in items if i[0] == key["item"]]
                icon, name = item_now[0]["icon"], item_now[0]["name"]

            string = f'`{key["_id"]}` **-** {icon} **{key["amount"]}** `{name.upper()}\n' \
                     f'PREÇO DA UND:` **R$ {d}**\n\n'

        elif str(ctx.command) == "equips":
            rarity = items[key]['rarity']
            string = f'{items[key]["icon"]} `{inventory[key]}{("⠀" * (5 - len(str(inventory[key]))))}` ' \
                     f'`{items[key]["name"]}{(" " * (35 - len(items[key]["name"])))}` **{rarity.lower()}**\n'

        else:
            if inventory[key]['type'] == "etc_item":
                icon = inventory[key]['reward'][0][0]
                string = f"{items[icon][0]} **{key.upper()}**\n\n"
            else:
                icon = inventory[key]['reward'][0][0]
                string = f"{equips[icon]['icon']} **{equips[icon]['name'].upper().replace(' ', '_')}**\n\n"

        cont += len(string)
        if cont <= 1500 and cont_i < 20:
            if str(ctx.command) in ["shop", "shopping", "shop_vote"]:
                string = "```Markdown\n" + string + "```"
            description += string
            cont_i += 1

        else:
            if str(ctx.command) in ["shop", "shopping", "shop_vote"]:
                string = "```Markdown\n" + string + "```"
            descriptions.append(description)
            description = f'{embed[2]}{string}'
            cont = len(description)
            cont_i = 0

    descriptions.append(description)
    cont = 0
    emojis = bot.config['emojis']['arrow']

    msg = await ctx.send('<:alert:739251822920728708>│`Aguarde...`')
    if page is None:
        for c in emojis:
            await msg.add_reaction(c)

    while not bot.is_closed():

        if page is not None:
            if (page + 1) > len(descriptions):
                cont = len(descriptions) - 1
            elif page < 0:
                cont = 0
            else:
                cont = page

        Embed = discord.Embed(
            title=embed[0],
            color=embed[1],
            description=descriptions[cont]
        )
        Embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        Embed.set_thumbnail(url="{}".format(ctx.author.avatar_url))
        Embed.set_footer(text="Ashley ® Todos os direitos reservados.  [Pag {}/{}]".format(cont + 1, len(descriptions)))

        if page is None:
            await msg.edit(embed=Embed, content='')
        else:
            try:
                await msg.delete()
            except discord.errors.NotFound:
                pass
            await ctx.send(embed=Embed)

        if page is None:

            def check(react, member):
                try:
                    if react.message.id == msg.id:
                        if member.id == ctx.author.id:
                            return True
                    return False
                except AttributeError:
                    return False

            try:
                reaction = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            except TimeoutError:
                break

            try:
                emoji = str(emojis[0]).replace('<:', '').replace(emojis[0][emojis[0].rfind(':'):], '')
                try:
                    _reaction = reaction[0].emoji.name
                except AttributeError:
                    _reaction = reaction[0].emoji
                if _reaction == emoji and reaction[0].message.id == msg.id:
                    cont = 0

                emoji = str(emojis[1]).replace('<:', '').replace(emojis[1][emojis[1].rfind(':'):], '')
                try:
                    _reaction = reaction[0].emoji.name
                except AttributeError:
                    _reaction = reaction[0].emoji
                if _reaction == emoji and reaction[0].message.id == msg.id:
                    cont -= 1
                    if cont < 0:
                        cont = 0

                emoji = str(emojis[2]).replace('<:', '').replace(emojis[2][emojis[2].rfind(':'):], '')
                try:
                    _reaction = reaction[0].emoji.name
                except AttributeError:
                    _reaction = reaction[0].emoji
                if _reaction == emoji and reaction[0].message.id == msg.id:
                    cont += 1
                    if cont > len(descriptions) - 1:
                        cont = len(descriptions) - 1

                emoji = str(emojis[3]).replace('<:', '').replace(emojis[3][emojis[3].rfind(':'):], '')
                try:
                    _reaction = reaction[0].emoji.name
                except AttributeError:
                    _reaction = reaction[0].emoji
                if _reaction == emoji and reaction[0].message.id == msg.id:
                    cont = len(descriptions) - 1

                emoji = str(emojis[4]).replace('<:', '').replace(emojis[4][emojis[4].rfind(':'):], '')
                try:
                    _reaction = reaction[0].emoji.name
                except AttributeError:
                    _reaction = reaction[0].emoji
                if _reaction == emoji and reaction[0].message.id == msg.id:
                    break
            except AttributeError:
                break
        else:
            break
    if page is None:
        await msg.delete()


async def get_response(message):
    if len(message.content) > 10:
        if include(message.content, ['denky', 'pai', 'criador']):
            if message.author.id != 300592580381376513:
                response = choice(responses['denky_f'])
                return response
            else:
                return "Eu não consigo falar nada contra o senhor!"
        if include(message.content, questions['denky_r']) and include(message.content, ['ashley', 'ash']):
            response = choice(responses['resposta_ashley'])
            return response
        for c in range(0, len(questions['perg_pq'])):
            if questions['perg_pq'][c] in message.content.lower():
                response = choice(responses['resposta_pq'])
                return response
        for c in range(0, len(questions['perg_qual'])):
            if questions['perg_qual'][c] in message.content.lower():
                if questions['perg_qual'][c] == "quando":
                    response = choice(responses['resposta_quando'])
                    return response
                elif questions['perg_qual'][c] == "como":
                    response = choice(responses['resposta_como'])
                    return response
                elif questions['perg_qual'][c] == "onde":
                    response = choice(responses['resposta_onde'])
                    return response
                elif questions['perg_qual'][c] == "vamos":
                    response = choice(responses['resposta_vamos'])
                    return response
                elif questions['perg_qual'][c] == "qual":
                    response = choice(responses['resposta_qual'])
                    return response
                elif questions['perg_qual'][c] == "quanto":
                    response = choice(responses['resposta_quanto'])
                    return response
                elif questions['perg_qual'][c] == "quem":
                    response = choice(responses['resposta_quem'])
                    return response
                elif questions['perg_qual'][c] == "quer":
                    response = choice(responses['resposta_quer'])
                    return response
                elif questions['perg_qual'][c] == "o que" or questions['perg_qual'][c] == "oq":
                    response = choice(responses['resposta_o_que'])
                    return response
                elif questions['perg_qual'][c] == "posso":
                    response = choice(responses['resposta_posso'])
                    return response
                else:
                    response = choice(responses['resposta_outras'])
                    return response
        if ' ou ' in message.content.lower():
            response = choice(responses['resposta_ou'])
            return response
    response = choice(responses['resposta_comum'])
    return response


def parse_duration(duration: int, vip=False):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    duration = []
    if days > 0:
        if days > 1:
            duration.append(f'{days} dias')
        else:
            duration.append(f'{days} dia')
    if hours > 0:
        if hours > 1:
            duration.append(f'{hours} horas')
        else:
            duration.append(f'{hours} hora')
    if minutes > 0:
        if minutes > 1:
            duration.append(f'{minutes} minutos')
        else:
            duration.append(f'{minutes} minuto')
    if not vip:
        if seconds > 0:
            if seconds > 1:
                duration.append(f'{seconds} segundos')
            else:
                duration.append(f'{seconds} segundo')
    return ', '.join(duration)


async def guild_info(guild):
    afk = guild.afk_channel.name if guild.afk_channel else "Sem canal de AFK"

    verification_level = {
        "none": "Nenhuma",
        "low": "Baixo: Precisa ter um e-mail verificado na conta do Discord.",
        "medium": "Médio: Precisa ter uma conta no Discord há mais de 5 minutos.",
        "high": "Alta: Também precisa ser um membro deste servidor há mais de 10 minutos.",
        "table_flip": "Alta: Precisa ser um membro deste servidor há mais de 10 minutos.",
        "extreme": "Extrema: Precisa ter um telefone verificado na conta do Discord.",
        "double_table_flip": "Extrema: Precisa ter um telefone verificado na conta do Discord."
    }

    verification = verification_level.get(str(guild.verification_level))
    embed = discord.Embed(color=int("ff00c1", 16), description="Abaixo está as informaçoes principais do servidor!")
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Nome:", value=guild.name, inline=True)
    embed.add_field(name="Dono:", value=f"{str(guild.owner)}")
    embed.add_field(name="ID:", value=guild.id, inline=True)
    embed.add_field(name="Cargos:", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Membros:", value=str(len(guild.members)), inline=True)
    embed.add_field(name="Canais de Texto", value=f'{len(guild.text_channels)}', inline=True)
    embed.add_field(name="Canais de Voz", value=f"{len(guild.voice_channels)}", inline=True)
    embed.add_field(name="Canal de AFK", value=str(afk), inline=True)
    embed.add_field(name="Bots:", value=str(len([a for a in guild.members if a.bot])), inline=True)
    embed.add_field(name="Nível de verificação", value=f"{verification}", inline=True)
    embed.add_field(name="Criado em:", value=guild.created_at.strftime("%d %b %Y %H:%M"), inline=True)
    embed.add_field(name="Região:", value=str(guild.region).title(), inline=True)
    return embed


def date_format(date):
    date_timezone = timezone("America/Recife")
    date_ = date.astimezone(date_timezone)
    return date_.strftime("%d/%m/%Y %H:%M")


PROVINCES = [542406551923720202,
             542406630218661929,
             542406759017611275,
             542406909278420992,
             542406979151462430,
             542407056339238922,
             542407122558779404,
             542407283750076514,
             542407345750278164,
             542407416768233530]

ERRORS = ['The check functions for command staff ban failed.',  # 0
          'The check functions for command staff kick failed.',  # 1
          'The check functions for command staff language failed.',  # 2
          'The check functions for command staff limpar failed.',  # 3
          'Command raised an exception: IndexError: list index out of range',  # 4
          'Command raised an exception: TimeoutError: ',  # 5
          'The check functions for command config guild failed.',  # 6
          'The check functions for command config report failed.',  # 7
          'The check functions for command staff slowmode failed.',  # 8
          'The check functions for command staff delete failed.',  # 9
          'The check functions for command logger failed.',  # 10
          'The check functions for command guild convert failed.',  # 11
          'The check functions for command source failed.',  # 12
          'The check functions for command register guild failed.',  # 13
          'The check functions for command config member_count failed.',  # 14
          'The check functions for command config action_log failed.',  # 15
          'The check functions for command config join_member failed.',  # 16
          'The check functions for command config remove_member failed.',  # 17
          'The check functions for command config draw_member failed.',  # 18
          'The check functions for command config interaction failed.']  # 19

enforcado = ['''
```
X==:== 
X  :   
X   
X  
X  
X  
===========
```''', '''
```
X==:== 
X  :   
X  O   
X  
X  
X  
===========
```''', '''
```
X==:== 
X  :   
X  O   
X  | 
X  
X  
===========
```''', '''
```
X==:== 
X  :   
X  O   
X \| 
X 
X 
===========
```''', '''
```
X==:== 
X  :   
X  O   
X \|/ 
X  
X  
===========
```''', '''
```
X==:== 
X  :   
X  O   
X \|/ 
X /  
X  
===========
```
''', '''
```
X==:== 
X  :   
X  O   
X \|/ 
X / \ 
X 
===========
```''']

make_doc_blocked = [
    "ChannelCreate",
    "ChannelDelete",
    "ChannelPinUpdate",
    "ChannelUpdate",
    "CommandErrorHandler",
    "EmojiUpdate",
    "GuildUpdate",
    "IaInteractions",
    "MemberBanClass",
    "MemberUpdate",
    "OnMemberJoin",
    "OnMemberRemove",
    "OnMessageDelete",
    "OnMessageEdit",
    "OnReady",
    "OnTypingClass",
    "RoleCreate",
    "RoleDelete",
    "RoleUpdate",
    "Shards",
    "SystemMessage",
    "UnBanClass",
    "VoiceClass"
]

reward_broken = {
    "leather": {
        "breastplate": {
            "silver": [("breastplate_shards", 5), ("essence_leather", 1)],
            "mystic": [("breastplate_shards", 25), ("essence_leather", 2)],
            "inspiron": [("breastplate_shards", 75), ("essence_leather", 3)],
            "violet": [("breastplate_shards", 125), ("essence_leather", 4)],
            "hero": [("breastplate_shards", 250), ("essence_leather", 5)],
        },
        "leggings": {
            "silver": [("leggings_shards", 5), ("essence_leather", 1)],
            "mystic": [("leggings_shards", 25), ("essence_leather", 2)],
            "inspiron": [("leggings_shards", 75), ("essence_leather", 3)],
            "violet": [("leggings_shards", 125), ("essence_leather", 4)],
            "hero": [("leggings_shards", 250), ("essence_leather", 5)],
        },
        "boots": {
            "silver": [("boots_shards", 5), ("essence_leather", 1)],
            "mystic": [("boots_shards", 25), ("essence_leather", 2)],
            "inspiron": [("boots_shards", 75), ("essence_leather", 3)],
            "violet": [("boots_shards", 125), ("essence_leather", 4)],
            "hero": [("boots_shards", 250), ("essence_leather", 5)],
        },
        "gloves": {
            "silver": [("gloves_shards", 5), ("essence_leather", 1)],
            "mystic": [("gloves_shards", 25), ("essence_leather", 2)],
            "inspiron": [("gloves_shards", 75), ("essence_leather", 3)],
            "violet": [("gloves_shards", 125), ("essence_leather", 4)],
            "hero": [("gloves_shards", 250), ("essence_leather", 5)],
        },
        "shoulder": {
            "silver": [("shoulder_shards", 5), ("essence_leather", 1)],
            "mystic": [("shoulder_shards", 25), ("essence_leather", 2)],
            "inspiron": [("shoulder_shards", 75), ("essence_leather", 3)],
            "violet": [("shoulder_shards", 125), ("essence_leather", 4)],
            "hero": [("shoulder_shards", 250), ("essence_leather", 5)],
        },
        "sword": {
            "silver": [("assassin_sword_shards", 5), ("necromancer_sword_shards", 5),
                       ("paladin_sword_shards", 5), ("priest_swords_shards", 5),
                       ("warlock_sword_shards", 5), ("warrior_sword_shards", 5), ("wizard_sword_shards", 5)],
            "mystic": [("assassin_sword_shards", 25), ("necromancer_sword_shards", 25),
                       ("paladin_sword_shards", 25), ("priest_swords_shards", 25),
                       ("warlock_sword_shards", 55), ("warrior_sword_shards", 25), ("wizard_sword_shards", 25)],
            "inspiron": [("assassin_sword_shards", 75), ("necromancer_sword_shards", 75),
                         ("paladin_sword_shards", 75), ("priest_swords_shards", 75),
                         ("warlock_sword_shards", 75), ("warrior_sword_shards", 75),
                         ("wizard_sword_shards", 75)],
            "violet": [("assassin_sword_shards", 125), ("necromancer_sword_shards", 125),
                       ("paladin_sword_shards", 125), ("priest_swords_shards", 125),
                       ("warlock_sword_shards", 125), ("warrior_sword_shards", 125),
                       ("wizard_sword_shards", 125)],
            "hero": [("assassin_sword_shards", 250), ("necromancer_sword_shards", 250),
                     ("paladin_sword_shards", 250), ("priest_swords_shards", 250),
                     ("warlock_sword_shards", 250), ("warrior_sword_shards", 250),
                     ("wizard_sword_shards", 250)]
        }
    },
    "platinum": {
        "breastplate": {
            "silver": [("breastplate_shards", 5), ("essence_platinum", 1)],
            "mystic": [("breastplate_shards", 25), ("essence_platinum", 2)],
            "inspiron": [("breastplate_shards", 75), ("essence_platinum", 3)],
            "violet": [("breastplate_shards", 125), ("essence_platinum", 4)],
            "hero": [("breastplate_shards", 250), ("essence_platinum", 5)],
        },
        "leggings": {
            "silver": [("leggings_shards", 5), ("essence_platinum", 1)],
            "mystic": [("leggings_shards", 25), ("essence_platinum", 2)],
            "inspiron": [("leggings_shards", 75), ("essence_platinum", 3)],
            "violet": [("leggings_shards", 125), ("essence_platinum", 4)],
            "hero": [("leggings_shards", 250), ("essence_platinum", 5)],
        },
        "boots": {
            "silver": [("boots_shards", 5), ("essence_platinum", 1)],
            "mystic": [("boots_shards", 25), ("essence_platinum", 2)],
            "inspiron": [("boots_shards", 75), ("essence_platinum", 3)],
            "violet": [("boots_shards", 125), ("essence_platinum", 4)],
            "hero": [("boots_shards", 250), ("essence_platinum", 5)],
        },
        "gloves": {
            "silver": [("gloves_shards", 5), ("essence_platinum", 1)],
            "mystic": [("gloves_shards", 25), ("essence_platinum", 2)],
            "inspiron": [("gloves_shards", 75), ("essence_platinum", 3)],
            "violet": [("gloves_shards", 125), ("essence_platinum", 4)],
            "hero": [("gloves_shards", 250), ("essence_platinum", 5)],
        },
        "shoulder": {
            "silver": [("shoulder_shards", 5), ("essence_platinum", 1)],
            "mystic": [("shoulder_shards", 25), ("essence_platinum", 2)],
            "inspiron": [("shoulder_shards", 75), ("essence_platinum", 3)],
            "violet": [("shoulder_shards", 125), ("essence_platinum", 4)],
            "hero": [("shoulder_shards", 250), ("essence_platinum", 5)],
        },
        "sword": {
            "silver": [("assassin_sword_shards", 5), ("necromancer_sword_shards", 5),
                       ("paladin_sword_shards", 5), ("priest_swords_shards", 5),
                       ("warlock_sword_shards", 5), ("warrior_sword_shards", 5), ("wizard_sword_shards", 5)],
            "mystic": [("assassin_sword_shards", 25), ("necromancer_sword_shards", 25),
                       ("paladin_sword_shards", 25), ("priest_swords_shards", 25),
                       ("warlock_sword_shards", 55), ("warrior_sword_shards", 25), ("wizard_sword_shards", 25)],
            "inspiron": [("assassin_sword_shards", 75), ("necromancer_sword_shards", 75),
                         ("paladin_sword_shards", 75), ("priest_swords_shards", 75),
                         ("warlock_sword_shards", 75), ("warrior_sword_shards", 75),
                         ("wizard_sword_shards", 75)],
            "violet": [("assassin_sword_shards", 125), ("necromancer_sword_shards", 125),
                       ("paladin_sword_shards", 125), ("priest_swords_shards", 125),
                       ("warlock_sword_shards", 125), ("warrior_sword_shards", 125),
                       ("wizard_sword_shards", 125)],
            "hero": [("assassin_sword_shards", 250), ("necromancer_sword_shards", 250),
                     ("paladin_sword_shards", 250), ("priest_swords_shards", 250),
                     ("warlock_sword_shards", 250), ("warrior_sword_shards", 250),
                     ("wizard_sword_shards", 250)]
        }
    },
    "cover": {
        "breastplate": {
            "silver": [("breastplate_shards", 5), ("essence_cover", 1)],
            "mystic": [("breastplate_shards", 25), ("essence_cover", 2)],
            "inspiron": [("breastplate_shards", 75), ("essence_cover", 3)],
            "violet": [("breastplate_shards", 125), ("essence_cover", 4)],
            "hero": [("breastplate_shards", 250), ("essence_cover", 5)],
        },
        "leggings": {
            "silver": [("leggings_shards", 5), ("essence_cover", 1)],
            "mystic": [("leggings_shards", 25), ("essence_cover", 2)],
            "inspiron": [("leggings_shards", 75), ("essence_cover", 3)],
            "violet": [("leggings_shards", 125), ("essence_cover", 4)],
            "hero": [("leggings_shards", 250), ("essence_cover", 5)],
        },
        "boots": {
            "silver": [("boots_shards", 5), ("essence_cover", 1)],
            "mystic": [("boots_shards", 25), ("essence_cover", 2)],
            "inspiron": [("boots_shards", 75), ("essence_cover", 3)],
            "violet": [("boots_shards", 125), ("essence_cover", 4)],
            "hero": [("boots_shards", 250), ("essence_cover", 5)],
        },
        "gloves": {
            "silver": [("gloves_shards", 5), ("essence_cover", 1)],
            "mystic": [("gloves_shards", 25), ("essence_cover", 2)],
            "inspiron": [("gloves_shards", 75), ("essence_cover", 3)],
            "violet": [("gloves_shards", 125), ("essence_cover", 4)],
            "hero": [("gloves_shards", 250), ("essence_cover", 5)],
        },
        "shoulder": {
            "silver": [("shoulder_shards", 5), ("essence_cover", 1)],
            "mystic": [("shoulder_shards", 25), ("essence_cover", 2)],
            "inspiron": [("shoulder_shards", 75), ("essence_cover", 3)],
            "violet": [("shoulder_shards", 125), ("essence_cover", 4)],
            "hero": [("shoulder_shards", 250), ("essence_cover", 5)],
        },
        "sword": {
            "silver": [("assassin_sword_shards", 5), ("necromancer_sword_shards", 5),
                       ("paladin_sword_shards", 5), ("priest_swords_shards", 5),
                       ("warlock_sword_shards", 5), ("warrior_sword_shards", 5), ("wizard_sword_shards", 5)],
            "mystic": [("assassin_sword_shards", 25), ("necromancer_sword_shards", 25),
                       ("paladin_sword_shards", 25), ("priest_swords_shards", 25),
                       ("warlock_sword_shards", 55), ("warrior_sword_shards", 25), ("wizard_sword_shards", 25)],
            "inspiron": [("assassin_sword_shards", 75), ("necromancer_sword_shards", 75),
                         ("paladin_sword_shards", 75), ("priest_swords_shards", 75),
                         ("warlock_sword_shards", 75), ("warrior_sword_shards", 75),
                         ("wizard_sword_shards", 75)],
            "violet": [("assassin_sword_shards", 125), ("necromancer_sword_shards", 125),
                       ("paladin_sword_shards", 125), ("priest_swords_shards", 125),
                       ("warlock_sword_shards", 125), ("warrior_sword_shards", 125),
                       ("wizard_sword_shards", 125)],
            "hero": [("assassin_sword_shards", 250), ("necromancer_sword_shards", 250),
                     ("paladin_sword_shards", 250), ("priest_swords_shards", 250),
                     ("warlock_sword_shards", 250), ("warrior_sword_shards", 250),
                     ("wizard_sword_shards", 250)]
        }
    }
}
