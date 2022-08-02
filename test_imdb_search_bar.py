import pytest, time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from login_data import username, password

driver = Chrome(service=Service(ChromeDriverManager().install()))


@pytest.fixture(scope='session', autouse=True)
def login_to_imdb():
    driver.get('https://www.imdb.com/')
    driver.find_element(By.XPATH, "//div[text()='Sign In']").click()
    driver.find_element(By.XPATH, "//span[text()='Sign in with IMDb']").click()

    driver.find_element(By.ID, "ap_email").send_keys(username)
    driver.find_element(By.ID, "ap_password").send_keys(password)
    driver.find_element(By.ID, "signInSubmit").click()

    time.sleep(3)

    yield driver

    driver.close()
    driver.quit()


def test_imdb_search_bar():
    search_bar = driver.find_element(By.ID, "suggestion-search")
    search_bar.send_keys("deadpool")
    search_bar.send_keys(Keys.RETURN)

    time.sleep(3)
