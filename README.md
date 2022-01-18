# Airflow GPG Plugin
[![Latest Version](https://img.shields.io/pypi/v/airflow-gpg-plugin.svg)](https://pypi.python.org/pypi/pytest-snowflake-bdd/)
[![Python Versions](https://img.shields.io/pypi/pyversions/airflow-gpg-plugin.svg)](https://pypi.python.org/pypi/pytest-snowflake-bdd/)

Airflow plugin with hooks and operators to work with GPG encryption and decryption.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install airflow-gpg-plugin
```

## Usage

Add an airflow connection from shell.

`login` is the email address in the GPG key.

`password` is the passphrase of the GPG key.

```shell
airflow connections add 'gpg_default_conn' \
    --conn-type 'gpg' \
    --conn-login 'gpgexamplepassphrase@example.com' \
    --conn-password 'gpgexamplepassphrase' \
    --conn-host '' \
    --conn-port '' \
    --conn-extra '{"key_file": "tests/resources/gpgexamplepassphrase.asc"}'
```

Using operators to encrypt and decrypt files.
```python
import os
from datetime import datetime

from airflow import DAG
from airflow_gpg_plugin.operators.gpg_decrypt_file_operator import GPGDecryptFileOperator
from airflow_gpg_plugin.operators.gpg_encrypt_file_operator import GPGEncryptFileOperator
gpg_conn_id = "gpg_default_conn"

dag = DAG(dag_id="gpg_example",
          start_date=datetime(2021, 1, 1),
          schedule_interval=None
          )

encrypt = GPGEncryptFileOperator(
    task_id="gpg_encrypt",
    dag=dag,
    conn_id=gpg_conn_id,
    input_file_path=os.curdir + "/README.md",
    output_file_path=os.curdir + "/README.md.gpg"
)
decrypt = GPGDecryptFileOperator(
    task_id="gpg_decrypt",
    dag=dag,
    conn_id=gpg_conn_id,
    input_file_path=os.curdir + "/README.md.gpg",
    output_file_path=os.curdir + "/README.md.txt"
)

encrypt >> decrypt


```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)