from dataclasses import asdict
import json
from typing import List

from models import Context, Session, ApplicationArguments


def save_context(context: Context, path: str) -> None:
    with open(path, 'w') as file:
        json.dump(asdict(context), file)


def get_context(path: str) -> Context:
    with open(path, 'r') as file:
        context = Context(**json.load(file))
        context.sessions = [
            Session(**session) for session in context.sessions
        ]
        return context


def get_argument_by_name(arguments: List[str], name: str):
    return arguments[arguments.index(name) + 1] if name in arguments else None


def parse_app_arguments(arguments: List[str]) -> ApplicationArguments:
    return ApplicationArguments(
        session_uuid=get_argument_by_name(arguments, '--id'),
        context_path=get_argument_by_name(arguments, '--context-path'),
        username=get_argument_by_name(arguments, '--username'),
        password=get_argument_by_name(arguments, '--password')
    )


def decdec(inner_dec):
    def ddmain(outer_dec):
        def decwrapper(f):
            wrapped = inner_dec(outer_dec(f))
            def fwrapper(*args, **kwargs):
               return wrapped(*args, **kwargs)
            return fwrapper
        return decwrapper
    return ddmain
