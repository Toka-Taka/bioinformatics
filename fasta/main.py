from itertools import product
import time
from nw import needleman_wunsch
from utils import (
    SS2COD, LENSS, PATH_DB, decode_int, decode_sequence,
    COUNT_DIAG, MAX_GAP, parse_matrix, MIN_coincidence, GAP
)

M = parse_matrix('BLOSUM62')


def metric(x, y):
    return M[(x, y)]


def find(sequence):
    ss_poss = [[] for _ in range(len(SS2COD))]
    for i in range(len(sequence) - LENSS + 1):
        # noinspection PyTypeChecker
        ss_poss[SS2COD[sequence[i:i + LENSS]]].append(i)

    ss_poss = tuple(ss_poss)

    _max = (0, ('', '', '', ''))

    with open(PATH_DB, 'rb') as f:
        block_size = decode_int(f.read(3))
        while block_size:
            block = decode_sequence(f.read(block_size))
            name, db_sequence = next(block)
            out = cmp(sequence, ss_poss, db_sequence, block)
            if out:
                sa, sb, score = out
                if score > _max[0]:
                    _max = (score, (name, sequence, db_sequence, sa, sb))
            block_size = decode_int(f.read(3))
    return _max


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


if __name__ == '__main__':
    t1 = time.time()
    max_score, seqs = find('NASLPRHLGISLLSCFPNVQMLPLDLRELFRDTPLADWYAAVQGRWEPYLLPVLSDASRI')
    t2 = time.time()
    print(t2 - t1)
    print(max_score)
    print(*seqs, sep='\n')
