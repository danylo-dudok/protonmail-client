import sys
import logging
from client import ProtonClient
from decorators import run_in_proton

logging.basicConfig(filename='./logs/logs.log', level=logging.DEBUG)


@run_in_proton
def main(client: ProtonClient) -> None:
    conversations = client.get_conversations()
    conversation = conversations[0]
    conversation.element.click()
    messages = [message.mail for message in client.get_messages()]
    print(messages)


if __name__ == '__main__':
    main(sys.argv)
