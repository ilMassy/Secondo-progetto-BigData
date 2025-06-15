from pyspark import SparkContext
import argparse
import csv
from collections import Counter

def get_band(price):
    if price < 20000:
        return "low"
    elif price <= 50000:
        return "medium"
    else:
        return "high"

def parse_line(line):
    try:
        parts = next(csv.reader([line]))
        city = parts[0]
        daysonmarket = int(parts[1])
        description = parts[2]
        price = float(parts[3])
        year = int(parts[4])
        band = get_band(price)
        return (city, year, band, daysonmarket, description)
    except:
        return None

def map_to_key_value_v2(record):
    city, year, band, daysonmarket, description = record
    words = [w for w in description.strip().split() if len(w) > 2]
    word_counter = Counter(words)
    return ((city, year, band), (1, daysonmarket, word_counter))

def reduce_values(v1, v2):
    count1, days1, counter1 = v1
    count2, days2, counter2 = v2
    count = count1 + count2
    days = days1 + days2
    counter1.update(counter2)
    return (count, days, counter1)

def compute_final(record):
    key, (count, days, word_counter) = record
    avg_days = days / count if count > 0 else 0
    top3 = sorted(word_counter.items(), key=lambda x: (-x[1], x[0]))[:3]
    top3_words = ','.join([w for w, _ in top3])
    city, year, band = key
    return (city, year, band, count, round(avg_days, 2), top3_words)

def main():
    parser = argparse.ArgumentParser(description="Spark Core Used Cars Analysis")
    parser.add_argument("--input_path", required=True, help="Input file path (local or hdfs)")
    parser.add_argument("--output_path", required=True, help="Output directory path")
    args = parser.parse_args()

    sc = SparkContext(appName="UsedCarsSparkCore")

    lines = sc.textFile(args.input_path)
    header = lines.first()
    data = lines.filter(lambda line: line != header)

    parsed = data.map(parse_line).filter(lambda x: x is not None)
    mapped = parsed.map(map_to_key_value_v2)
    reduced = mapped.reduceByKey(reduce_values)
    final_rdd = reduced.map(compute_final)
    final_sorted = final_rdd.sortBy(lambda x: (x[0], x[1], x[2]))

    final_sorted.map(lambda x: "\t".join(map(str, x))).saveAsTextFile(args.output_path)

    for row in final_sorted.take(10):
        print("\t".join(map(str, row)))

    sc.stop()

if __name__ == "__main__":
    main()
