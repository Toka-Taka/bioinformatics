def needleman_wunsch(a, b, metric, gap, n):
    n = min(len(a), n)
    len_window = min(2 * n - 1, len(a))
    x = n
    y = max(len(a) - n + 1, n)

    c = metric(a[0], b[0])
    line = [c + i * gap for i in range(n)] + [None] * (len_window - n)

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
    return line[-1]


def d_metric(a, b):
    return 1 if a == b else -1

"""
    for i, ca in enumerate(a[y:]):
        print(line)
        e2 = line[i] + metric(ca, b[i + 1])
        e3 = line[i + 1] + gap
        c, line[i + 1] = line[i + 1], max(e2, e3)
        for j, cb in enumerate(b[-len_window + i + 2:]):
            e1 = line[j + i + 1] + gap
            e2 = c + metric(ca, cb)
            e3 = line[j + i + 3] + gap
            c, line[j + i + 1] = line[j + i + 1], max(e1, e2, e3)
        line[i] = None
    print(line)
"""