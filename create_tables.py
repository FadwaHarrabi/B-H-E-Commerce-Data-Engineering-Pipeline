from datetime import datetime
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


with DAG(
    dag_id="create_tables",
    start_date=datetime(2026, 8, 31),
    schedule=None,
    catchup=False,
    template_searchpath="/opt/airflow/database",
) as dag:

    create_tables = SQLExecuteQueryOperator(
        task_id="create_tables",
        conn_id="bhp_postgres",
        sql="create_tables.sql",
        database="bhphotovideo",
    )