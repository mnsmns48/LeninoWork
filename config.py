import os
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings

root_path = Path(os.path.abspath(__file__)).parent


class Config(BaseSettings):
    db_local_username: SecretStr
    db_local_password: SecretStr
    db_local_port: SecretStr
    db_name: SecretStr
    db_table: str
    db_server_username: SecretStr
    db_server_password: SecretStr
    ssh_host: SecretStr
    ssh_port: int
    ssh_username: SecretStr
    ssh_password: SecretStr
    tunnel: bool
    link: str


config = Config(_env_file=f"{root_path}/.env")
