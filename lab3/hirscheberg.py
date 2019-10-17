from itertools import cycle
from operator import itemgetter


class Hirscheberg:
    COD_LEFT = 1
    COD_UP_LEFT = 2
    COD_UP = 3
    GAP_CHAR = '_'

    def __init__(self, metric, gap, chain_a, chain_b):
        self.metric = metric
        self.gap = gap
        self.chain_a = chain_a
        self.chain_b = chain_b
        (self.align_chain_a, self.align_chain_b), self.score = self.hirscheberg(self.chain_a, self.chain_b)

    def nw_mini(self, a, b):
        """
        Минимализованый алгоритм Needleman–Wunsch
        Цепочка b должна иметь размер равный 1. А цепочка a должна быть не пустой

        :param a: Цепока a
        :param b: Цепока b
        :return: выравнивание для цепочки a, выравнивание для цепочки b, score
        """
        assert len(b) == 1
        pos, score = max(enumerate(map(self.metric, a, cycle(b))), key=itemgetter(1))
        if score > 2 * self.gap:
            return (
                a,
                self.GAP_CHAR * pos + b + self.GAP_CHAR * (len(a) - pos - 1),
                score + self.gap * (len(a) - 1)
            )
        return (
            a + self.GAP_CHAR,
            self.GAP_CHAR * len(a) + b,
            self.gap * (len(a) + 1)
        )

    def score_nw(self, a, b):
        """
        Возвращение последней строки при вычислении алгоритма Needleman–Wunsch

        :param a: Цепока a
        :param b: Цепока b
        :return: Массив длиной len(a) + 1
        """
        line = [x * self.gap for x in range(len(a) + 1)]
        for char_b in b:
            c = line[0] + self.gap
            for j, char_a in enumerate(a):
                score_gap_a = line[j + 1] + self.gap
                score_gap_b = c + self.gap
                score_cmp_ab = line[j] + self.metric(char_a, char_b)
                line[j], c = c, max(score_gap_a, score_gap_b, score_cmp_ab)
            line[-1] = c
        return line

    def hirscheberg(self, a, b):
        """
        Алгоритм Hirscheberg

        :param a: Цепочка a
        :param b: Цепочка b
        :return: (выровненная цепочка a, выровненная цепочка b), score
        """
        # Чтобы уменьшить количество логических блоков,
        # предполагается, что len(a) > len(b), иначе цепочки меняются местами
        a_le_b = len(a) < len(b)
        if a_le_b:
            a, b = b, a
        # Если минимальная цепочка нулевой длины,
        # то возвращаем максимальную цепочку
        # и цепочку состоящую из gap длиной len(a)
        if not len(b):
            x = a
            y = self.GAP_CHAR * len(a)
            score = self.gap * len(a)
        # Если минимальная цепочка имеет размер равный 1,
        # то выравниваем их при помощи
        # минимализованого алгоритма Needleman–Wunsch
        elif len(b) == 1:
            x, y, score = self.nw_mini(a, b)
        # Иначе делим максимальную цепочку на две части
        # и рекурсивно высчитываем выравнивание для двух частей
        else:
            # Центр максимальной цепочки
            a_mid = len(a) // 2
            # Высчитываем последние строки массива скоров для двух частей
            score_left = self.score_nw(b, a[:a_mid])
            # Для правой части делаем реверс строк, так как rev(nw(rev(a), rev(b))) = nw(a, b)
            score_right = self.score_nw(b[::-1], a[:a_mid - 1:-1])
            # b и rev(b) имеют одинаковую длину и из-за реализации score_nw,
            # нам вернутся массивы одинаковой длины

            # Высчитываем arg_max для двух массивов
            b_mid, score = max(enumerate(map(int.__add__, score_left, score_right[::-1])), key=itemgetter(1))
            # Рекурсивно высчитываем выравнивания для a_left, b_left и a_right, b_right и конкатинруем результат
            x, y = map(
                str.__add__,
                self.hirscheberg(a[:a_mid], b[:b_mid])[0],
                self.hirscheberg(a[a_mid:], b[b_mid:])[0]
            )
        # Меняем цепочки местам, если меняли их в начале
        return (y, x) if a_le_b else (x, y), score

    def out(self):
        return self.score, self.align_chain_a, self.align_chain_b

# P.S. Код так себе (На троечку). Тут совсем лишний класс,
# так как все можно было сделать с помощью функций.
# Но класс использовался, чтобы не менять тело модуля main.
# И оптимизация памяти это не про Python
# (хотя если использовать numpy, то еще можно что-то оптимизировать).
# В C/C++ этот алгоритм бы показал себя во всей красе.
