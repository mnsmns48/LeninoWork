from typing import Callable
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder

from config import config


class Settings():
    def __init__(self, username: str, password: str, port: int, db_name: str):
        self.db_url: str = (f"postgresql+psycopg2://{username}:{password}"
                            f"@localhost:{port}/{db_name}")
        self.db_echo: bool = False


class DataBase:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_engine(
            url=url,
            echo=echo)


def create_ssh_tunnel() -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        (config.ssh_host.get_secret_value(), 22),
        ssh_username=config.ssh_username.get_secret_value(),
        ssh_password=config.ssh_password.get_secret_value(),
        remote_bind_address=('localhost', 5432))
    tunnel.start()
    return tunnel


def ssh_connect(function: Callable) -> Callable:
    def wrapped(*args, **kwargs):
        if kwargs.get('tunnel'):
            tunnel = create_ssh_tunnel()
            settings = Settings(
                username=config.db_server_username.get_secret_value(),
                password=config.db_server_password.get_secret_value(),
                port=tunnel.local_bind_port,
                db_name=config.db_name.get_secret_value()
            )
        else:
            settings = Settings(
                username=config.db_local_username.get_secret_value(),
                password=config.db_local_password.get_secret_value(),
                port=config.db_local_port.get_secret_value(),
                db_name=config.db_name.get_secret_value()
            )
        db = DataBase(url=settings.db_url, echo=settings.db_echo)
        return function(bind=db, *args, **kwargs)

    return wrapped


@ssh_connect
def db_start_sync(Base, **kwargs):
    Base.metadata.create_all(bind=kwargs.get('bind').engine)