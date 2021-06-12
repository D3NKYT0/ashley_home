from random import choice, randint
from config import data as config
from resources.verify_cooldown import verify_cooldown


def generate_gift():
    gentype = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    key = ['AySeHlLhEsYa', 'aYsEhLlHeSyA']
    lgt = list()
    gift = str()
    fgift = str()
    for L in key[choice([0, 1])]:
        lgt.append(L.upper())
        lgt.append(ord(L))
    for c in range(len(lgt)):
        if c % 2 == 0:
            gift += str(lgt[c])
        else:
            gift += str(choice(gentype))
    for L in range(len(gift)):
        if L % 5 == 0 and L != 0:
            fgift += '-'
        fgift += gift[L]
    fgift += str(choice(gentype))
    gift += fgift[-1]
    return fgift, gift


async def register_gift(bot, time):
    while True:
        gift_t, _id = generate_gift()
        data = await bot.db.get_data("_id", _id, "gift")
        if data is None:
            data = {"_id": _id, "gift_t": gift_t, "validity": time}
            await bot.db.push_data(data, "gift")
            if not await verify_cooldown(bot, _id, time):
                return gift_t


async def register_code(bot, _id, _code1, _code2, adlink1, adlink2, bonus):
    data = {"_id": _id, "code": [_code1, _code2], "adlink": [adlink1, adlink2], "bonus": bonus, "pending": True}
    await bot.db.push_data(data, "adfly")


async def open_gift(bot, gift):
    if "-" in gift:
        key = "gift_t"
    else:
        key = "_id"

    data = await bot.db.get_data(key, gift, "gift")

    if data is not None:

        _id = data['_id']
        time = data['validity']

        if await verify_cooldown(bot, _id, time, True):
            validity = True
        else:
            validity = False

        ethernyas = randint(250, 300)
        coins = randint(50, 100)
        items = ['crystal_fragment_light', 'crystal_fragment_energy', 'crystal_fragment_dark', 'Energy']

        rare = None
        chance = randint(1, 100)
        if chance <= 50:
            item_1 = choice(['Unearthly', 'Surpassing', 'Hurricane', 'Heavenly', 'Blazing', 'Augur'])
            item_2 = choice(['Crystal_of_Energy', 'Discharge_Crystal', 'Acquittal_Crystal'])
            item_3 = choice(['SoulStoneYellow', 'SoulStoneRed', 'SoulStonePurple', 'SoulStoneGreen',
                             'SoulStoneDarkGreen', 'SoulStoneBlue'])
            rare = [item_1, item_2, item_3]

            if chance < 5:
                item_plus = choice(["soul_crystal_of_love", "soul_crystal_of_love", "soul_crystal_of_love",
                                    "soul_crystal_of_hope", "soul_crystal_of_hope", "soul_crystal_of_hope",
                                    "soul_crystal_of_hate", "soul_crystal_of_hate", "soul_crystal_of_hate"])
                rare.append(item_plus)

        return {"money": ethernyas, "coins": coins, "items": items, "rare": rare, "validity": validity}

    else:
        return None


