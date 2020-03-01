from typing import List, Final
from uuid import uuid1

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from models import Session

DEFAULT_SESSION_URL: Final = 'http://127.0.0.1:4444/wd/hub'
DEFAULT_TIMEOUT: Final = 20
DEFAULT_WAIT_FLAG: Final = False


def create_web_driver(session_url: str = DEFAULT_SESSION_URL):
    return webdriver.Remote(session_url, DesiredCapabilities.CHROME)


def start_new_session() -> (WebDriver, Session):
    driver = create_web_driver()
    session = Session(
        str(uuid1()),
        driver.session_id,
        driver.command_executor._url,
        None
    )
    return driver, session


def attach_to_session(session: Session) -> (WebDriver, Session):
    driver = create_web_driver(session.session_url)
    driver._is_remote = True
    driver.session_id = session.session_id
    driver.start_client()
    return driver, session


def attach_or_start_session(session: Session) -> (WebDriver, Session):
    try:
        return attach_to_session(session)
    except:
        return start_new_session()


ElementType = 'Element'


class Element:
    _web_element: WebElement

    @property
    def text(self):
        return self._web_element.text

    def __init__(self, web_element: WebElement):
        self._web_element = web_element

    def click(self) -> None:
        self._web_element.click()

    def send_keys(self, key: str) -> None:
        self._web_element.send_keys(key)

    def wait_for_element(self, css_selector: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        wait = WebDriverWait(self._web_element, timeout)
        wait.until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    def wait_until_url(self, url: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        wait = WebDriverWait(self._web_element, timeout)
        wait.until(expected_conditions.url_to_be(url))

    def find_by_id(self, id: str, wait: bool = DEFAULT_WAIT_FLAG) -> ElementType:
        if wait:
            self.wait_for_element(f'#{id}')
        return Element(
            self._web_element.find_element_by_id(id)
        )

    def find_by_css_selector(self, selector: str, wait: bool = DEFAULT_WAIT_FLAG) -> List[ElementType]:
        if wait:
            self.wait_for_element(selector)
        return [
            Element(element) for element in self._web_element.find_elements_by_css_selector(selector)
        ]

    def find_by_tag(self, tag_name: str, wait: bool = DEFAULT_WAIT_FLAG) -> List[ElementType]:
        if wait:
            self.wait_for_element(tag_name)
        return [
            Element(element) for element in self._web_element.find_elements_by_tag_name(tag_name)
        ]


class Browser(Element):
    _driver: WebDriver
    _current_session: Session or None

    @property
    def current_session(self) -> Session:
        return self._current_session

    @current_session.setter
    def current_session(self, value: Session) -> None:
        # TODO: attach to session
        self._current_session = value

    @property
    def current_url(self) -> str:
        return self._driver.current_url

    def navigate(self, url: str) -> None:
        self._driver.get(url)

    def __init__(self, session: Session):
        self._driver, self._current_session = attach_or_start_session(session) if session else start_new_session()
        Element.__init__(self, self._driver)

    def dispose(self):
        self._current_session = None
        self._driver.close()
