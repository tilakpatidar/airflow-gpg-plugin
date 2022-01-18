import os
import tempfile

os.environ["AIRFLOW_HOME"] = tempfile.TemporaryDirectory().name
os.environ["AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS"] = "False"
os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"

print(f"airflow home : {os.environ['AIRFLOW_HOME']}")
