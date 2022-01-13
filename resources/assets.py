from random import randint, choice


ASSETS = {
    "Gold Cube": 250000,
    "Golden Apple": 75000,
    "Golden Egg": 50000,
    "Transmogrificador": 150000,
    "Stone of Moon": 111000,
    "Lost Parchment": 71428,
    "Royal Parchment": 71428,
    "Sages Scroll": 71428,
    "Melted Artifact": 75000,
    "Unsealed Stone": 45000,
    "Feather White": 100000,
    "Feather Gold": 100000,
    "Feather Black": 100000,
    "Essence Cover": 35000,
    "Essence Leather": 35000,
    "Essence Platinum": 35000,
    "Teleport Scroll": 50000,
    "Pass Royal": 50000,
    "Frozen Letter": 100000,
    "Angel Stone": 33333,
    "Angel Wing": 50000,
    "Herb Red": 100000,
    "Herb Green": 100000,
    "Herb Blue": 100000,
    "Transcendental Stone": 250000,
    "Transcendental Flower": 250000
}

EXCHANGES = {
    "Etheria": ["Gold Cube", "Golden Apple", "Golden Egg"],
    "Rauberior": ["Stone of Moon", "Transmogrificador"],
    "Ilumiora": ["Lost Parchment", "Royal Parchment", "Sages Scroll"],
    "Kerontaris": ["Melted Artifact", "Unsealed Stone"],
    "Widebor": ["Feather White", "Feather Gold", "Feather Black"],
    "Jangalor": ["Essence Cover", "Essence Leather", "Essence Platinum"],
    "Yotungar": ["Teleport Scroll", "Pass Royal"],
    "Shoguriar": ["Frozen Letter", "Angel Stone", "Angel Wing"],
    "Dracaris": ["Herb Red", "Herb Green", "Herb Blue"],
    "Forgerion": ["Transcendental Stone", "Transcendental Flower"]
}

AMOUNT = {
    'Gold Cube': 8,
    'Golden Apple': 35,
    'Golden Egg': 41,
    'Transmogrificador': 657,
    'Stone of Moon': 129,
    'Lost Parchment': 133,
    'Royal Parchment': 148,
    'Sages Scroll': 143,
    'Melted Artifact': 809,
    'Unsealed Stone': 1372,
    'Feather White': 186,
    'Feather Gold': 61,
    'Feather Black': 136,
    'Essence Cover': 154,
    'Essence Leather': 107,
    'Essence Platinum': 112,
    'Teleport Scroll': 184,
    'Pass Royal': 76,
    'Frozen Letter': 2832,
    'Angel Stone': 919,
    'Angel Wing': 1544,
    'Herb Red': 387,
    'Herb Green': 313,
    'Herb Blue': 416,
    'Transcendental Stone': 534,
    'Transcendental Flower': 582
}

EXCHANGE_VALUE = {
    "Etheria": 0,
    "Rauberior": 0,
    "Ilumiora": 0,
    "Kerontaris": 0,
    "Widebor": 0,
    "Jangalor": 0,
    "Yotungar": 0,
    "Shoguriar": 0,
    "Dracaris": 0,
    "Forgerion": 0
}


class Broker(object):
    def __init__(self):
        self.assets = ASSETS
        self.exchanges = EXCHANGES
        self.amount = AMOUNT

    @staticmethod
    def format_value(num):
        a = '{:,.0f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    @staticmethod
    def format_blessed(num):
        a = '{:,.4f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    def get_asset(self, name):
        pass

    def get_exchange(self, name):

        if name not in self.exchanges.keys():
            return print("Essa EXCHANGE nao existe!")

        value = 0
        for asset in self.exchanges[name]:
            value += self.assets[asset]

        return value


if __name__ == "__main__":
    broker = Broker()
    cotacao_be = 500000
    tot_global = 0
    for exchange in EXCHANGE_VALUE.keys():
        value_now = broker.get_exchange(exchange)
        be = broker.format_blessed(value_now / cotacao_be)
        be_tot = broker.format_blessed(value_now / cotacao_be * 1000)
        tot_global += value_now / cotacao_be * 1000
        print(f"{exchange}: {broker.format_value(value_now)} - BE: {be} | Total: {be_tot}")
    et = broker.format_value(tot_global * cotacao_be)
    print(f"\nTotal da bolsa: {broker.format_blessed(tot_global)} | Ethernyas: {et}")
