# Copyright (C) 2020 Lagg Squad Dev Team.
# This source code is released under a GPL-3.0 license.

'''
The handler module contains the AWS Lambda functions that implement
the available endpoints.
'''

import json
import logging
import pathfinder
import telegram

from typing import Union


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#   HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def ok_response(
        code: int = 200,
        body: Union[str,dict] = 'ok',
        headers: dict = {}
) -> dict:
    """
    Generates and returns a response to show success.

    Parameters:
        code (:obj:`int`, optional): Status code.
        body (:obj:`str` | :obj:`dict`, optional): Body of the message, will be sent as a
            JSON string.
        headers (:obj:`dict`, optional): Additional headers. The Content-Type header is
        provided by this function and set to 'application/json'.
    """
    headers.update({'Content-Type': 'application/json'})
    return {'statusCode': code, 'headers': headers, 'body': json.dumps(body)}


def error_response(
        code: int = 400,
        body: Union[str,dict] = 'Oops... Something went wrong!',
        headers: dict = {}
) -> dict:
    """
    Generates and returns a response to show success.

    Parameters:
        code (:obj:`int`, optional): Status code.
        body (:obj:`str` | :obj:`dict`, optional): Body of the message, will be sent as a
            JSON string.
        headers (:obj:`dict`, optional): Additional headers. The Content-Type header is
        provided by this function and set to 'application/json'.
    """
    headers.update({'Content-Type': 'application/json'})
    return {'statusCode': code, 'headers': headers, 'body': json.dumps(body)}


# ------------------------------------------------------------------------------
#   LAMBDA FUNCTIONS
# ------------------------------------------------------------------------------

def set_webhook(event: dict, context: dict) -> dict:
    """
    Sets the Telegram bot webhook.
    """
    try:
        logger.info(f'Setting webhook\n\t--- Event ---\n%s.', event)
        bot = pathfinder.configure_bot()
        url = 'https://{}/{}'.format(
            event.get('headers').get('Host'),
            event.get('requestContext').get('stage'),
        )

        if bot.set_webhook(url):
            return ok_response(body=f'Webhook set -> {url}')

    except Exception as e:
        return error_response(body=f'Exception: {e}')

    # reched on error.
    return error_response(body='Failed to set webhook.')


def webhook(event: dict, context: dict) -> dict:
    """
    Runs the webhook for received Telegram updates.
    """
    try:
        logger.info(f'Running webhook\n\t--- Event ---\n%s', event)

        if event.get('httpMethod') == 'POST' and event.get('body'):
            dispatcher = pathfinder.configure_dispatcher()
            update = telegram.Update.de_json(json.loads(event.get('body')), dispatcher.bot)
            dispatcher.process_update(update)
            return ok_response(body='Update handled propperly.')

    except Exception as e:
        return error_response(body=f'Exception {e}')

    # reached on error.
    return error_response(body=f'Unsupported method / missing body.')
