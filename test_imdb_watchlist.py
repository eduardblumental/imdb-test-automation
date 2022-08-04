import os, pytest

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException


driver = Chrome(service=Service(ChromeDriverManager().install()))


def sign_in_to_imdb(user, password):
    driver.get('https://www.imdb.com/')
    driver.find_element(By.XPATH, "//div[text()='Sign In']").click()
    driver.find_element(By.XPATH, "//span[text()='Sign in with IMDb']").click()

    driver.find_element(By.ID, "ap_email").send_keys(user)
    driver.find_element(By.ID, "ap_password").send_keys(password)
    driver.find_element(By.ID, "signInSubmit").click()


def go_to_movie_page(movie_name):
    search_bar = driver.find_element(By.ID, "suggestion-search")
    search_bar.send_keys(movie_name)
    search_bar.send_keys(Keys.RETURN)
    driver.find_element(By.XPATH, f"//a[text()='{movie_name}']").click()


def add_movie_to_watchlist(movie_name):
    go_to_movie_page(movie_name)
    WebDriverWait(driver, 10).\
        until(EC.visibility_of_element_located((By.XPATH, "//div[text()='Add to Watchlist']"))).\
        click()
    driver.refresh()


def get_all_watchlist_movies():
    driver.find_element(By.XPATH, "//div[text()='Watchlist']").click()
    watchlist_elements = driver.find_elements(By.XPATH, "//h3[@class='lister-item-header']/a")
    return [element.get_attribute('innerHTML') for element in watchlist_elements]


def remove_movie_from_watchlist(movie_name):
    driver.find_element(By.XPATH,
                        f"//a[text()='{movie_name}']/../../../div/div[@title='Click to remove from watchlist']").click()
    driver.refresh()


def get_watchlist_count(waiting_time=10, xpath="//div[text()='Watchlist']/span"):
    try:
        watchlist_count = WebDriverWait(driver, waiting_time).\
            until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return int(watchlist_count.get_attribute('innerHTML'))
    except TimeoutException:
        return 0


@pytest.fixture(scope='session')
def movie():
    return 'Deadpool'


@pytest.fixture(scope='session')
def results():
    return {}


@pytest.fixture(scope='session', autouse=True)
def execute_test_scenario(results, movie):
    sign_in_to_imdb(os.environ.get('USER'), os.environ.get('PASSWORD'))
    results['watchlist_count_0'] = get_watchlist_count()

    add_movie_to_watchlist(movie)
    results['watchlist_count_1'] = get_watchlist_count()
    results['watchlist_movies'] = get_all_watchlist_movies()

    remove_movie_from_watchlist(movie)
    results['watchlist_count_2'] = get_watchlist_count()

    yield driver

    driver.close()
    driver.quit()


def test_imdb_watchlist_count_increase(results):
    assert results.get('watchlist_count_0') + 1 == results.get('watchlist_count_1')


def test_imdb_watchlist_added_movie_presence(results, movie):
    assert movie in results.get('watchlist_movies')


def test_imdb_watchlist_count_decrease(results):
    assert results.get('watchlist_count_1') - 1 == results.get('watchlist_count_2')
