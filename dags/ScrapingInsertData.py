from airflow  import DAG 
from airflow.operators.python import PythonOperator
from datetime import datetime
from WebScraping.bhphotovideo import main
import asyncio
def webscraping():
    asyncio.run(main())
with DAG(
     dag_id="scraping_insert_data",
     start_date=datetime(2026, 3, 3),
     schedule="@daily",
     catchup=False,
) as dag:
    webscraping_task = PythonOperator(
         task_id="webscraping_task",
         python_callable=webscraping
    )

           