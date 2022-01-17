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

    @staticmethod
    def get_link(exchange):
        return f"https://br.tradingview.com/symbols/{f'{self.flutuation[exchange][0]}'}"

    def get_flutuation(self, exchange):
        flutuation = TA_Handler(
            symbol=f"{self.flutuation[exchange][0]}",
            screener=f"{self.flutuation[exchange][3]}",
            exchange=f"{self.flutuation[exchange][2]}",
            interval=Interval.INTERVAL_1_DAY
        )
        return flutuation.get_analysis().indicators["change"]


if __name__ == "__main__":
    flutuations = TradingView()
    for ex in flutuations.flutuation.keys():
        print(flutuations.get_flutuation(ex))