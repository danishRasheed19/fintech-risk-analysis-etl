
import os
import subprocess
import sys
from datetime import datetime, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_ROOT = "/opt/project"
PROJECT_SRC = f"{PROJECT_ROOT}/src"


def run_etl():
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{PROJECT_SRC}"

    subprocess.run(
        [sys.executable, f"{PROJECT_SRC}/pipeline.py"],
        cwd=PROJECT_SRC,
        env=env,
        check=True,
    )


def run_risk_pipeline():
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{PROJECT_SRC}"

    subprocess.run(
        [sys.executable, f"{PROJECT_SRC}/risk_platform/risk_pipeline.py"],
        cwd=PROJECT_SRC,
        env=env,
        check=True,
    )


with DAG(
    dag_id="risk_analytics_pipeline",
    description="Run ETL followed by risk analytics",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    tags=["etl", "risk-analytics"],
) as dag:

    etl_task = PythonOperator(
        task_id="run_etl",
        python_callable=run_etl,
    )

    risk_task = PythonOperator(
        task_id="run_risk_pipeline",
        python_callable=run_risk_pipeline,
    )

    etl_task >> risk_task
