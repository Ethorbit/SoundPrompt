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

from queue import Queue
from soundprompt.worker import Worker
from soundprompt.event import Event
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


class CommandLoop(Worker):
    """
    Handles processing of commands
    """

    _queue: Queue[str]
    event: Event

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = Queue()
        self.event = Event()

    def run(self) -> None:
        while not self.is_stopped():
            if not self._queue.empty():
                cmd = self._queue.get()
                self.event.notify(cmd)

    def submit(self, cmd: str) -> None:
        self._queue.put(cmd)


class Console(Worker):
    """
    Class for CLI console
    """

    commandLoop: CommandLoop
    history: InMemoryHistory
    _prompt_session: PromptSession

    def __init__(self, commandLoop: CommandLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commandLoop = commandLoop
        history = InMemoryHistory()
        self.history = history
        self._prompt_session = PromptSession(history=history)
        self._command_queue = Queue()

    def send_command(self, command: str) -> None:
        self.commandLoop.submit(command)

    def run(self) -> None:
        while not self.is_stopped():
            try:
                cmd = self._prompt_session.prompt(">>>").strip().lower()
                if not cmd:
                    continue

                self.history.append_string(cmd)
                self.send_command(cmd)
            except (KeyboardInterrupt, EOFError):
                print("\nInterrupted. Exiting...")
                break
