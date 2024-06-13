import pickle

import undetected_chromedriver as uc
from config import root_path


def browser() -> uc:
    options = uc.ChromeOptions()
    chrome_prefs = {
        "profile.default_content_settings": {"images": 2},
        "profile.managed_default_content_settings": {"images": 2}
    }
    # options.add_experimental_option('prefs', chrome_prefs)
    driver = uc.Chrome(headless=False,
                       use_subprocess=False,
                       version_main=114,
                       options=options,
                       driver_executable_path=f'{root_path}/chromedriver')
    driver.implicitly_wait(10)
    driver.maximize_window()
    return driver
