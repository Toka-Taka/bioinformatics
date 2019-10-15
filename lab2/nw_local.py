from functools import reduce


class NWLocal:
    COD_LEFT = 1
    COD_UP_LEFT = 2
    COD_UP = 3
    GAP_CHAR = '_'

    def __init__(self, metric, gap, chain_a, chain_b):
        """

        :param metric: Метрика: функция, возвращающая для пары букв оценку.
        :param gap: Значение штрафа за gap
        :param chain_a: Цепочка A
        :param chain_b: Цепочка B
        """
        self.chain_a = chain_a
        self.chain_b = chain_b
        # self.matrix - матрица на основе которой строится выравнивание
        # Ширина матрицы - длина цепочки A + 1
        # Высота матрицы - длина цепочки B + 1
        # Элемент матрицы - пара (sum, order), где:
        # - sum - значение ячейки
        # - order - направление:
        # -- 1 (COD_LEFT) - gap в строке B
        # -- 2 (COD_UP_LEFT) - оставляем обе буквы
        # -- 3 (COD_UP) - gap в строке A

        # Заполняем в матрице первую строку
        self.matrix = [[(0, None) for _ in range(len(chain_a) + 1)]]
        # Пробегаем по каждой букве цепочки B, тем самым заполняем оставшиеся строки
        for i, b in enumerate(chain_b):
            # Запоминаем верхнуюю строку (последняя заполненная строка)
            upline = self.matrix[-1]
            # Первый элемент текущей строки строится на основе индекса буквы и значения штрафа за gap
            line = [(0, None)]
            # Пробегаем по каждой букве цепочки A
            # И заполняем текущую строку
            for j, a in enumerate(chain_a):
                # Вычисляем штраф за gap в строке B
                # (значение левого элемента + штраф за gap)
                e1 = (line[-1][0] + gap, self.COD_LEFT)
                # Вычисляем штраф за сравнивание букв из двух цеочек
                # (значение левого верхнего элемента + значение сравнения)
                e2 = (upline[j][0] + metric(a, b), self.COD_UP_LEFT)
                # Вычисляем штраф за gap в строке A
                # (значение верхнего элемента + штраф за gap)
                e3 = (upline[j+1][0] + gap, self.COD_UP)
                # Поиск локального скора отличается тем,
                # что все значения не отрицательные.
                # И при нахождении 0 алгоритм останавливается
                e4 = (0, None)
                # В качестве элемента берем максимальное значение
                max_score, direct = max(e1, e2, e3, e4, key=lambda x: x[0])
                line.append((max_score, direct) if max_score else (max_score, None))
            # Добавляем строку в матрицу
            self.matrix.append(line)

    def out(self):
        """
        Получение результата

        :return: score, chain a, chain b
        """
        # Находим максимальный скор и его координаты
        j, i, (val, cod) = reduce(
            lambda acc, el: max(acc, el, key=lambda x: x[2][0]),
            (
                (i, j, el)
                for i, line in enumerate(self.matrix)
                for j, el in enumerate(line)
            ),
            (0, 0, (0, None))
        )
        a = ''
        b = ''
        while cod is not None:
            cod = self.matrix[j][i][1]
            # Если код направления "лево"
            if cod == self.COD_LEFT:
                # К выравненной цеопчки A приписываем символ из цеопчки A (под соответствующем индексом)
                a += self.chain_a[i - 1]
                # К цепочке B приписываем gap
                b += self.GAP_CHAR
                # Сдвигаем "курсор" влево
                i -= 1
            elif cod == self.COD_UP_LEFT:
                # К выравненной цеопчки A приписываем символ из цеопчки A (под соответствующем индексом)
                a += self.chain_a[i - 1]
                # К выравненной цеопчки B приписываем символ из цеопчки B (под соответствующем индексом)
                b += self.chain_b[j - 1]
                # Сдвигаем "курсор" влево и вверх
                i -= 1
                j -= 1
            elif cod == self.COD_UP:
                # К цепочке A приписываем gap
                a += self.GAP_CHAR
                # К выравненной цеопчки B приписываем символ из цеопчки B (под соответствующем индексом)
                b += self.chain_b[j - 1]
                # Сдвигаем "курсор" в вверх
                j -= 1
        return val, a[::-1], b[::-1]
