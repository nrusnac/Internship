# Airflow Tasks

This folder contains the work for the Airflow part of the internship. The DAGs
themselves live in [`../dags/`](../dags/); this README explains how each task was
implemented.

## Running

Airflow runs locally via the [`docker-compose.yaml`](./docker-compose.yaml)
(CeleryExecutor + Postgres + Redis). Bring it up with:

```bash
docker compose up -d        # web UI at http://localhost:8080 (airflow / airflow)
```

The DAGs in `../dags/` are mounted into the containers, so editing a file there
updates Airflow after a reserialize.

A connection named `postgres_default` (pointing at the Postgres above) must exist
for the database tasks to work.

## Task 1 — Dynamically generated pipeline DAGs

File: [`../dags/jobs_dag.py`](../dags/jobs_dag.py)

Three DAGs (`users_pipeline`, `products_pipeline`, `orders_pipeline`) are
generated from a single `config` dict by a `create_dag()` factory and registered
with `globals()[dag_id] = ...`. Each pipeline:

1. **`print_process_start`** — `PythonOperator` logging the start.
2. **`get_current_user`** — `BashOperator` running `whoami`, pushing the result to XCom.
3. **`check_table_exists`** — `BranchPythonOperator` querying `information_schema.tables`
   via a `PostgresHook`. Branches to `create_table` if missing, else straight to `insert_row`.
4. **`create_table` / `insert_row`** — `SQLExecuteQueryOperator`s. `insert_row` uses
   `trigger_rule="none_failed"` so it runs whether or not the table was just created,
   and inserts the username pulled from XCom.
5. **`query_table`** — a **custom operator** `PostgreSQLCountRows`
   ([`postgresql_count_rows.py`](../dags/postgresql_count_rows.py)) that returns the
   row count (auto-pushed to XCom).
6. **`push_run_ended`** — pushes a completion message and this run's `logical_date`
   to XCom so the trigger DAG can find this exact run.

## Task 2 — Trigger DAG (sensor → trigger → process)

File: [`../dags/trigger_dag.py`](../dags/trigger_dag.py)

1. **`sensor_wait_run_file`** — `FileSensor` waiting for a `run` file in
   `trigger_folder/` (the filename comes from the `path_variable` Airflow Variable).
2. **`Trigger_DAG`** — `TriggerDagRunOperator` that triggers `users_pipeline`.
3. **`process_results`** (a `task_group`):
   - `ExternalTaskSensor` waits for the triggered run to succeed, locating it via the
     `logical_date` published in XCom (`execution_date_fn`).
   - `print_result` pulls the cross-DAG XCom message.
   - removes the `run` file, then creates a `finished_<timestamp>` file.
   - `notify_slack` — placeholder `EmptyOperator`; the real Slack notification is kept
     commented (no paid Slack access). The token is meant to be read from HashiCorp
     Vault via the Variable backend.

## Other example DAGs

The `../dags/` folder also holds smaller examples built while learning the concepts:
`branching.py` (BranchPythonOperator per weekday), `triggers.py` (TaskFlow `@task.branch`),
`xcom_example.py` / `xcom_cross_dag.py` (XCom), and `dynamic_dags.py`.
