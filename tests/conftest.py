import io
import os
import tempfile

import gnupg
import pytest
from airflow import settings
from airflow.models import Connection

from airflow_gpg_plugin.hooks.gpg_hook import GpgHook


@pytest.fixture(scope="session", autouse=True)
def airflow_home():
    os.system(f"airflow db init")
    yield "airflow_home"


@pytest.fixture(scope="session", autouse=True)
def gpg_key_with_passphrase(tmpdir_factory):
    key_file_path = str(tmpdir_factory.mktemp("keys").join("gpg_key_with_passphrase.asc"))
    key_file = open(key_file_path, "w")
    key_file.write(open("./tests/resources/gpgexamplepassphrase.asc", "r").read())
    key_file.flush()
    key_file.close()
    yield dict(
        login="gpgexamplepassphrase@example.com",
        password="gpgexamplepassphrase",
        key_file=key_file_path
    )


@pytest.fixture(scope="session", autouse=True)
def gpg_key_with_passphrase_connection(gpg_key_with_passphrase, tmpdir_factory):
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
    yield gpg_conn_id


@pytest.fixture(scope="session", autouse=True)
def gpg_key_without_passphrase(tmpdir_factory):
    key_file_path = str(tmpdir_factory.mktemp("keys").join("gpg_key.asc"))
    key_file = open(key_file_path, "w")
    key_file.write(open("./tests/resources/gpgexample.asc", "r").read())
    key_file.flush()
    key_file.close()
    yield dict(
        login="gpgexample@example.com",
        password=None,
        key_file=key_file_path
    )


def create_connection(conn_id: str, connection: Connection):
    session = settings.Session
    print(f"Creating connection {conn_id}")
    connection_objs = session.query(Connection).filter(
        Connection.conn_id == conn_id).all()
    for connection_obj in connection_objs:
        if connection_obj is not None:
            # delete all existing connections
            msg = f'\n\tA connection with `conn_id`={conn_id} already exists. Overwriting\n'
            print(msg)
            session.delete(connection_obj)
            session.commit()
    session.add(connection)
    session.commit()
    return conn_id


def decrypt_file(encrypted_file_path, key_details):
    with tempfile.NamedTemporaryFile(mode="w") as decrypted_file:
        with tempfile.TemporaryDirectory() as gnupghome:
            gpg = gnupg.GPG(gnupghome=gnupghome)
            import_result = gpg.import_keys(open(key_details["key_file"], "r").read(),
                                            passphrase=key_details["password"])
            gpg.trust_keys([x["fingerprint"] for x in import_result.results], 'TRUST_ULTIMATE')
            with open(encrypted_file_path, "rb") as encrypted_file:
                gpg.decrypt_file(encrypted_file, always_trust=True, output=decrypted_file.name,
                                 passphrase=key_details["password"])
            return open(decrypted_file.name, "r").read()


def encrypt_file(data, encrypted_file_path, key_details):
    with tempfile.TemporaryDirectory() as gnupghome:
        gpg = gnupg.GPG(gnupghome=gnupghome)
        import_result = gpg.import_keys(open(key_details["key_file"], "r").read(),
                                        passphrase=key_details["password"])
        gpg.trust_keys([x["fingerprint"] for x in import_result.results], 'TRUST_ULTIMATE')
        with io.BytesIO(bytes(data, "ascii")) as file:
            gpg.encrypt_file(file, always_trust=True,
                             output=encrypted_file_path,
                             recipients=[key_details["login"]],
                             passphrase=key_details["password"])
