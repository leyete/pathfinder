# Copyright (C) 2020 Lagg Squad Dev Team.
# This source code is released under a GPL-3.0 license.

"""
Base class for command handlers.
"""

import abc

import telegram
import telegram.ext


class CommandHandlerMetaclass(abc.ABCMeta):
    """
    Metaclass for CommandHandlers. When a class is loaded, it will be added to the
    REGISTERED_HANDLERS so it can be instantiated and added to the dispatcher later.
    """
    def __new__(cls, name, base, dct):
        """
        Creates the new class.
        """
        newcls = type(abc.ABCMeta).__new__(cls, name, base, dct)
        if 'command' in dct and dct['command']:
            REGISTERED_HANDLERS.append(newcls)
        return newcls


class CommandHandler(telegram.ext.CommandHandler, metaclass=CommandHandlerMetaclass):
    """
    Base class for command handlers. This purpose of this class is to simplify
    the creation of command handlers and abstract the developer from the
    underlying API (python-telegram-bot).
    """

    command: str = None
    filters: telegram.ext.BaseFilter = None

    def __init__(self):
        """
        Initializes the CommandHandler instance.
        """
        super().__init__(
                self.command,
                self.callback,
                filters = self.filters,
                run_async = False,
        )

    @abc.abstractmethod
    def callback(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """
        Handles a dispatched Telegram update. When the dispatcher receives an update it will
        be delegated to the handlers and, if the handler is allowed to handle the update, this
        method will be executed.

        Check python-telegram-bot API for more info.

        Parameters:
            update (:obj:`telegram.ext.Update`): The Telegram update instance.
            contetx (:obj:`telegram.ext.CallbackContext`): The callback context.
        """

# List of registered handlers
REGISTERED_HANDLERS = []
