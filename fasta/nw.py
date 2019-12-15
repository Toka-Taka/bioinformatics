

# Учеченный алгоритм Нидельмана Вундша
# Высчитывает только скор
# Учитывает максимальное число гэпов
# По памяти занимает 2 * n - где n - максимальное число гэпов
def needleman_wunsch(a, b, metric, gap, n):
    # Данный алгоритм можно разделить на 3 части
    # * A B C D E F G _
    # A ? ? ?          |
    # B ? ? ? ?        |
    # C ? ? ? ? ?     _| 1-ый этап (заполнение массива)
    # D   ? ? ? ? ?    |
    # E     ? ? ? ? ? _| 2-ой этап (массив не изменяется по длине)
    # F       ? ? ? ?  |
    # G         ? ? ? _| 3-ий этап (уменьшение массива)
    n = min(len(a), n)
    len_window = min(2 * n - 1, len(a))
    x = n
    y = max(len(a) - n + 1, n)

    c = metric(a[0], b[0])
    # Высчитывание первой линии
    line = [c + i * gap for i in range(n)] + [None] * (len_window - n)

    # Высчитываение 1-го этапа
    for i, ca in enumerate(a[1:x]):
        c, line[0] = line[0], line[0] + gap
        for j, cb in enumerate(b[1:n + i]):
            e1 = line[j] + gap
            e2 = c + metric(ca, cb)
            e3 = line[j + 1] + gap
            c, line[j + 1] = line[j + 1], max(e1, e2, e3)
        if n + i < len(b):
            e1 = line[n + i - 1] + gap
            e2 = c + metric(ca, b[n + i])
            line[n + i] = max(e1, e2)

    # Высчитывание 2-го этапа (его может и не быть)
    for i, ca in enumerate(a[x:y]):
        e2 = line[0] + metric(ca, b[i + 1])
        e3 = line[1] + gap
        line[0] = max(e2, e3)
        for j, cb in enumerate(b[i + 2:i + len_window]):
            e1 = line[j] + gap
            e2 = line[j + 1] + metric(ca, cb)
            e3 = line[j + 2] + gap
            line[j + 1] = max(e1, e2, e3)

        e1 = line[-2] + gap
        e2 = line[-1] + metric(ca, b[i + len_window])
        line[-1] = max(e1, e2)

    # Вычисление 3-го этапа
    for i, ca in enumerate(a[y:]):
        e2 = line[i] + metric(ca, b[i + 1])
        e3 = line[i + 1] + gap
        c, line[i + 1] = line[i+1], max(e2, e3)
        for j, cb in enumerate(b[-len_window + i + 2:]):
            e1 = line[i + j + 1] + gap
            e2 = c + metric(ca, cb)
            e3 = line[i + j + 2] + gap
            c, line[i + j + 2] = line[i + j + 2], max(e1, e2, e3)
        line[i] = None

    # Возврат скора
    return line[-1]


# Это код из первой лабы
# Полный алгоритм Нидельмана Вундша
class NW:
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
        self.matrix = [[(i * gap, self.COD_LEFT) for i in range(len(chain_a) + 1)]]
        # Пробегаем по каждой букве цепочки B, тем самым заполняем оставшиеся строки
        for i, b in enumerate(chain_b):
            # Запоминаем верхнуюю строку (последняя заполненная строка)
            upline = self.matrix[-1]
            # Первый элемент текущей строки строится на основе индекса буквы и значения штрафа за gap
            line = [((i+1) * gap, self.COD_UP)]
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
                # В качестве элемента берем максимальное значение
                # При одинаковых оценках берется элемент с наибольшим кодом направления
                # gap_B < compare < gap_A (по умолчанию)
                # Меня коды можно достич нужного нам выбора
                line.append(max(e1, e2, e3))
            # Добавляем строку в матрицу
            self.matrix.append(line)

    def out(self):
        """
        Получение результата
        :return: score, chain a, chain b
        """
        # Устанавливаем "курсор" на последний элемент матрицы
        i = len(self.chain_a)
        j = len(self.chain_b)
        # Изначально цепочки пустые
        a = ''
        b = ''
        # Score - значение последнего элемента
        rating = self.matrix[j][i][0]
        # Идем до тех пор, пока "курсор" не будет указывать на первый элемент
        while i + j != 0:
            # Получаем код направления
            cod = self.matrix[j][i][1]
            # Если код направления "лево"
            if cod == self.COD_LEFT:
                # К выравненной цеопчки A приписываем символ из цеопчки A (под соответствующем индексом)
                a += self.chain_a[i-1]
                # К цепочке B приписываем gap
                b += self.GAP_CHAR
                # Сдвигаем "курсор" влево
                i -= 1
            elif cod == self.COD_UP_LEFT:
                # К выравненной цеопчки A приписываем символ из цеопчки A (под соответствующем индексом)
                a += self.chain_a[i-1]
                # К выравненной цеопчки B приписываем символ из цеопчки B (под соответствующем индексом)
                b += self.chain_b[j-1]
                # Сдвигаем "курсор" влево и вверх
                i -= 1
                j -= 1
            else:
                # К цепочке A приписываем gap
                a += self.GAP_CHAR
                # К выравненной цеопчки B приписываем символ из цеопчки B (под соответствующем индексом)
                b += self.chain_b[j-1]
                # Сдвигаем "курсор" в вверх
                j -= 1
        return rating, a[::-1], b[::-1]
