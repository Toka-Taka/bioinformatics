from multiprocessing import Queue, Process, Manager
from itertools import product
import time
from nw import needleman_wunsch, NW
from utils import (
    SS2COD, LENSS, PATH_DB, decode_int, decode_sequence,
    COUNT_DIAG, MAX_GAP, parse_matrix, MIN_coincidence, GAP
)

# Число процессов
NUM_EXECUTOR = 20
# Размер очереди
QUEUE_SIZE = round(NUM_EXECUTOR * 1.3)

# Матрица BLOSUM62
M = parse_matrix('BLOSUM62')


# Функция, сравнивает два символа согласно матрице BLOSUM62
def metric(x, y):
    return M[(x, y)]


# Код одного исполнителя
def worker(seq_a, a_ss, q: Queue, out: list):
    # Максимальный скор
    max_score = 0
    # Имя цепочки с максимальным скором (из базы)
    b_name = ''
    # Сама цепочка
    b_sequence = ''
    # Усеченная входная цепочка
    a_short = ''
    # Усеченная выходная цепочка
    b_short = ''
    # Считываение цепочки из базы (в данном случае из очереди)
    data = q.get()
    while data is not None:
        # Раскодирование цепочки из базы
        block = decode_sequence(data)
        # Полечение имени и самой цепочки
        _name, seq_b = next(block)
        # Сравнение входной цепочки и цепочки из базы
        res = cmp(seq_a, a_ss, seq_b, block)
        # Если результат есть и скор больше максимального скора, то переписываем максимум
        if res and res[2] >= max_score:
            a_short, b_short, max_score = res
            b_name = _name
            b_sequence = seq_b
        # Получение следующей цепочки из базы (очереди) пока они там есть.
        data = q.get()
    # Возврат цепочки с максимальным скором
    out.append((
        max_score,
        b_name,
        b_sequence,
        b_short,
        a_short
    ))


# Сравнение двух цепочек
def cmp(a, a_ss, b, b_ss):
    # Создание массивов диагоналей (там будут храниться позиции совпадений)
    diags = [[] for _ in range(len(a) + len(b) - 1)]
    i = 0
    # Проход по всем подцепочкам двух цепочек и запоминание позиций совпадений
    for cod_b, b_poss in b_ss:
        while i < cod_b:
            i += 1
        if i == cod_b:
            for n, m in product(a_ss[i], b_poss):
                # noinspection PyTypeChecker
                diags[m - n].append(n)
            i += 1
    # Выбор 10 (COUNT_DIAG) диагоналей с наибольшим числом совпадений
    # Дополнительно отсеиваются все диагонали,
    # число совпадений на которых не превысило заданного минимума (MIN_coincidence)
    d_max = sorted(filter(lambda e: len(e[1]) > MIN_coincidence, enumerate(diags)), key=lambda x: len(x[1]))[-COUNT_DIAG:]
    _max = (0, ('', ''))
    # Подсчет промежуточного скора на этих диагоналях
    for d, poss in d_max:
        start = min(poss)
        end = max(poss) + 1
        sc = 0
        sa = a[start:end + 1]
        sb = b[d + start:d + end + 1]
        for ca, cb in zip(sa, sb):
            sc += metric(ca, cb)
        if sc >= _max[0]:
            _max = (sc, (sa, sb))
    sa, sb = _max[1]
    # Для диагонали с максимальным промежуточным скором (если такая найдена)
    # высчитывается полный скор (с учетом максимально возможного числа ГЭПОВ)
    if sa and sb:
        return sa, sb, needleman_wunsch(sa, sb, metric, GAP, MAX_GAP)
    return None


# Поиск максимально близкой цепочки из базы
def find(sequence):
    # Нахождение позиций для подпоследовательностей в введенной последовательности
    ss_poss = [[] for _ in range(len(SS2COD))]
    for i in range(len(sequence) - LENSS + 1):
        # noinspection PyTypeChecker
        ss_poss[SS2COD[sequence[i:i + LENSS]]].append(i)
    ss_poss = tuple(ss_poss)
    q = Queue(QUEUE_SIZE)
    manager = Manager()
    out = manager.list()
    # Создание процессов
    procs = [
        Process(target=worker, args=(sequence, ss_poss, q, out))
        for _ in range(NUM_EXECUTOR)
    ]
    # Запуск процессов
    for proc in procs:
        proc.start()
    # Открытие файла базы данных
    with open(PATH_DB, 'rb') as f:
        block_size = decode_int(f.read(3))
        i = 0
        while block_size:
            # Считывание цепочки из базы
            block = f.read(block_size)
            # Добавление цепочки в очередь
            q.put(block)
            block_size = decode_int(f.read(3))
            i += 1
    # Сигнал о завершении работы
    for _ in range(QUEUE_SIZE):
        q.put(None)
    # Ожидание завершения процессов
    for proc in procs:
        proc.join()
    # Получение результатов из исполнителей
    sout = sorted(out, reverse=True, key=lambda x: x[0])
    # Возврат цепочки с максимальным скором
    return sout


if __name__ == '__main__':
    t1 = time.time()
    # Ввод цепочки
    seq = input("Введите цепочку:").replace(' ', '').upper()
    print("Ждите. (примерно 220 секунд)")
    # Поиск наиболее подходящей подцепочки
    score, name, _, a_min, b_min = find(seq)[0]
    t2 = time.time()
    print("Время работы:", t2 - t1)
    print("Найденная цепочка:")
    print(name)
    print()
    print("Скор:", score)
    print("Усеченая входная цепочка:", a_min)
    print("Усеченая цеопчка из базы:", b_min)
    print("=" * 200)
    print()
    # Получение выравнивания
    print("Выравнивание с помощью полного алгоритма Нидельмана Вундша.))")
    new_score, new_a_min, new_b_min = NW(metric, GAP, a_min, b_min).out()
    print(new_a_min, '- входная цепочка')
    print(new_b_min, '- цепочка из базы')
    print('Новый скор:', new_score)
