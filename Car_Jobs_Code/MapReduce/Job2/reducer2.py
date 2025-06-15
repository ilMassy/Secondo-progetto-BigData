#!/usr/bin/env python3
import sys
from collections import Counter

current_key = None
car_count = 0
sum_dom = 0
words = Counter()

for line in sys.stdin:
    line = line.strip()
    try:
        key, value = line.split("\t")
        parts = value.split("::")
    except ValueError:
        continue

    if current_key != key:
        if current_key is not None:
            top3 = ','.join([w for w, _ in sorted(words.items(), key=lambda x: (-x[1], x[0]))[:3]])
            avg_dom = sum_dom / car_count if car_count > 0 else 0
            print(f"{current_key}\t{car_count}\t{avg_dom:.2f}\t{top3}")
        current_key = key
        car_count = 0
        sum_dom = 0
        words = Counter()

    if parts[0] == "CAR":
        try:
            dom = int(parts[1])
            car_count += 1
            sum_dom += dom
        except:
            continue
    elif parts[0] == "WORD":
        word = parts[1]
        words[word] += 1

if current_key is not None:
    top3 = ','.join([w for w, _ in sorted(words.items(), key=lambda x: (-x[1], x[0]))[:3]])
    avg_dom = sum_dom / car_count if car_count > 0 else 0
    print(f"{current_key}\t{car_count}\t{avg_dom:.2f}\t{top3}")
