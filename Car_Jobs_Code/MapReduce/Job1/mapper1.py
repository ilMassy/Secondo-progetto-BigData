#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)
header = next(reader)  # salta intestazione

for row in reader:
    try:
        make = row[0]
        model = row[1]
        price = float(row[2])
        year = row[3]
        print(f"{make}|{model}\t1,{price},{price},{price},{year}")
    except:
        continue
