import csv
import os
import random

from airflow.sdk import dag, task

# Mounted from Tasks/data on the host
DATA_DIR = "/opt/airflow/data"
SOURCE_FILE = os.path.join(DATA_DIR, "1_0_176_98_transformed_ddos_dataset_pandas.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "ddos_sample.csv")

N_LINES = 10


@dag(
    dag_id="ddos_a_generate",
    schedule="0 * * * 1-5",
    catchup=False,
    tags=["ddos"],
)
def ddos_a_generate():
    @task
    def generate_sample():
        with open(SOURCE_FILE, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)

        sample = random.sample(rows, N_LINES)

        with open(OUTPUT_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(sample)

        print(f"Wrote {len(sample)} random lines to {OUTPUT_FILE}")
        return OUTPUT_FILE

    generate_sample()


ddos_a_generate()
