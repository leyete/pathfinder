# Copyright (C) 2020 Lagg Squad dev team.
# This source code is released under a GPLv3 license.

'''
The handler module contains the AWS Lambda functions that implement
the available endpoints.
'''

import json
import logging
import telegram  # python-telegram-bot package.


# Setup logging subsystem.
logger = logging.getLogger("lepathfinderbot")
logging.basicConfig(level=logging.INFO)

# Endpoint responses.
OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok'),
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!'),
}


def configure_bot():
    """
    Configures the bot with a Telegram Token.
    """
    import os
    if (TELEGRAM_TOKEN := os.environ.get('TELEGRAM_TOKEN')):
        return telegram.Bot(TELEGRAM_TOKEN)

    logger.error('The TELEGRAM_TOKEN must be set.')
    raise NotImplementedError


def webhook(event: dict, context: dict) -> dict:
    """
    Runs the Telegram webhook.
    """
    logger.info(f'Event: {event}')
    bot = configure_bot()

    if event.get('httpMethod') == 'POST' and event.get('body'):
        logger.info('Telegram update received')
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
        text = update.message.text

        if text == '/start':
            text = 'Hi friend! My name is Pathfinder, type /help to see a list of things that I can do!'

        bot.sendMessage(chat_id=update.message.chat.id, text=text)
        logger.info('Update sent!')

        return OK_RESPONSE

    return ERROR_RESPONSE


def set_webhook(event: dict, context: dict) -> dict:
    """
    Sets the Telegram bot webhook.
    """
    logger.info(f'Event: {event}')
    bot = configure_bot()
    url = f'https://{event.get("headers").get("Host")}/{event.get("requestContext").get("stage")}/'

    if bot.set_webhook(url):
        return OK_RESPONSE

    return ERROR_RESPONSE

