from pyspark.sql import SparkSession
from pyspark.sql import Window
import pyspark.sql.functions as F
import os
import matplotlib
from pyspark.sql.types import BooleanType, StringType, IntegerType, DoubleType
import pandas as pd
import time

matplotlib.use("Agg")
import matplotlib.pyplot as plt

def data_transformation(df, output_path=None):
    # Task 1: Add column: rolling average on “Fwd Pkts/s” (grouped by IP) ------------------------------------------------------------

    # Window of 3 elements for each Src IP, ordered by Timestamp
    window_spec_fwd = Window.partitionBy("Src IP").orderBy("Timestamp").rowsBetween(-2, 0)

    df_with_avg = df.withColumn(
        "rolling_avg_fwd_pkts", 
        F.avg("Fwd Pkts/s").over(window_spec_fwd)
    )

    df_with_avg.select("Src IP", "Timestamp", "Fwd Pkts/s", "rolling_avg_fwd_pkts").show(10)

    # Task 2: Add column: rolling average on “Bwd Pkts/s” on another time interval (grouped by IP) ------------------------------------------------------------
    window_spec_bwd = Window.partitionBy("Src IP").orderBy("Timestamp").rowsBetween(-2, 0)

    df_with_avg = df_with_avg.withColumn(
        "rolling_avg_bwd_pkts", 
        F.avg("Bwd Pkts/s").over(window_spec_bwd)
    )

    df_with_avg.select("Src IP", "Timestamp", "Bwd Pkts/s", "rolling_avg_bwd_pkts").show(10)
                    
    # Task 3: Add two columns: column: (“Fwd Pkt Len Max” + “Fwd Pkt Len Min”)/2, by using spark functions and by using spark sql

    df_with_avg = df_with_avg.withColumn(
        "fwd_pkt_len_avg_spark_func",
        (F.col("Fwd Pkt Len Max") + F.col("Fwd Pkt Len Min")) / 2
    )

    df_with_avg.createOrReplaceTempView("df_with_avg")

    df_with_avg = spark.sql("""SELECT *, 
                        (`Fwd Pkt Len Max` + `Fwd Pkt Len Min`) / 2 AS fwd_pkt_len_avg_spark_sql
                        FROM df_with_avg""")

    df_with_avg.select("fwd_pkt_len_avg_spark_func", "fwd_pkt_len_avg_spark_sql").show(10)

    # Task 4: Calculate statistics on “Fwd Header Len” column (mean, min, max) by IP, 
    # create 3 histograms based on these statistics, and write these pictures to 3 files. ------------------------------------------------------------

    df_with_avg.createOrReplaceTempView("df_with_avg")

    statistic_on_fwd_header_len = spark.sql("""
        SELECT `Src IP`
            ,AVG(`Fwd Header Len`) AS mean_fwd_header_len 
            ,MIN(`Fwd Header Len`) AS min_fwd_header_len 
            ,MAX(`Fwd Header Len`) AS max_fwd_header_len
        FROM df_with_avg
        GROUP BY `Src IP`
    """)

    statistic_on_fwd_header_len.show(10)

    ip_count = statistic_on_fwd_header_len.select("Src IP").distinct().count()

    mean_res = statistic_on_fwd_header_len.select(
        F.histogram_numeric(F.col("mean_fwd_header_len"), F.lit(ip_count)).alias("hist")
    ).show(10)

    hist = statistic_on_fwd_header_len.select(
        F.histogram_numeric(F.col("min_fwd_header_len"), F.lit(ip_count)).alias("hist")
    ).show(10)

    max_res = statistic_on_fwd_header_len.select(
        F.histogram_numeric(F.col("max_fwd_header_len"), F.lit(ip_count)).alias("hist")
    ).show(10)


    def plot_by_ip(column,limit, filename):
        pdf = statistic_on_fwd_header_len.select("Src IP", column).toPandas()
        pdf = pdf.sort_values(column, ascending=False).head(limit)
        ax = pdf.plot.bar(
            x="Src IP",
            y=column,
            figsize=(12, 5),
            title=f"Top {limit} IPs by {column.replace('_', ' ').title()}"
        )
        ax.set_xlabel("Src IP")
        ax.set_ylabel(column)
        plt.xticks(rotation=90)
        fig = ax.get_figure()
        fig.savefig(filename, dpi=150, bbox_inches="tight")

    plot_by_ip("mean_fwd_header_len", 50, "mean_fwd_header_len_by_ip.png")
    plot_by_ip("min_fwd_header_len", 50, "min_fwd_header_len_by_ip.png")
    plot_by_ip("max_fwd_header_len", 50, "max_fwd_header_len_by_ip.png")


    # Task 5: Add column: create a pandas udf function which write to a new column 
    # boolean value true if value in the “Init Bwd Win Byts” 
    # column less than mean of this column, and write false otherwise. ------------------------------------------------------------
    mean_init_bwd_win_byts = df_with_avg.agg(F.mean("Init Bwd Win Byts")).first()[0]

    @F.pandas_udf(BooleanType())
    def is_below_mean_init_bwd_win_byts(values: pd.Series) -> pd.Series:
        return values < mean_init_bwd_win_byts

    df_with_avg = df_with_avg.withColumn(
        "is_below_mean_init_bwd_win_byts",
        is_below_mean_init_bwd_win_byts(F.col("Init Bwd Win Byts"))
    )

    df_with_avg.select("Init Bwd Win Byts", "is_below_mean_init_bwd_win_byts").show(10)

    # Task 6: Add two columns: create a pandas udf function which write to a new column 
    # a country based on the given IP address (“IP - Country” mappings can be found 
    # here https://datahub.io/core/geoip2-ipv4#data) for source and destination IP addresses. For unknown IPs set value to “unknown”. ------------------------------------------------------------

    # Because i have many workers, i will broadcast the mapping to all of them, 
    # so they can access it without needing to read the file multiple times
    geoip_pdf = pd.read_csv("geoip2-ipv4.csv")
    geoip_map = dict(zip(geoip_pdf["geoname_id"], geoip_pdf["country_name"]))
    geoip_broadcast = spark.sparkContext.broadcast(geoip_map)

    @F.pandas_udf(StringType())
    def get_country(ip: pd.Series) -> pd.Series:
        lookup = geoip_broadcast.value
        return ip.map(lambda value: lookup.get(value, "unknown"))

    df_with_avg = df_with_avg.withColumn(
        "Src Country",
        get_country(F.col("Src IP"))
    )

    df_with_avg = df_with_avg.withColumn(
        "Dst Country",
        get_country(F.col("Dst IP"))
    )

    df_with_avg.select("Src IP", "Src Country", "Dst IP", "Dst Country").show(10)

    # Task 7: Calculate percent of zeros in each numeric column and drop those 
    # columns that contain more than “threshold” percent of zeros, where 
    # “threshold" is defined based on the statistic: 93%-percentile of 
    # zeros distribution among all numeric columns. It means that 93% of 
    # columns have percent of zeros less than “threshold” and 7% of columns - more than “threshold”. 
    # Try different percentiles and choose the best based on the number of columns which will be dropped. -------------------------------------------------------------

    numeric_columns = [field.name for field in df_with_avg.schema.fields if (field.dataType == IntegerType() or field.dataType == DoubleType())]
    zero_percentages = {}
    for column in numeric_columns:
        total_count = df_with_avg.count()
        zero_count = df_with_avg.filter(F.col(column) == 0).count()
        zero_percentages[column] = (zero_count / total_count) * 100

    # thresholds = [96, 97, 98, 99, 99.5, 99.7, 99.9]
    # for threshold in thresholds:
    #     columns_to_drop = [col for col, percent in zero_percentages.items() if percent > threshold]
    #     print(f"Threshold: {threshold:.2f}%, Percent of columns to drop: {len(columns_to_drop) / len(numeric_columns) * 100:.2f}% ({len(columns_to_drop)} columns)")

    threshold = 99.7
    columns_to_drop = [col for col, percent in zero_percentages.items() if percent > threshold]
    #drop columns
    df_with_avg = df_with_avg.drop(*columns_to_drop)
    print("dropped columns:", columns_to_drop)

    # Task 8: Create a “data_transformation” function which encapsulates all the above transformations and applies them sequentially. ------------------------------------------------------------
    # Done

    # Task 9: Write the resulting Spark DataFrame to a csv file partitioned by IP address.
    if output_path:
        df_with_avg.write.mode("overwrite").option("header", "true").partitionBy("Src IP").csv(output_path)
    return df_with_avg

if __name__ == "__main__":
    # Task 11: Transform csv data file to parquet files, apply “data_transformation” function and analyze differences in performance.

    spark = SparkSession.builder \
        .appName("DDoS Attack Detection") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    csv_path = "ddos_dataset/ddos_imbalanced/unbalaced_20_80_dataset.csv"
    parquet_path = "ddos_dataset_parquet"

    # start = time.perf_counter()
    # df = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path)
    # data_transformation(df, "transformed_ddos_dataset_from_csv")
    # csv_elapsed = time.perf_counter() - start
    # print(f"CSV pipeline time: {csv_elapsed:.2f} seconds") # CSV pipeline time: 657.46 seconds   

    start = time.perf_counter()
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path)
    df.write.mode("overwrite").parquet(parquet_path)
    df_parquet = spark.read.parquet(parquet_path)
    data_transformation(df_parquet, "transformed_ddos_dataset_from_parquet")
    parquet_elapsed = time.perf_counter() - start
    print(f"Parquet pipeline time (including conversion): {parquet_elapsed:.2f} seconds") # Parquet pipeline time (including conversion): 390.32 seconds 

    spark.stop()