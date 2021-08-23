import math
import decimal
import datetime

dec = decimal.Decimal


def position(now=None):
    if now is None:
        now = datetime.datetime.now()

    diff = now - datetime.datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    lunations = dec("0.20439731") + (days * dec("0.03386319269"))

    return lunations % dec(1)


def phase(pos):
    index = (pos * dec(8)) + dec("0.5")
    index = math.floor(index)
    return {
        0: "Lua Nova",
        1: "Quarto Crescente",
        2: "Lua Crescente",
        3: "Crescente Gibosa",
        4: "Lua Cheia",
        5: "Minguante Gibosa",
        6: "Quarto Minguante",
        7: "Lua Minguante"
    }[int(index) & 7]


def get_moon():
    _position = position()
    phase_name = phase(_position)
    rounded_position = round(float(_position), 3)
    return phase_name, rounded_position


if __name__ == "__main__":
    response = get_moon()
    print(response[0], response[1])
