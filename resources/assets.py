import json

from random import randint, choice

HASH, TEST = ["Melted Bone", "Life Crystal", "Energy", "Death Blow", "Stone of Soul", "Vital Force"], False
if TEST:
    with open("../data/attribute.json", encoding="utf8") as attribute:
        all_data = {"attribute": json.loads(attribute.read())}
else:
    from config import data as all_data


class Broker(object):
    def __init__(self, bot):
        self.bot = bot
        self.assets = all_data['attribute']["assets"]
        self.exchanges = all_data['attribute']["exchanges"]

    def create_exchanges(self):
        new_exchanges = dict()
        for ex in self.exchanges.keys():
            new_exchanges[ex] = dict()
            for _ in range(1000):

                if _ in [n for n in range(len(self.exchanges[ex]))]:
                    _asset = self.assets[self.exchanges[ex][_]]
                    value = randint(_asset // 2, _asset)
                    exchange = {"item": self.exchanges[ex][_], "value": value, "owner": None}

                else:
                    exch = HASH + self.exchanges[ex]
                    _asset = self.assets[choice(self.exchanges[ex])]
                    value = randint(_asset // 2, _asset)
                    exchange = {"item": choice(exch), "value": value, "owner": None}

                new_exchanges[ex][str(_ + 1)] = exchange
        return new_exchanges

    @staticmethod
    def format_value(num):
        a = '{:,.0f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    @staticmethod
    def format_flutuation(num):
        a = '{:,.1f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    @staticmethod
    def format_bitash(num):
        a = '{:,.4f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    def get_assets(self, name):
        assets = self.exchanges[name]
        return assets

    def get_exchange(self, name):

        if name not in self.exchanges.keys():
            return -1

        if self.bot is not None:
            flutuation = float(self.bot.tradingview.get_flutuation(name))
        else:
            flutuation = 0.0

        value = 0
        for asset in self.exchanges[name]:
            value += self.assets[asset]

        original = float(value)

        value += value * flutuation

        if value < original * 0.25:
            value = original * 0.25

        return value


if __name__ == "__main__":

    def get_balance_now(bk):
        cotacao_be, tot_global = 500000, 0
        for _exchange in bk.exchanges.keys():
            value_now = bk.get_exchange(_exchange)
            be = bk.format_bitash(value_now / cotacao_be)
            be_tot = bk.format_bitash(value_now / cotacao_be * 1000)
            tot_global += value_now / cotacao_be * 1000
            print(f"{_exchange} = Ethernyas: {bk.format_value(value_now)} - BITASH: {be} | Total BITASH: {be_tot}")
        et = bk.format_value(tot_global * cotacao_be)
        print(f"\nTotal da bolsa em BITASH: {bk.format_bitash(tot_global)} | Ethernyas: {et}")

    broker = Broker(None)
    get_balance_now(broker)
    _exchanges = broker.create_exchanges()
    print(_exchanges)
