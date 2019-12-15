import itertools
import io
import sys

# Путь к цепочкам FASTA
PATH_FASTA = "uniprot_sprot.fasta"
# Путь к файлу базы данных
PATH_DB = "fasta.db"
# Алфавит белков
ABC = "ABCDEFGHIJKLMNOPQRSTUVWYZX"
# Длина подцепочек
LENSS = 2
# Отображение подцепочки в код
SS2COD = {
    ''.join(key): value
    for value, key in enumerate(itertools.product(*[ABC] * LENSS))
}
# Максимальное число диагоналей, для которых производится вычисление промежуточного скора
COUNT_DIAG = 10
# Максимальное число гэпов
MAX_GAP = 5
# Минимальное число совпадений на диагонали
MIN_coincidence = 10
# Штраф за гэп
GAP = -4


# Чтение матрицы из файла
def parse_matrix(path):
    d = {}
    with open(path) as f:
        line = f.readline().strip()
        while line.startswith('#'):
            line = f.readline().strip()
        keys = [k for k in line.upper().split() if k]
        line = f.readline().strip()
        while line:
            k1, *values = [k for k in line.split() if k]
            for k2, value in zip(keys, values):
                d[(k1.upper(), k2)] = int(value)
            line = f.readline().strip()
    return d


# Кодирование чисел в байты
def encode_int(n):
    return n.to_bytes(2, byteorder='big', signed=False)


# Кодирование позиций подцепочек
def encode_seq_decomposition(sequence):
    out = [b''] * len(SS2COD)
    for i in range(len(sequence) - LENSS + 1):
        out[SS2COD[sequence[i:i + LENSS]]] += encode_int(i)
    return out


# Кодирование цепочки в базу данных
def encode_sequence(name, sequence):
    b_name = name.encode('utf-8')
    out = encode_int(len(b_name)) + b_name

    b_sequence = sequence.encode('utf-8')
    out += encode_int(len(b_sequence)) + b_sequence

    decomposition = encode_seq_decomposition(sequence)
    for cod, positions in enumerate(decomposition):
        if positions:
            out += encode_int(cod) + encode_int(len(positions) // 2) + positions

    return out


# Создание файла базы данных из цепочек fasta
def parse_fasta(path_fasta, path_out):
    with open(path_fasta) as f, open(path_out, 'wb') as out:
        line = f.readline().strip()
        while line:
            name = line[1:]
            buf = []
            line = f.readline().strip().upper()
            while not line.startswith('>') and line:
                buf.append(line)
                line = f.readline().strip().upper()

            sequence = ''.join(buf)
            bseq = encode_sequence(name, sequence)
            out.write(len(bseq).to_bytes(3, byteorder='big', signed=False) + bseq)


# Раскодирование числа из байтов
def decode_int(b):
    return int.from_bytes(b, byteorder='big', signed=False)


# Раскодирование цепочки из базы данных
def decode_sequence(byte_string):
    f = io.BytesIO(byte_string)
    name = f.read(decode_int(f.read(2))).decode('utf-8')
    sequence = f.read(decode_int(f.read(2))).decode('utf-8')
    yield name, sequence
    bcod = f.read(2)
    while bcod:
        cod = decode_int(bcod)
        poss = tuple(
            decode_int(f.read(2))
            for _ in range(decode_int(f.read(2)))
        )
        yield cod, poss
        bcod = f.read(2)


def main():
    import time
    path_fasta = sys.argv[1]
    path_db = sys.argv[2]
    print("Create DB (Ждите 300 секунд)")
    t1 = time.time()
    parse_fasta(path_fasta, path_db)
    t2 = time.time()
    print("Время выполнения:", t2 - t1)


if __name__ == '__main__':
    main()
