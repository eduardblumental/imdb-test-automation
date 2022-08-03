import pytest, time, os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException


driver = Chrome(service=Service(ChromeDriverManager().install()))


@pytest.fixture(scope='session')
def counter():
    return {'watchlist': 0}


@pytest.fixture(scope='session', autouse=True)
def login_to_imdb(counter):
    driver.get('https://www.imdb.com/')
    driver.find_element(By.XPATH, "//div[text()='Sign In']").click()
    driver.find_element(By.XPATH, "//span[text()='Sign in with IMDb']").click()

    driver.find_element(By.ID, "ap_email").send_keys(os.environ.get('USER'))
    driver.find_element(By.ID, "ap_password").send_keys(os.environ.get('PASSWORD'))
    driver.find_element(By.ID, "signInSubmit").click()

    try:
        watchlist_counter = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[text()='Watchlist']/span")))
        counter['watchlist'] = int(watchlist_counter.get_attribute('innerHTML'))
    except TimeoutException:
        print('\nThe Watchlist is empty. Keeping counter at 0.')

    yield driver

    driver.close()
    driver.quit()


def test_imdb_search_bar(counter):
    search_bar = driver.find_element(By.ID, "suggestion-search")
    search_bar.send_keys("Deadpool")
    search_bar.send_keys(Keys.RETURN)

    assert counter['watchlist'] == 0
