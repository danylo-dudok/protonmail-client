from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from models import UserCredentials, Context


def login(driver: WebDriver, context: Context, user: UserCredentials) -> None:
    driver.get(context.login_url)

    if not user or not driver.current_url == context.login_url:
        raise Exception()

    username_input = driver.find_element_by_id('username')
    password_input = driver.find_element_by_id('password')
    login_button = driver.find_element_by_id('login_btn')

    username_input.send_keys(user.username)
    password_input.send_keys(user.password)
    login_button.click()

    code_input = driver.find_elements_by_css_selector('#twoFactorCode')
    if len(code_input) and user.code and driver.current_url == context.login_url:
        code_input = code_input[0]
        code_login_button = driver.find_element_by_id('login_btn_2fa')
        code_input.send_keys(user.code)
        code_login_button.click()

    wait = WebDriverWait(driver, 5)
    wait.until(expected_conditions.url_to_be(context.inbox_url))
