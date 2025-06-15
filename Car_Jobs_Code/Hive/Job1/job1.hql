-- 1. Creazione tabella esterna che punta al CSV su HDFS, salta header
DROP TABLE IF EXISTS used_cars_hive;
CREATE EXTERNAL TABLE used_cars_hive (
  make_name STRING,
  model_name STRING,
  price FLOAT,
  year INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar" = "\"",
  "escapeChar" = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/massimiliano/input';


-- 2. Creazione tabella aggregata per i risultati
DROP TABLE IF EXISTS job1_result;
CREATE TABLE IF NOT EXISTS job1_result (
  make_name STRING,
  model_name STRING,
  count INT,
  min_price FLOAT,
  max_price FLOAT,
  avg_price FLOAT,
  years_str STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ', '
STORED AS TEXTFILE;

-- 3. Inserimento dati aggregati nella tabella job1_result da cars_cleaned
-- Cancellazione e inserimento dati nella tabella "job1_result"
-- calcolo minimi e massimi su valori numerici, no stringhe
-- per il valore medio non c'è questo problema
-- 3. Inserimento dati aggregati nella tabella job1_result da cars_cleaned
-- Cancellazione e inserimento dati nella tabella "job1_result"
INSERT OVERWRITE TABLE job1_result
SELECT
  make_name,
  model_name,
  COUNT(*) AS count,
  MIN(CAST(price AS FLOAT)) AS min_price,
  MAX(CAST(price AS FLOAT)) AS max_price,
  AVG(price) AS avg_price,
  CONCAT('[', CONCAT_WS(',', SORT_ARRAY(COLLECT_SET(CAST(year AS STRING)))), ']') AS years_str
FROM used_cars_hive
WHERE price IS NOT NULL AND year IS NOT NULL
GROUP BY make_name, model_name;


