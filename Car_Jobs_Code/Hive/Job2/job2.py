from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("UsedCarsHiveSQL") \
    .enableHiveSupport() \
    .getOrCreate()

# Esegui tutto in SQL senza creazione di dataframe
spark.sql("""
WITH banded AS (
  SELECT 
    city,
    year,
    daysonmarket,
    description,
    CASE 
      WHEN price < 20000 THEN 'low'
      WHEN price <= 50000 THEN 'medium'
      ELSE 'high'
    END AS band
  FROM used_cars_hive
),

base_stats AS (
  SELECT 
    city, year, band,
    COUNT(*) AS num_cars,
    ROUND(AVG(daysonmarket), 2) AS avg_daysonmarket
  FROM banded
  GROUP BY city, year, band
),

word_counts AS (
  SELECT 
    city, year, band, word, COUNT(*) as word_count
  FROM (
    SELECT 
      city, year, band,
      explode(split(description, ' ')) as word
    FROM banded
  ) tmp
  WHERE LENGTH(word) > 2
  GROUP BY city, year, band, word
),

ranked_words AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY city, year, band 
      ORDER BY word_count DESC, word ASC
    ) as rank
  FROM word_counts
),

top3_words AS (
  SELECT city, year, band,
    concat_ws(',', collect_list(word)) as top_words
  FROM ranked_words
  WHERE rank <= 3
  GROUP BY city, year, band
)

SELECT 
  s.city, s.year, s.band,
  s.num_cars,
  s.avg_daysonmarket,
  COALESCE(t.top_words, '') AS top_words
FROM base_stats s
LEFT JOIN top3_words t
ON s.city = t.city AND s.year = t.year AND s.band = t.band
ORDER BY s.city, s.year, s.band
""").show(10, truncate=False)

spark.stop()
