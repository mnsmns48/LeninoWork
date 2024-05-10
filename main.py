from browser import browser
from config import config
from crud import output
from engine import db_start_sync
from func import update_data
from models import Base


def main():
    db_start_sync(Base, tunnel=config.tunnel)
    update_data(driver=browser(), url=config.link, tunnel=config.tunnel)
    # output(tunnel=config.tunnel)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Script stopped')
