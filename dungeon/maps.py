from PIL import Image, ImageDraw, ImageFont


_NUM = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30)
_LETTERS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
            'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD')

LEGEND = {
    "0": (0, 0, 0, 255),
    "1": (231, 230, 230, 255),
    "2": (112, 48, 160, 255),
    "3": (0, 176, 80, 255),
    "4": (255, 0, 0, 255),
    "5": (255, 255, 0, 255),
}

GUNDEONS = {
    "start_floor": [11, 30],
    "floor-1": [11, 30],
    "floor-2": [11, 30],
    "floor-3": [11, 30],
    "floor-4": [11, 30],
    "floor-5": [11, 30],
    "floor-6": [30, 30],
    "floor-7": [30, 30],
    "floor-8": [30, 30],
    "floor-9": [30, 30],
    "last-floor": [30, 30]
}

# ---==== LEGENDAS ====---
#  0 - PAREDE
#  1 - CAMINHO
#  2 - ENTRADA
#  3 - CHEGADA
#  4 - BATALHAS
#  5 - RECOMPENÇAS
# ---==================---


def get_map(img_map=None, show_img=False):

    _MAP = dict()

    if img_map is None:
        img_patch = f"dungeon/maps/start_floor.png"
        size = GUNDEONS["start_floor"]
    else:
        if img_map in GUNDEONS.keys():
            img_patch = f"dungeon/maps/{img_map}.png"
            size = GUNDEONS[img_map]
        else:
            img_patch = f"dungeon/maps/start_floor.png"
            size = GUNDEONS["start_floor"]

    # load image
    image = Image.open(img_patch).convert('RGBA')
    show = ImageDraw.Draw(image)
    _pixel = image.load()
    width, height = image.size
    width -= 1
    height -= 1

    # retangulo inicial
    rectangle_out = [0, 0, 40, 33]
    x1, y1, x2, y2 = rectangle_out
    show.rectangle((x1, y1, x2, y2))  # vermelho

    _COLUM, _LINE = 0, 0
    pix = [x1 + 10 if x1 + 10 <= width else width - 5, y1 + 10 if y1 + 10 <= height else height - 5]
    _MAP[f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"] = [(x1, y1, x2, y2), _pixel[pix[0], pix[1]]]

    for _ in range(size[1] - 1):
        x1 += 40
        x2 += 40
        show.rectangle((x1, y1, x2, y2))  # verde

        _COLUM += 1
        pix = [x1 + 10 if x1 + 10 <= width else width - 5, y1 + 10 if y1 + 10 <= height else height - 5]
        _MAP[f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"] = [(x1, y1, x2, y2), _pixel[pix[0], pix[1]]]

    for n in range(size[0] - 1):
        y1 += 33
        y2 += 33
        show.rectangle((x1, y1, x2, y2))  # vermelho

        _LINE += 1
        pix = [x1 + 10 if x1 + 10 <= width else width - 5, y1 + 10 if y1 + 10 <= height else height - 5]
        _MAP[f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"] = [(x1, y1, x2, y2), _pixel[pix[0], pix[1]]]

        if n % 2 == 0:

            for _ in range(size[1] - 1):
                x1 -= 40
                x2 -= 40
                show.rectangle((x1, y1, x2, y2))  # azul

                _COLUM -= 1
                pix = [x1 + 10 if x1 + 10 <= width else width - 5, y1 + 10 if y1 + 10 <= height else height - 5]
                _MAP[f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"] = [(x1, y1, x2, y2), _pixel[pix[0], pix[1]]]

        else:

            for _ in range(size[1] - 1):
                x1 += 40
                x2 += 40
                show.rectangle((x1, y1, x2, y2))  # verde

                _COLUM += 1
                pix = [x1 + 10 if x1 + 10 <= width else width - 5, y1 + 10 if y1 + 10 <= height else height - 5]
                _MAP[f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"] = [(x1, y1, x2, y2), _pixel[pix[0], pix[1]]]

    if show_img:
        image.show()

    return _MAP


def get_vision(map_dict, loc_now):
    # loc start
    x, y = loc_now

    # vision 3 x 3
    down_left = x - 1, y - 1
    cell_left = x - 1, y
    up_left = x - 1, y + 1
    down_center = x, y - 1
    up_center = x, y + 1
    up_right = x + 1, y + 1
    down_right = x + 1, y - 1
    cell_right = x + 1, y
    cell_center = x, y

    vision = [down_left, cell_left, up_left,
              down_center, cell_center, up_center,
              down_right, cell_right, up_right]

    cells = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    chuncks_create = dict()

    for _ in range(len(vision)):
        chunck = vision[_]
        if chunck[0] < 0 or chunck[1] < 0:
            chuncks_create[cells[_]] = None
        else:
            try:
                cell = f"{_LETTERS[chunck[0]]}{_NUM[chunck[1]]}"
                chuncks_create[cells[_]] = map_dict[cell]
            except (KeyError, IndexError):
                chuncks_create[cells[_]] = None

    return chuncks_create


def get_matrix(map_dict, map_size):
    _matriz_create, colors, _start = list(), dict(), None
    for colum in range(map_size[1]):
        _matriz_create.append(list())
        for line in range(map_size[0]):
            color = map_dict[f"{_LETTERS[colum]}{_NUM[line]}"][1]

            code = -1
            for k in LEGEND.keys():
                if color == LEGEND[k]:
                    code = k

            if code == "2" and _start is None:
                _start = [(_LETTERS[colum], _NUM[line]), (colum, line)]

            _matriz_create[colum].append(code)
            if color not in colors.keys():
                colors[color] = 1
            else:
                colors[color] += 1
    return _matriz_create, _start


def create_map(chuncks_now, img_map, show_img=False):
    # load fonts
    font_text = ImageFont.truetype(f"fonts/bot.otf", 40)

    img_patch = f"dungeon/maps/{img_map}.png"
    size = [3, 3]

    # load image
    image = Image.open(img_patch).convert('RGBA')
    show = ImageDraw.Draw(image)
    _pixel = image.load()
    width, height = image.size
    width -= 1
    height -= 1

    # Text Align
    def text_align(box, text, font_t):
        nonlocal show
        _x1, _y1, _x2, _y2 = box
        w, h = show.textsize(text.upper(), font=font_t)
        x = (_x2 - _x1 - w) // 2 + _x1
        y = (_y2 - _y1 - h) // 2 + _y1
        return x, y

    # retangulo inicial
    rectangle_out = [0, 0, 40, 33]
    x1, y1, x2, y2 = rectangle_out
    _COLUM, _LINE = 0, 0
    cell = f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"
    color = (239, 179, 16, 255) if chuncks_now[cell] is None else chuncks_now[cell][1]
    show.rectangle((x1, y1, x2, y2), color)

    for _ in range(size[1] - 1):
        x1 += 40
        x2 += 40
        _COLUM += 1
        cell = f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"
        color = (239, 179, 16, 255) if chuncks_now[cell] is None else chuncks_now[cell][1]
        show.rectangle((x1, y1, x2, y2), color)

    for n in range(size[0] - 1):
        y1 += 33
        y2 += 33
        _LINE += 1
        cell = f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"
        color = (239, 179, 16, 255) if chuncks_now[cell] is None else chuncks_now[cell][1]
        show.rectangle((x1, y1, x2, y2), color)

        if n % 2 == 0:
            for _ in range(size[1] - 1):
                x1 -= 40
                x2 -= 40
                _COLUM -= 1
                cell = f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"
                color = (239, 179, 16, 255) if chuncks_now[cell] is None else chuncks_now[cell][1]
                show.rectangle((x1, y1, x2, y2), color)

                if cell == "B2":
                    _text = "X"  # sinalizador do jogador
                    x_, y_ = text_align((x1, y1, x2, y2), _text, font_text)
                    show.text(xy=(x_ + 1, y_ + 1), text=_text, fill=(68, 29, 114), font=font_text)
                    show.text(xy=(x_, y_), text=_text, fill=(255, 255, 255), font=font_text)

        else:
            for _ in range(size[1] - 1):
                x1 += 40
                x2 += 40
                _COLUM += 1
                cell = f"{_LETTERS[_COLUM]}{_NUM[_LINE]}"
                color = (239, 179, 16, 255) if chuncks_now[cell] is None else chuncks_now[cell][1]
                show.rectangle((x1, y1, x2, y2), color)

    if show_img:
        image.show()


if __name__ == "__main__":
    for key in GUNDEONS.keys():
        name_map = key
        map_now = get_map(name_map, False)
        _matriz, start_x_y = get_matrix(map_now, GUNDEONS[name_map])
        chuncks = get_vision(map_now, start_x_y[1])
        create_map(chuncks, "vision_map", True)
        break
