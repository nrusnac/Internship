import csv
import os
from datetime import timedelta

from airflow.sdk import dag, task
from airflow.providers.standard.sensors.external_task import ExternalTaskSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import DagRun
from airflow.utils.session import provide_session
from airflow.utils.state import DagRunState

DATA_DIR = "/opt/airflow/data"
INPUT_FILE = os.path.join(DATA_DIR, "ddos_sample.csv")

POSTGRES_CONN_ID = "ddos_postgres"
TABLE_NAME = "ddos_flows"

# Numeric columns we keep for easier insertion
COLUMNS = ["Src Port", "Dst Port", "Protocol", "Flow Duration",
           "Tot Fwd Pkts", "Tot Bwd Pkts"]

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id            SERIAL PRIMARY KEY,
    src_port      INTEGER,
    dst_port      INTEGER,
    protocol      INTEGER,
    flow_duration BIGINT,
    tot_fwd_pkts  INTEGER,
    tot_bwd_pkts  INTEGER,
    loaded_at     TIMESTAMP DEFAULT NOW()
);
"""


@dag(
    dag_id="ddos_b_load",
    schedule="0 * * * 1-5",
    catchup=False,
    tags=["ddos"],
)
def ddos_b_load():
    # Wait for DAG A's run in the same hour (both DAGs share the same schedule,
    # so execution_delta=0 matches A's run for this interval). Poke every 5 min,
    # fail after 10 min (two pokes).
    wait_for_a = ExternalTaskSensor(
        task_id="wait_for_ddos_a",
        external_dag_id="ddos_a_generate",
        external_task_id=None,
        execution_delta=timedelta(0),
        poke_interval=5 * 60,
        timeout=10 * 60,
        mode="reschedule",
        failed_states=["failed"],
    )

    @task
    def load_to_db():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        hook.run(CREATE_TABLE_SQL)

        with open(INPUT_FILE, newline="") as f:
            reader = csv.DictReader(f)
            rows = [tuple(int(float(r[c])) for c in COLUMNS) for r in reader]

        hook.insert_rows(
            table=TABLE_NAME,
            rows=rows,
            target_fields=["src_port", "dst_port", "protocol",
                           "flow_duration", "tot_fwd_pkts", "tot_bwd_pkts"],
        )
        print(f"Inserted {len(rows)} rows into {TABLE_NAME}")

    wait_for_a >> load_to_db()


ddos_b_load()


"""Check database
docker compose exec -T postgres psql -U airflow -d airflow -c "SELECT * FROM ddos_flows;"
"""