# Copyright (C) 2020 Lagg Squad Dev Team.
# This source code is released under a GPL-3.0 license.

'''
Pathfinder command API.
'''

import logging
import telegram.ext

from .command import REGISTERED_HANDLERS
from .greet import GreetCommand


__all__ = ( 'load_handlers', )

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def load_handlers(dispatcher: telegram.ext.Dispatcher) -> None:
    """
    Adds all command handlers to the supplied dispatcher.

    Parameters:
        dispatcher (:obj:`telegram.ext.Dispatcher`): Dispatcher which the command handlers
        will be added to.
    """
    for handler in REGISTERED_HANDLERS:
        dispatcher.add_handler(handler())
        logger.info(f'Command registered: /{handler.command}')
