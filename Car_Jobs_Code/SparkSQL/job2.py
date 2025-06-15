from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, split, explode, count, avg,
    row_number, collect_list, concat_ws, when, length
)
from pyspark.sql.window import Window

# Inizializza Spark
spark = SparkSession.builder \
    .appName("UsedCarsAnalysis") \
    .enableHiveSupport() \
    .config("spark.sql.shuffle.partitions", "50") \
    .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

# Caricamento dati
df = spark.sql("""
SELECT city, year, daysonmarket, price, description
FROM used_cars_hive
""")

# Crea la colonna 'band'
df = df.withColumn(
    "band",
    when(col("price") < 20000, "low")
    .when(col("price") <= 50000, "medium")
    .otherwise("high")
).select("city", "year", "daysonmarket", "band", "description")

# Parte 1: Statistiche base
stats_df = df.groupBy("city", "year", "band").agg(
    count("*").alias("num_cars"),
    avg("daysonmarket").alias("avg_daysonmarket")
).persist()

# Parte 2: Parole (descrizioni già pulite)
words_df = df.select("city", "year", "band", "description") \
    .withColumn("word", explode(split(col("description"), "\\s+"))) \
    .filter((col("word") != "") & (length(col("word")) > 2))  # parole di almeno 3 lettere

# Conta parole
word_counts = words_df.groupBy("city", "year", "band", "word").agg(
    count("*").alias("word_count")
)

# Top 3 parole per gruppo, con ordinamento secondario per parola (tie-break)
window_spec = Window.partitionBy("city", "year", "band") \
    .orderBy(col("word_count").desc(), col("word").asc())

top_words = word_counts.withColumn("rank", row_number().over(window_spec)) \
    .filter(col("rank") <= 3)

# Aggregazione parole in una stringa
top3_formatted = top_words.groupBy("city", "year", "band").agg(
    concat_ws(",", collect_list("word")).alias("top_words")
)

# Join finale con statistiche
final_df = stats_df.join(top3_formatted, on=["city", "year", "band"], how="left")

# Mostra output finale
final_df.orderBy("city", "year", "band").select(
    "city", "year", "band", "num_cars", "avg_daysonmarket", "top_words"
).show(10, truncate=False)

spark.stop()
