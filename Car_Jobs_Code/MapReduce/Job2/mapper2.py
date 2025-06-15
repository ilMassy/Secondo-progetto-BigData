#!/usr/bin/env python3
import sys
import csv

first_line = True

for line in sys.stdin:
    if first_line:
        first_line = False
        continue
    line = line.strip()
    if not line:
        continue
    try:
        row = next(csv.reader([line]))
        city, year, price_str, dom_str, desc = row[0], row[4], row[3], row[1], row[2]
        price = float(price_str)
        dom = int(dom_str)

        if price < 20000:
            band = "low"
        elif price <= 50000:
            band = "medium"
        else:
            band = "high"

        group_key = f"{city}::{year}::{band}"

        print(f"{group_key}\tCAR::{dom}")

        for word in desc.strip().split():
            if len(word) > 2:
                print(f"{group_key}\tWORD::{word}")
    except Exception:
        continue
