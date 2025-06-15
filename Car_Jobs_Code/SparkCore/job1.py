#!/usr/bin/env python3
import csv
import argparse
from pyspark import SparkContext, SparkConf

def parse_line(line):
    try:
        parts = next(csv.reader([line]))
        make = parts[0]
        model = parts[1]
        price = float(parts[2])
        year = int(parts[3])
        key = f"{make}|{model}"
        return (key, (1, price, price, price, [year]))
    except:
        return None

def merge_values(val1, val2):
    count1, min1, max1, sum1, years1 = val1
    count2, min2, max2, sum2, years2 = val2
    return (
        count1 + count2,
        min(min1, min2),
        max(max1, max2),
        sum1 + sum2,
        years1 + years2
    )

def format_output(record):
    key, (count, min_price, max_price, total_price, years) = record
    avg_price = round(total_price / count, 2)
    years_sorted = sorted(set(years))
    years_str = f"[{','.join(str(y) for y in years_sorted)}]"
    return f"{key}\t{count},{min_price},{max_price},{avg_price},{years_str}"

def main(input_path, output_path):
    conf = SparkConf().setAppName("UsedCarsAggregation")
    sc = SparkContext(conf=conf)

    lines = sc.textFile(input_path)
    header = lines.first()
    data = lines.filter(lambda line: line != header)

    parsed = data.map(parse_line).filter(lambda x: x is not None)
    aggregated = parsed.reduceByKey(merge_values)

    # Ordinamento per chiave "make|model"
    result = aggregated.sortBy(lambda x: x[0]).map(format_output)

    # Stampa delle prime 10 righe
    for line in result.take(10):
        print(line)

    # Salvataggio su HDFS o file system locale
    result.saveAsTextFile(output_path)
    sc.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, help="Percorso input (es. HDFS o file://)")
    parser.add_argument("--output_path", required=True, help="Percorso output (es. HDFS o file://)")
    args = parser.parse_args()

    main(args.input_path, args.output_path)
