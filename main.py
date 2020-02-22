import sys
from selenium.webdriver.remote.webdriver import WebDriver
from client import run_in_browser, get_conversation_elements, get_messages


@run_in_browser
def main(driver: WebDriver) -> None:
    conversation_elements = get_conversation_elements(driver)
    conversation_elements[0].click()
    messages = get_messages(driver)
    print(messages)


if __name__ == '__main__':
    main(sys.argv)
