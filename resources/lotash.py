import random


class LoteriaNaoSuportada(Exception):
    pass


class QuantidadeInvalida(Exception):
    pass


K_COMMON = 0
LOTERIAS = {
    'quina': {
        'marcar': (5, 7), 'numeros': (1, 80),
    },
    'megasena': {
        'marcar': (6, 15), 'numeros': (1, 60), 'nome': "Mega-Sena",
    },
    'lotofacil': {
        'marcar': (15, 18), 'numeros': (1, 25),
    },
    'lotomania': {
        'marcar': (1, 50), 'numeros': (1, 100), 'padrao': 20,
        'url-script': "_lotomania_pesquisa.asp",
    },
    'duplasena': {
        'marcar': (6, 15), 'numeros': (1, 50), 'nome': "Dupla Sena",
    }
}


class Lottery(object):
    def __init__(self, nome):
        try:
            c = LOTERIAS[nome]
        except KeyError as err:
            raise LoteriaNaoSuportada(err)

        self.settings = c
        self.nome = nome

        # atributos do gerador de números
        self._range = range(c['numeros'][0], c['numeros'][1] + 1)
        self._min = c['marcar'][0]
        self._max = c['marcar'][1]
        self._padrao = c.get('padrao', self._min)

    def gerar_aposta(self, marcar=None):
        if marcar is None:
            marcar = self._padrao
        if not (self._min <= marcar <= self._max):
            raise QuantidadeInvalida(self.nome, marcar)
        result = random.sample(self._range, marcar)
        return tuple(sorted(result))


def create(loteria, quantidade, numeros):
    bets = list()
    try:
        for _ in range(quantidade):
            bets.append(loteria.gerar_aposta(numeros))
    except QuantidadeInvalida:
        return None

    return bets
