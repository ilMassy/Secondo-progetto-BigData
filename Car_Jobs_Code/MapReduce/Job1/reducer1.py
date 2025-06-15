#!/usr/bin/env python3
import sys

current_key = None
count = 0
price_sum = 0
price_min = float('inf')
price_max = float('-inf')
years = set()

for line in sys.stdin:
    key, values = line.strip().split('\t')
    n, pmin, pmax, psum, year = values.split(',')
    n, pmin, pmax, psum = int(n), float(pmin), float(pmax), float(psum)

    if key != current_key:
        if current_key:
            avg = round(price_sum / count, 2)
            print(f"{current_key}\t{count},{price_min},{price_max},{avg},{sorted(years)}")
        current_key = key
        count = 0
        price_sum = 0
        price_min = float('inf')
        price_max = float('-inf')
        years = set()

    count += n
    price_sum += psum
    price_min = min(price_min, pmin)
    price_max = max(price_max, pmax)
    years.add(year)

# ultimo gruppo
if current_key:
    avg = round(price_sum / count, 2)
    print(f"{current_key}\t{count},{price_min},{price_max},{avg},{sorted(years)}")
