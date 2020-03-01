import logging
from typing import List

from browser import Browser
from client import ProtonClient
from models import Context, UserCredentials
from tools import decdec, save_context, parse_app_arguments, get_context


def run_in_browser(func):
    def wrapper(arguments: List[str]):
        app_args = parse_app_arguments(arguments)
        context = get_context(app_args.context_path)
        current_session = None

        if app_args.session_uuid:
            current_session = next(
                filter(lambda session: session.id == app_args.session_uuid, context.sessions),
                None
            )

        browser = Browser(current_session)
        user_creds = UserCredentials(app_args.username, app_args.password, None)

        try:
            func(browser, context, user_creds)
        except Exception as ex:
            logging.exception('Browser error.', ex)
            current_session = None
            context.sessions = [
                session for session in context.sessions
                if session.id != current_session.id
            ]
            browser.dispose()
        finally:
            if current_session:
                context.sessions.append(current_session)
            save_context(context, app_args.context_path)

    return wrapper


@decdec(run_in_browser)
def run_in_proton(func):
    def wrapper(browser: Browser, context: Context, user: UserCredentials):
        try:
            client = ProtonClient(browser, context)
            client.login(user)
            func(client)
        except Exception as ex:
            logging.exception('Client error.', ex)

    return wrapper
