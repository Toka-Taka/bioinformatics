from multiprocessing import Queue, Process, Manager
from itertools import product
import time
from nw import needleman_wunsch
from utils import (
    SS2COD, LENSS, PATH_DB, decode_int, decode_sequence,
    COUNT_DIAG, MAX_GAP, parse_matrix, MIN_coincidence, GAP
)
import os

NUM_EXECUTOR = 20
QUEUE_SIZE = round(NUM_EXECUTOR * 1.3)

M = parse_matrix('BLOSUM62')


def metric(x, y):
    return M[(x, y)]


def worker(seq_a, a_ss, q: Queue, out: list):
    print('process id:', os.getpid())

    max_score = 0
    b_name = ''
    b_sequence = ''
    a_short = ''
    b_short = ''

    data = q.get()
    print(data)
    while data is not None:
        block = decode_sequence(data)
        name, seq_b = next(block)
        res = cmp(seq_a, a_ss, seq_b, block)
        if res and res[2] >= max_score:
            a_short, b_short, max_score = res
            b_name = name
            b_sequence = seq_b
        data = q.get()
    out.append((
        max_score,
        b_name,
        b_sequence,
        b_short,
        a_short
    ))


def cmp(a, a_ss, b, b_ss):
    diags = [[] for _ in range(len(a) + len(b) - 1)]
    i = 0
    for cod_b, b_poss in b_ss:
        while i < cod_b:
            i += 1
        if i == cod_b:
            for n, m in product(a_ss[i], b_poss):
                # noinspection PyTypeChecker
                diags[m - n].append(n)
            i += 1
    d_max = sorted(enumerate(diags), key=lambda x: len(x[1]))[-COUNT_DIAG:]
    _max = (0, ('', ''))
    for d, poss in filter(lambda e: len(e[1]) > MIN_coincidence, d_max):
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
    if sa and sb:
        return sa, sb, needleman_wunsch(sa, sb, metric, GAP, MAX_GAP)
    return None


def find(sequence):
    ss_poss = [[] for _ in range(len(SS2COD))]
    for i in range(len(sequence) - LENSS + 1):
        # noinspection PyTypeChecker
        ss_poss[SS2COD[sequence[i:i + LENSS]]].append(i)
    ss_poss = tuple(ss_poss)

    q = Queue(QUEUE_SIZE)
    manager = Manager()
    out = manager.list()
    procs = [
        Process(target=worker, args=(sequence, ss_poss, q, out))
        for _ in range(NUM_EXECUTOR)
    ]
    for proc in procs:
        proc.start()

    with open(PATH_DB, 'rb') as f:
        block_size = decode_int(f.read(3))
        i = 0
        while block_size:
            # if i == 1000:
            #     break
            block = f.read(block_size)
            q.put(block)
            block_size = decode_int(f.read(3))
            i += 1

    for _ in range(QUEUE_SIZE):
        q.put(None)

    for proc in procs:
        proc.join()

    sout = sorted(out, reverse=True)
    print(*sout, sep='\n')


if __name__ == '__main__':
    t1 = time.time()
    find('NASLPRHLGISLLSCFPNVQMLPLDLRELFRDTPLADWYAAVQGRWEPYLLPVLSDASRI')
    t2 = time.time()
    print(t2 - t1)
