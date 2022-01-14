import json

from random import randint, choice

HASH, TEST = ["Melted Bone", "Life Crystal", "Energy", "Death Blow", "Stone of Soul", "Vital Force"], False
if TEST:
    with open("../data/attribute.json", encoding="utf8") as attribute:
        all_data = {"attribute": json.loads(attribute.read())}
else:
    from config import data as all_data


class Broker(object):
    def __init__(self):
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

                new_exchanges[ex][_ + 1] = exchange
        return new_exchanges

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

    broker.create_exchanges()

    for _exchange in broker.exchanges.keys():
        value_now = broker.get_exchange(_exchange)
        be = broker.format_blessed(value_now / cotacao_be)
        be_tot = broker.format_blessed(value_now / cotacao_be * 1000)
        tot_global += value_now / cotacao_be * 1000
        print(f"{_exchange} = Ethernyas: {broker.format_value(value_now)} - BITASH: {be} | Total BITASH: {be_tot}")
    et = broker.format_value(tot_global * cotacao_be)
    print(f"\nTotal da bolsa em BITASH: {broker.format_blessed(tot_global)} | Ethernyas: {et}")
