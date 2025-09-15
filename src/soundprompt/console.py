# LICENSE HEADER MANAGED BY add-license-header
#
# Copyright (C) 2025 Ethorbit
#
# This file is part of SoundPrompt.
#
# SoundPrompt is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# SoundPrompt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with SoundPrompt.
# If not, see <https://www.gnu.org/licenses/>.
#

from threading import Thread
from soundprompt.event import Event
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


class Console:
    """
    Class for console command handling
    """

    # TODO: add Queue, methods to send commands

    on_command: Event
    history: InMemoryHistory
    _prompt_session: PromptSession

    def __init__(self):
        history = InMemoryHistory()
        self.history = history
        self._prompt_session = PromptSession(history=history)
        self.on_command = Event()

    # Create Queue Loop, cb on each command
    # def send(cmd: str)

    def interactive(self) -> Thread:
        while True:
            try:
                cmd = self._prompt_session.prompt(">>>").strip().lower()
                if not cmd:
                    continue

                self.history.append_string(cmd)
                # TODO: self.send(cmd)
                self.on_command.notify(cmd)
            except (KeyboardInterrupt, EOFError):
                print("\nInterrupted. Exiting...")
                break
