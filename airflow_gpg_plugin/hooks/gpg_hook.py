#
import tempfile
from contextlib import contextmanager
from typing import ContextManager

import gnupg
from airflow import AirflowException
from airflow.hooks.base import BaseHook


def extract_key_data(extra_options: dict) -> str:
    key_file = extra_options.get('key_file')
    if key_file is not None:
        key_data = open(key_file).read()
    else:
        private_key = extra_options.get('private_key')
        if private_key is not None:
            key_data = private_key
        else:
            raise AirflowException("Either key_file or private_key must be present in connection extra")
    return key_data


class GpgHook(BaseHook):
    # Override to provide the connection name.
    conn_type = 'gpg'
    hook_name = 'gpg'

    def __init__(self, gpg_conn_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpg_conn_id = gpg_conn_id

    @contextmanager
    def get_conn(self) -> ContextManager[gnupg.GPG]:
        """Returns a connection object"""
        connection_obj = self.get_connection(self.gpg_conn_id)
        key_data = extract_key_data(connection_obj.extra_dejson)
        passphrase = connection_obj.password
        return self.import_key(key_data, passphrase)

    def import_key(self, key_data: str, passphrase: str) -> ContextManager[gnupg.GPG]:
        with tempfile.TemporaryDirectory() as gnupghome:
            self.log.info(f"Created temporary gnupghome directory {gnupghome}")
            gpg = gnupg.GPG(gnupghome=gnupghome)
            import_result = gpg.import_keys(key_data, passphrase=passphrase)
            gpg.trust_keys([x["fingerprint"] for x in import_result.results], 'TRUST_ULTIMATE')
            self.log.info("Import result")
            self.log.info(import_result.results)
            yield gpg
