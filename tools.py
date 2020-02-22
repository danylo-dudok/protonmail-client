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
    name_index = next((index for index, arg in enumerate(arguments) if arg == name), -1)
    if name_index < 0:
        return None

    value_index = name_index + 1
    if value_index >= len(arguments):
        return None

    return arguments[value_index]


def parse_app_arguments(arguments: List[str]) -> ApplicationArguments:
    return ApplicationArguments(
        session_uuid=get_argument_by_name(arguments, '--id'),
        context_path=get_argument_by_name(arguments, '--context-path'),
        username=get_argument_by_name(arguments, '--username'),
        password=get_argument_by_name(arguments, '--password')
    )
