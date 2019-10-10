import getopt
import os
import re
import sys
from itertools import zip_longest, chain

__version__ = '0.1'

D_MATRIX_AMINO = os.path.join(os.path.dirname(__file__), 'BLOSUM62')
D_MATRIX_NUCLEOTIDE = os.path.join(os.path.dirname(__file__), 'DNAfull')
D_GAP = -2
ABC_AMINO = 'ARNDCQEGHILKMFPSTWYVBZX'
ABC_NUCLEOTIDE = 'ATGCSWRYKMBVHDN'
MAX_SIZE_LINE = 100


def _exit(msg, code=1):
    """
    Вывод сообщения об ошибке и выход

    :param msg: Сообщение
    :param code: Код ошибки
    :return:
    """
    print(msg)
    sys.exit(code)


def default_metric(x, y):
    """
    Метрика по умолчанию

    :param x: Буква из первой строки
    :param y: Буква из второй строки
    :return: 1, если x == y, иначе -1
    """
    return 1 if x == y else -1


def read_matrix(path, delimiter=None):
    """
    Чтение матрицы из файла
    В файле могут быть комментарии, начинающиеся с #

    :param path: Путь к файлу
    :param delimiter: Разделитель (по умолчанию пробел и табуляция)
    :return: Метрика (функция), которая сопоставляет паре букв численное значение
    """
    with open(path) as f:
        matrix = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                matrix.append(list(filter(None, line.split(delimiter))))
        if len(matrix) < 2:
            _exit('Empty matrix')
        if len(matrix[0]) == len(matrix[1]) - 1:
            matrix[0].insert(0, '')
        for li in matrix:
            if len(li) != len(matrix):
                _exit('Wrong size matrix')

        keys = [k.upper() for k in matrix[0][1:]]
        s = {}
        for li in matrix[1:]:
            key, *values = li
            s.update(zip(zip_longest([], keys, fillvalue=key.upper()), map(int, values)))

        if len(s) != (len(matrix) - 1) ** 2:
            raise _exit('Duplicate keys')

        return lambda x, y: s[(x, y)]


def read_fast(path):
    """
    Считывание FAST

    :param path: Путь к файлу
    :return: Список цепочек FAST в формате: (описание, цепочка)
    """
    with open(path) as f:
        cleaner = re.compile(r'\s[0-9]')
        chains = []
        buf = []
        name = ''
        for line in f:
            line = line.strip()
            if line:
                if line.startswith('>'):
                    chains.append((name, ''.join(buf)))
                    name = line
                    buf = []
                else:
                    buf.append(cleaner.sub('', line).upper())
        if buf:
            chains.append((name, ''.join(buf)))
        return chains[1:]


def read_args():
    """
    Считывание аргуметров командной строки
    -a, --amino: Флаг указывающий на последовательность аминокислот
    -n, --nucleotide: Флаг указывающий на последовательность нуклеотидов
    -h, --help: Информация об опциях программы
    -V, --version: Версия программы
    -g, --gap <int>: Штраф за gap (по умолчанию -2)
    -m, --matrix <path>: Путь к матрице описывающей метрику.
                         По умолчанию:
                         -- для аминокислот - матрица BLOSUM62
                         -- для нуклеотидов - матрица DNAFull
                         -- для произвольных цепочек: совпадение +1, не совпадение -1
    -o, --output <path>: Путь куда записывать результат (по умполчанию stdout)

    :return:
    """
    optlist = []
    args = []
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'anhVg:m:o:', [
            'amino',
            'nucleotide',
            'help',
            'version',
            'gap=',
            'matrix=',
            'output=',
        ])
    except getopt.GetoptError as err:
        _exit(err, 2)

    amino = False
    nucleotide = False
    gap = None
    metric = None
    output = None

    for o, a in optlist:
        if o in ('-a', '--amino'):                     # Amino
            amino = True
        elif o in ('-n', '--nucleotide'):              # Nucleotide
            nucleotide = True
        elif o in ('-h', '--help'):                    # Help
            _exit(open('README.md').read(), 0)
        elif o in ('-V', '--version'):                 # Version
            _exit(__version__, 0)
        elif o in ('-g', '--gap'):                     # Gap
            gap = int(a)
        elif o in ('-m', '--matrix'):                  # Matrix
            metric = read_matrix(a)
        elif o in ('-o', '--output'):                  # Output
            output = a

    if amino and nucleotide:
        # Если используются флаги -a и -n одновременно, то ошибка
        _exit('Нужно выбрать только один тип для сравнения')
    elif amino:
        metric = metric or read_matrix(D_MATRIX_AMINO)
    elif nucleotide:
        metric = metric or read_matrix(D_MATRIX_NUCLEOTIDE)
    else:
        metric = metric or default_metric

    gap = gap or D_GAP

    if not (1 <= len(args) <= 2):
        # Если не заданы пути к fast файлам или их больше двух, то ошибка
        _exit('Wrong parameters\nTry \'python nw.py --help\' for more information.')
    chains = []
    for a in args:
        chains.extend(read_fast(a))
    if len(chains) != 2:
        # Если суммарно в файлах количество цепочек != 2, то ошибка
        _exit('Not found two chains or found many chains')

    # Проверка алфавита в цепочках, для случая по умолчанию проверка не производится
    if amino:
        for _, c in chains:
            if c.strip(ABC_AMINO):
                _exit('Недопустимые символы в цепочке аминокислот: {}'.format(c))
    elif nucleotide:
        for _, c in chains:
            if c.strip(ABC_NUCLEOTIDE):
                _exit('Недопустимые символы в цепочке нуклеотидов: {}'.format(c))
    return metric, gap, chains, output


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


def write_output(output, rating, a, b):
    buffer = '\n'.join(chain(
        (
            line
            for prefix, ch in [('Chain 1:', a), ('Chain 2:', b)]
            for line in chain(
                (prefix,),
                (
                    ch[i:i + MAX_SIZE_LINE]
                    for i in range(0, len(ch), MAX_SIZE_LINE)
                ),
                ('', '')
            )
        ),
        ('Score:', str(rating))
    ))
    if output:
        with open(output, 'w') as f:
            f.write(buffer)
    else:
        print()
        print(buffer)
        print()


def main():
    print('Start')
    try:
        metric, gap, [(_, chain_1), (_, chain_2)], output = read_args()
    except ImportError as e:
        _exit('Ошибка входных данных\n{}'.format(e))
        return
    print('Input success')
    try:
        nw = NW(metric, gap, chain_1, chain_2)
    except ImportError as e:
        _exit('Ошибка при построении матрицы\n{}'.format(e))
        return
    print('Make matrix success')
    try:
        write_output(output, *nw.out())
    except ImportError as e:
        _exit('Ошибка при выводе результата\n{}'.format(e))
        return
    print('Success')


if __name__ == '__main__':
    main()
