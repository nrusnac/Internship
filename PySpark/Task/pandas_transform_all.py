import pandas as pd

#Task 10: Write approval code: for example, create a separate file containing data 
# related to one IP address, and calculate all the above columns by using pandas and 
# compare to the file written by using PySpark.

INPUT_CSV = "ddos_dataset/ddos_imbalanced/unbalaced_20_80_dataset.csv"
GEOIP_CSV = "geoip2-ipv4.csv"
OUTPUT_CSV = "transformed_ddos_dataset_pandas.csv"
TARGET_IP = "1.0.176.98"


def add_rolling_averages(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.sort_values(["Src IP", "Timestamp"]).reset_index(drop=True)

    df["rolling_avg_fwd_pkts"] = (
        df.groupby("Src IP")["Fwd Pkts/s"]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    df["rolling_avg_bwd_pkts"] = (
        df.groupby("Src IP")["Bwd Pkts/s"]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    return df


def add_fwd_pkt_len_avg(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fwd_pkt_len_avg_spark_func"] = (
        df["Fwd Pkt Len Max"] + df["Fwd Pkt Len Min"]
    ) / 2
    df["fwd_pkt_len_avg_spark_sql"] = df["fwd_pkt_len_avg_spark_func"]
    return df


def add_init_bwd_win_flag(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mean_init_bwd_win_byts = df["Init Bwd Win Byts"].mean()
    df["is_below_mean_init_bwd_win_byts"] = (
        df["Init Bwd Win Byts"] < mean_init_bwd_win_byts
    )
    return df


def add_country_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    geoip_pdf = pd.read_csv(GEOIP_CSV)
    if "geoname_id" in geoip_pdf.columns and "country_name" in geoip_pdf.columns:
        geoip_map = dict(zip(geoip_pdf["geoname_id"], geoip_pdf["country_name"]))
    else:
        geoip_map = {}
    df["Src Country"] = df["Src IP"].map(lambda value: geoip_map.get(value, "unknown"))
    df["Dst Country"] = df["Dst IP"].map(lambda value: geoip_map.get(value, "unknown"))
    return df


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    df = df[df["Src IP"] == TARGET_IP].copy()
    df = add_rolling_averages(df)
    df = add_fwd_pkt_len_avg(df)
    df = add_init_bwd_win_flag(df)
    df = add_country_columns(df)
    output_path = f"{TARGET_IP.replace('.', '_')}_{OUTPUT_CSV}"
    df.to_csv(output_path, index=False)
    print(f"Wrote pandas output to {output_path}")


if __name__ == "__main__":
    main()
