# Copyright (C) 2020 Lagg Squad Dev Team.
# This source code is released under a GPL-3.0 license.

'''
Pathfinder API.
'''

import logging
import telegram
import telegram.ext


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#   API FUNCTIONS
# ------------------------------------------------------------------------------

def configure_bot() -> telegram.Bot:
    """
    Configures a bot with a Telegram token.

    Returns:
        A `telegram.Bot` instance.
    """
    import os
    if (TELEGRAM_TOKEN := os.environ.get('TELEGRAM_TOKEN')):
        return telegram.Bot(TELEGRAM_TOKEN)

    raise NotImplementedError('TELEGRAM_TOKEN not set.')


def configure_dispatcher() -> telegram.ext.Dispatcher:
    """
    Configures the update dispatcher.

    Returns:
        A `telegram.ext.Dispatcher` instance.
    """
    from commands import load_handlers
    dispatcher = telegram.ext.Dispatcher(configure_bot(), None, workers=0)
    load_handlers(dispatcher)
    return dispatcher
