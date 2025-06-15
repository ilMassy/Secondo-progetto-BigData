import sys
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, min, max, avg, collect_set, sort_array, concat_ws

def main(input_path, output_path):
    spark = SparkSession.builder.appName("MakeModelStatistics_Flat").getOrCreate()

    df = spark.read.option("header", "true") \
                   .option("inferSchema", "true") \
                   .csv(input_path)

    # Raggruppa per marca e modello, calcola statistiche
    agg_df = df.groupBy("make_name", "model_name") \
        .agg(
            count("*").alias("count"),
            min("price").alias("min_price"),
            max("price").alias("max_price"),
            avg("price").alias("avg_price"),
            sort_array(collect_set(col("year"))).alias("years_sorted")
        )

    # Trasforma lista anni in stringa
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType

    def format_years(years):
        return "[" + ",".join(str(y) for y in years) + "]"

    format_years_udf = udf(format_years, StringType())

    result_df = agg_df.withColumn("years_str", format_years_udf(col("years_sorted"))) \
                      .select(
                          "make_name",
                          "model_name",
                          "count",
                          "min_price",
                          "max_price",
                          "avg_price",
                          "years_str"
                      ) \
                      .orderBy("make_name", "model_name")

    # Stampa prime 10 righe (ordinate)
    result_df.show(10, truncate=False)

    # Salva output come CSV
    result_df.write.mode("overwrite").option("header", "true").csv(output_path)

    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, help="Percorso input (HDFS o locale)")
    parser.add_argument("--output_path", required=True, help="Percorso output (HDFS o locale)")
    args = parser.parse_args()

    main(args.input_path, args.output_path)
