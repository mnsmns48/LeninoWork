import pickle
import random
import re
import time
import dateparser
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from retry import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session
from sshtunnel import BaseSSHTunnelForwarderError

from config import config
from crud import write_data
from engine import ssh_connect
from models import Base


def _filter(text: str, block_words: list) -> bool:
    for block_word in block_words:
        if block_word in text:
            return False
    return True


def bs4_processing(soup: BeautifulSoup, black_authors: list, block_words: list) -> dict | None:
    url = soup.find('a', {'itemprop': 'url'})
    title = soup.find('h3', {'itemprop': 'name'}).text
    author = soup.find("div", {"class": re.compile('.*iva-item-userInfoStep-.*')})
    cond = soup.find('p', {'data-marker': 'item-specific-params'}).text
    desc = soup.find("div", {"class": re.compile('iva-item-descriptionStep-.*')}).text.strip()
    locality = soup.find("div", {"class": re.compile('geo-root-.*')}).text
    updated_at = soup.find("div", {"class": re.compile('iva-item-dateInfoStep-.*')}).text
    if (_filter(text=title,
                block_words=block_words)
            and _filter(text=cond,
                        block_words=block_words)
            and _filter(text=desc,
                        block_words=block_words)
            and _filter(
                text=author.text,
                block_words=black_authors)):
        result = {
            'id': int(soup.div.get('data-item-id')),
            'title': title,
            'author': author.div.a.p.text if author else None,
            'payment': soup.find('strong').span.text,
            'cond': cond,
            'desc': desc.replace('\n\n', '\n'),
            'performance': soup.find("span", {"class": re.compile('iva-item-text-.*')}).text,
            'locality': 'Республика Крым, Щёлкино' if len(locality) <= 5 else locality,
            'link': 'https://www.avito.ru' + url.get('href'),
            'updated_at': dateparser.parse(updated_at),
        }
        return result
    return None


@retry(BaseSSHTunnelForwarderError, tries=5000, delay=30)
@ssh_connect
def update_data(driver: uc, url: str, **kwargs):
    print('start update data')
    driver.get('https://www.avito.ru/')
    [driver.add_cookie(cookie) for cookie in pickle.load(open("cookies.pkl", "rb"))]
    time.sleep(5)
    driver.get(url)
    pag_list = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "[data-marker='pagination-button']")))
    pag_l = pag_list.find_elements(By.TAG_NAME, 'li')
    last_pag_page = pag_l[-2].find_element(By.TAG_NAME, 'a').get_attribute('data-value')
    count = 1
    with open('blacklist_author.txt', 'r', encoding='utf-8') as file:
        black_authors = [line.strip() for line in file.readlines()]
    with open('blacklist_words.txt', 'r', encoding='utf-8') as file:
        block_words = [line.strip() for line in file.readlines()]
    with Session(bind=kwargs.get('bind').engine) as session:
        while count != int(last_pag_page) + 1:
            if count == 1:
                pass
            else:
                link = f"{url}&p={count}"
                driver.get(link)
                time.sleep(random.randint(3, 10))
            items = driver.find_elements(By.CSS_SELECTOR, "[data-marker='item']")
            for item in items:
                soup = BeautifulSoup(markup=item.get_attribute('outerHTML'), features='lxml')
                data = bs4_processing(soup=soup, black_authors=black_authors, block_words=block_words)
                if data:
                    write_data(session=session, table=Base.metadata.tables.get(config.db_table), data=data)
            count += 1
    print('success')


