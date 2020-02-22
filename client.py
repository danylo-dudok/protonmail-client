from typing import Final, List
from uuid import uuid1

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from authorization import login
from models import Session, Mail, Body, UserInfo, Conversation, UserCredentials
from tools import get_context, parse_app_arguments, save_context

DEFAULT_SESSION_URL: Final = 'http://127.0.0.1:4444/wd/hub'


def create_web_driver(session_url: str = DEFAULT_SESSION_URL):
    return webdriver.Remote(session_url, DesiredCapabilities.CHROME)


def get_conversation_elements(element: WebElement) -> List[WebElement]:
    return element.find_elements_by_css_selector('#conversation-list-rows > section > div.conversation')


def get_conversations(conversation_elements: List[WebElement]) -> List[Conversation]:
    return [
        Conversation(
            sender=item.find_element_by_css_selector('span.senders.ellipsis > span').text,
            subject=item.find_element_by_css_selector('div.subject > h4 > span.subject-text.ellipsis').text
        )
        for item in conversation_elements
    ]


def start_new_session() -> (WebDriver, Session):
    driver = create_web_driver()
    session = Session(
        str(uuid1()),
        driver.session_id,
        driver.command_executor._url
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


def get_messages(element: WebElement) -> List[Mail]:
    message_elements = element.find_elements_by_css_selector('article.message.hasSender')
    messages = []
    for el in message_elements:
        el.click()
        sender_el = el.find_element_by_css_selector('div.summary > div.summary-left > div.meta > div > div.from-value')
        body_el = el.find_element_by_css_selector('div.frame.message-frame > div')
        username_el = sender_el.find_element_by_tag_name('strong')
        email_el = sender_el.find_element_by_tag_name('em')
        messages.append(
            Mail(
                sender=UserInfo(
                    username=username_el.text.replace('<', '').replace('>', ''),
                    email=email_el.text.replace('<', '').replace('>', '')
                ),
                body=Body(body_el.text)
            )
        )

    return messages


def run_in_browser(func):
    def wrapper(arguments: List[str]):
        app_args = parse_app_arguments(arguments)
        context = get_context(app_args.context_path)
        driver, current_session = None, None

        if app_args.session_uuid:
            current_session = next(
                filter(lambda x: x.id == app_args.session_uuid, context.sessions),
                None
            )

        try:
            if current_session:
                driver, current_session = attach_or_start_session(current_session)
            else:
                driver, current_session = start_new_session()
                current_session.user_creds = UserCredentials(
                    app_args.username,
                    app_args.password,
                    None
                )
                login(driver, context, current_session.user_creds)

            func(driver)

            context.sessions = [current_session]
        except:
            context.sessions = []
            driver.close()
        finally:
            save_context(context, app_args.context_path)

    return wrapper
