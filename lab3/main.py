from itertools import cycle
from operator import itemgetter


def default_metric(x, y):
    return 1 if x == y else -1


default_gap = -2


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

    def nw_mini(self, a, b):
        assert len(b) == 1
        pos, score = max(enumerate(map(self.metric, a, cycle(b))))
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
        a_le_b = len(a) <= len(b)
        if a_le_b:
            a, b = b, a

        if not len(b):
            x = a
            y = self.GAP_CHAR * len(a)
            score = self.gap * len(a)
        elif len(b) == 1:
            x, y, score = self.nw_mini(a, b)
        else:
            a_mid = len(a) // 2
            score_left = self.score_nw(b, a[:a_mid])
            score_right = self.score_nw(b[::-1], a[:a_mid-1:-1])

            b_mid, score = max(enumerate(map(int.__add__, score_left, score_right[::-1])), key=itemgetter(1))
            x, y = map(
                str.__add__,
                self.hirscheberg(a[:a_mid], b[:b_mid])[0],
                self.hirscheberg(a[a_mid:], b[b_mid:])[0]
            )
        return (y, x) if a_le_b else (x, y), score


def main():
    a = 'AATCG'
    b = 'AACG'
    print(a)
    print(b)
    print('===' * 3)
    (x, y), score = Hirscheberg(default_metric, default_gap, a, b).hirscheberg(a, b)
    print()
    print(x)
    print(y)
    print(score)


if __name__ == '__main__':
    main()
