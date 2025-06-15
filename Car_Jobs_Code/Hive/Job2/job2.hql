DROP TABLE IF EXISTS used_cars_hive;
CREATE EXTERNAL TABLE used_cars_hive (
  city STRING,
  daysonmarket INT,
  description STRING,
  price FLOAT,
  year INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\"",
  "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/massimiliano/input'
TBLPROPERTIES ("skip.header.line.count"="1");
