import os
from rocketchat_API import RocketChat
from tools.vault import get_vault_secret
from tools.logger import logger

rocket_chat_url = os.getenv('ROCKETCHAT_URL', 'default')
ROCKET_CHAT_VAULT_PATH = os.getenv('ROCKET_CHAT_VAULT_PATH', 'default')

rocket_chat_username = get_vault_secret(VAULT_PATH)
rocket_chat_password = get_vault_secret(VAULT_PATH)


def send_message(message: object, channel: str):
    rocket_chat = RocketChat(rocket_chat_username, rocket_chat_password, server=rocket_chat_url)
    response = rocket_chat.chat_post_message(message, channel)
    logger.info(f"Sending message to rocketchat: RESPONSE: {response}")
    return response



