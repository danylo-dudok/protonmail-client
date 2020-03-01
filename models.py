from dataclasses import dataclass
from typing import List


@dataclass
class ApplicationArguments:
    session_uuid: str
    context_path: str
    username: str
    password: str


@dataclass
class UserCredentials:
    username: str
    password: str
    code: str or None


@dataclass
class Session:
    id: str
    session_id: str
    session_url: str
    user_creds: UserCredentials


@dataclass
class Context:
    login_url: str
    inbox_url: str
    sessions: List[Session]


@dataclass
class Body:
    content: str


@dataclass
class UserInfo:
    username: str
    email: str


@dataclass
class Mail:
    sender: UserInfo
    body: Body


@dataclass
class Conversation:
    sender: str
    subject: str


@dataclass
class User:
    username: str
    conversations: List[Conversation]