def choice_chest(chest, event):
    if chest == "Baú de Evento - Incomum":
        chance_relic = 5
        max_money = 250 if event else 100
        max_coin = 100 if event else 50
        max_energy = 75 if event else 50
        bonus = choice(['Unearthly', 'Surpassing', 'Hurricane', 'Heavenly', 'Blazing', 'Augur'])
        items = ['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal', bonus]

        relics = {
            "WrathofNatureCapsule": 1,
            "UltimateSpiritCapsule": 1,
            "SuddenDeathCapsule": 1,
            "InnerPeacesCapsule": 1,
            "EternalWinterCapsule": 1,
            "EssenceofAsuraCapsule": 1,
            "DivineCalderaCapsule": 1,
            "DemoniacEssenceCapsule": 1,
            "unsealed_stone": 1,
            "melted_artifact": 1,
            "angel_stone": 1,
            "angel_wing": 1
        }

    elif chest == "Baú de Evento - Raro":
        chance_relic = 15
        max_money = 300 if event else 100
        max_coin = 150 if event else 50
        max_energy = 100 if event else 50
        bonus = choice(["crystal_fragment_light", "crystal_fragment_energy", "crystal_fragment_dark"])
        items = ['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal', bonus]

        relics = {
            "WrathofNatureCapsule": 3,
            "UltimateSpiritCapsule": 3,
            "SuddenDeathCapsule": 3,
            "InnerPeacesCapsule": 3,
            "EternalWinterCapsule": 3,
            "EssenceofAsuraCapsule": 3,
            "DivineCalderaCapsule": 3,
            "DemoniacEssenceCapsule": 3,
            "unsealed_stone": 1,
            "melted_artifact": 1,
            "angel_stone": 1,
            "angel_wing": 1
        }

    elif chest == "Baú de Evento - Super Raro":
        chance_relic = 25
        max_money = 350 if event else 100
        max_coin = 200 if event else 50
        max_energy = 125 if event else 50
        bonus = choice(["solution_agent_green", "solution_agent_blue", "nucleo_z", "nucleo_y", "nucleo_x"])

        if randint(1, 100) < 60:
            bb = choice(["crystal_fragment_light", "crystal_fragment_energy", "crystal_fragment_dark"])
            items = ['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal', bonus, bb]
        else:
            items = ['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal', bonus]

        relics = {
            "WrathofNatureCapsule": 5,
            "UltimateSpiritCapsule": 5,
            "SuddenDeathCapsule": 5,
            "InnerPeacesCapsule": 5,
            "EternalWinterCapsule": 5,
            "EssenceofAsuraCapsule": 5,
            "DivineCalderaCapsule": 5,
            "DemoniacEssenceCapsule": 5,
            "unsealed_stone": 1,
            "melted_artifact": 1,
            "boss_key": 1,
            "angel_stone": 1,
            "angel_wing": 1
        }

    else:
        chance_relic = 35
        max_money = 400 if event else 100
        max_coin = 250 if event else 50
        max_energy = 150 if event else 50
        bonus = choice(["solution_agent_green", "solution_agent_blue", "nucleo_z", "nucleo_y", "nucleo_x"])

        if randint(1, 100) < 80:
            bb = choice(["crystal_fragment_light", "crystal_fragment_energy", "crystal_fragment_dark"])
            items = ['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal', bonus, bb]
        else:
            items = ['Discharge_Crystal', 'Crystal_of_Energy', 'Acquittal_Crystal', bonus]

        relics = {
            "WrathofNatureCapsule": 1,
            "UltimateSpiritCapsule": 1,
            "SuddenDeathCapsule": 1,
            "InnerPeacesCapsule": 1,
            "EternalWinterCapsule": 1,
            "EssenceofAsuraCapsule": 1,
            "DivineCalderaCapsule": 1,
            "DemoniacEssenceCapsule": 1
        }

    return chance_relic, max_money, max_coin, max_energy, items, relics


def open_chest(chest, event=True, amount=None):
    max_relics = list()
    _data = choice_chest(chest, event)
    chance_relic = _data[0]
    max_money = _data[1]
    max_coin = _data[2]
    max_energy = _data[3]
    items = _data[4]
    relics = _data[5]

    ethernyas = randint(200 if event else 50, max_money)
    coins = randint(50 if event else 5, max_coin)
    Energy = randint(50 if event else 5, max_energy)

    if randint(1, 100) <= chance_relic and event:
        list_relic = list()
        for k, v in relics.items():
            list_relic += [k] * v
        max_relics.append(choice(list_relic))

    if amount is not None:
        if amount - 1 > 0:
            for _ in range(amount - 1):
                chests, bbchests = list(), {"Baú de Evento - Incomum": 20, "Baú de Evento - Raro": 10,
                                            "Baú de Evento - Super Raro": 5, "Baú de Evento - Ultra Raro": 1}
                for k, v in bbchests.items():
                    chests += [k] * v
                chest_new = choice(chests)

                _data = choice_chest(chest_new, event)
                chance_relic = _data[0]
                max_money = _data[1]
                max_coin = _data[2]
                max_energy = _data[3]
                items += _data[4]
                relics = _data[5]

                ethernyas += randint(200 if event else 50, max_money)
                coins += randint(50 if event else 5, max_coin)
                Energy += randint(50 if event else 5, max_energy)

                if randint(1, 100) <= chance_relic and event:
                    list_relic = list()
                    for k, v in relics.items():
                        list_relic += [k] * v
                    max_relics.append(choice(list_relic))

    return {"money": ethernyas, "coins": coins, "Energy": Energy, "items": items, "relic": max_relics}
