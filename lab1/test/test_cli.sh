#!/usr/bin/env bash
rm -f log.txt
# Тестирование по умолчанию
if ! python ../nw.py FAST/one.fast FAST/one.fast >> log.txt; then
    echo "Error test 1"
    exit 1
fi
# Тестирование алфавита
# Аминокислот
if python ../nw.py -a FAST/one.fast FAST/wrong.fast >> log.txt; then
    echo "Error test 2"
    exit 1
fi

if ! python ../nw.py -a FAST/one.fast FAST/amino.fast >> log.txt; then
    echo "Error test 3"
    exit 1
fi
if ! python ../nw.py -a FAST/one.fast FAST/nucleotide.fast >> log.txt; then
    echo "Error test 4"
    exit 1
fi
# Нуклеотидов
if python ../nw.py -n FAST/one.fast FAST/wrong.fast >> log.txt; then
    echo "Error test 5"
    exit 1
fi
if python ../nw.py -n FAST/one.fast FAST/amino.fast >> log.txt; then
    echo "Error test 6"
    exit 1
fi
if ! python ../nw.py -n FAST/one.fast FAST/nucleotide.fast >> log.txt; then
    echo "Error test 7"
    exit 1
fi

# Тестирование аргуметов
if ! python ../nw.py FAST/two.fast >> log.txt; then
    echo "Error test 8"
    exit 1
fi
if python ../nw.py FAST/three.fast >> log.txt; then
    echo "Error test 9"
    exit 1
fi
if python ../nw.py FAST/one.fast FAST/two.fast >> log.txt; then
    echo "Error test 10"
    exit 1
fi
if python ../nw.py FAST/one.fast FAST/three.fast >> log.txt; then
    echo "Error test 11"
    exit 1
fi
