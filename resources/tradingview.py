import json

from tradingview_ta import TA_Handler, Interval, Exchange

TEST = False
if TEST:
    with open("../data/attribute.json", encoding="utf8") as attribute:
        all_data = {"attribute": json.loads(attribute.read())}
else:
    from config import data as all_data


class TradingView(object):
    def __init__(self):
        self.flutuation = all_data['attribute']["flutuation"]
        self.exchange_rate = 0.025

    def get_link(self, exchange):
        company = f'{self.flutuation[exchange][1]}'
        return f"https://br.tradingview.com/symbols/{f'{self.flutuation[exchange][0]}'}", company

    def get_flutuation(self, exchange):
        flutuation = TA_Handler(
            symbol=f"{self.flutuation[exchange][0]}",
            screener=f"{self.flutuation[exchange][3]}",
            exchange=f"{self.flutuation[exchange][2]}",
            interval=Interval.INTERVAL_1_DAY
        )
        change = flutuation.get_analysis().indicators["change"]
        return change + (change * self.exchange_rate)


if __name__ == "__main__":
    flutuations = TradingView()
    for ex in flutuations.flutuation.keys():
        print(flutuations.get_flutuation(ex))
