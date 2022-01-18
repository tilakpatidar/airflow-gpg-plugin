import os
from datetime import datetime

from airflow import DAG
from airflow.models import Connection

from airflow_gpg_plugin.hooks.gpg_hook import GpgHook
from airflow_gpg_plugin.operators.gpg_decrypt_file_operator import GPGDecryptFileOperator
from tests.conftest import create_connection, encrypt_file


def test_gpg_decrypt_file_operator(gpg_key_with_passphrase, tmpdir_factory):
    gpg_conn_id = "default_gpg_conn_enc_op"

    conn = Connection(
        conn_id=gpg_conn_id,
        conn_type=GpgHook.conn_type,
        login=gpg_key_with_passphrase["login"],
        password=gpg_key_with_passphrase["password"],
        extra={
            "key_file": gpg_key_with_passphrase["key_file"]
        }
    )

    create_connection(gpg_conn_id, conn)

    input_file_path = str(tmpdir_factory.mktemp("files").join("test_file_enc.txt"))
    output_file_path = str(tmpdir_factory.mktemp("files").join("test_file_dec.txt"))
    encrypt_file(data="hello world", encrypted_file_path=input_file_path, key_details=gpg_key_with_passphrase)

    with DAG(dag_id="test_gpg_decrypt_file_dag", start_date=datetime(2021, 1, 1), schedule_interval="@daily") as dag:
        op = GPGDecryptFileOperator(
            task_id="gpg_enc",
            dag=dag,
            conn_id=gpg_conn_id,
            input_file_path=input_file_path,
            output_file_path=output_file_path
        )
        dag.clear()
        op.run(
            start_date=dag.start_date,
            end_date=dag.start_date,
            ignore_first_depends_on_past=True,
            ignore_ti_state=True
        )

        assert os.path.exists(op.output_file_path)
        assert open(op.output_file_path, "r").read() == "hello world"
