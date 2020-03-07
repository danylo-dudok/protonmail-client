from dataclasses import dataclass
from typing import List

from browser import Browser, Element
from models import Mail, Body, UserInfo, Conversation, UserCredentials, Context


@dataclass
class ElementTuple:
    element: Element


@dataclass
class ElementConversation(ElementTuple):
    conversation: Conversation


@dataclass
class ElementMail(ElementTuple):
    mail: Mail


class Client:
    _browser: Browser

    def __init__(self, browser: Browser):
        self._browser = browser


class ProtonClient(Client):
    _context: Context

    @property
    def is_authorized(self) -> bool:
        return (bool(self._browser.current_session.user_creds)
                if self._browser.current_session else False)

    def __init__(self, browser: Browser, context: Context):
        Client.__init__(self, browser)
        self._context = context

    def login(self, user: UserCredentials) -> None:
        if self.is_authorized:
            return

        self._browser.navigate(self._context.login_url)

        if not user or not self._browser.current_url == self._context.login_url:
            raise Exception()

        username_input = self._browser.find_by_id('username')
        password_input = self._browser.find_by_id('password')
        login_button = self._browser.find_by_id('login_btn')

        username_input.send_keys(user.username)
        password_input.send_keys(user.password)
        login_button.click()

        code_input = self._browser.find_by_css_selector('#twoFactorCode')
        if len(code_input) and user.code and self._browser.current_url == self._context.login_url:
            code_input = code_input[0]
            code_login_button = self._browser.find_by_id('login_btn_2fa')
            code_input.send_keys(user.code)
            code_login_button.click()

        self._browser.wait_until_url(self._context.inbox_url)
        self._browser.current_session.user_creds = user

    def get_conversations(self) -> List[ElementConversation]:
        return [
            ElementConversation(
                element=item,
                conversation=Conversation(
                    sender=item.find_by_css_selector('span.senders.ellipsis > span')[0].text,
                    subject=item.find_by_css_selector('div.subject > h4 > span.subject-text.ellipsis')[0].text
                )
            )
            for item in self._browser.find_by_css_selector(
                '#conversation-list-rows > section > div.conversation',
                True
            )
        ]

    def get_messages(self) -> List[ElementMail]:
        for el in self._browser.find_by_css_selector('article.message.hasSender', True):
            el.click()
            [sender_el] = el.find_by_css_selector(
                'div.summary > div.summary-left > div.meta > div > div.from-value',
                True
            )
            [body_el] = el.find_by_css_selector('div.frame.message-frame > div', True)
            [username_el] = sender_el.find_by_tag('strong')
            [email_el] = sender_el.find_by_tag('em')
            yield ElementMail(
                element=el,
                mail=Mail(
                    sender=UserInfo(
                        username=username_el.text.replace('<', '').replace('>', ''),
                        email=email_el.text.replace('<', '').replace('>', '')
                    ),
                    body=Body(body_el.text)
                )
            )
