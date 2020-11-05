# Copyright (C) 2020 Lagg Squad Dev Team.
# This source code is released under a GPL-3.0 license.

"""
Greet command.
"""

import telegram
import telegram.ext

from .command import CommandHandler


class GreetCommand(CommandHandler):
    """
    Pathfinder will salute you with joy and a cheerful spirit.
    """

    command: str = 'greet'

    def callback(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Salute the user that invoked the command."""
        update.message.reply_text("Hi friend!")
