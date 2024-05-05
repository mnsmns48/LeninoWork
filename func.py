import asyncio

from browser import browser


async def info():
    driver = browser()
    driver.get('https://www.avito.ru/schelkino/vakansii?cd=1')
    driver.save_screenshot('fgh.png')
    print('1')
    await asyncio.sleep(50)