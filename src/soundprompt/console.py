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
from threading import Thread
from soundprompt.event import Event
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory


class CommandLoop:
    """
    Handles processing of commands
    """

    _queue: Queue[str]
    _is_stopped: bool = False
    event: Event

    def __init__(self):
        self._queue = Queue()
        self.event = Event()

    def _start(self) -> None:
        while not self._is_stopped:
            if not self._queue.empty():
                cmd = self._queue.get()
                self.event.notify(cmd)

    def start(self) -> Thread:
        t = Thread(target=self._start)
        t.start()
        return t

    def stop(self) -> None:
        self._is_stopped = True
        self._queue.empty()

    def submit(self, cmd: str) -> None:
        self._queue.put(cmd)


class Console:
    """
    Class for console interface
    """

    commandLoop: CommandLoop
    history: InMemoryHistory
    _prompt_session: PromptSession

    def __init__(self, commandLoop: CommandLoop):
        self.commandLoop = commandLoop
        history = InMemoryHistory()
        self.history = history
        self._prompt_session = PromptSession(history=history)
        self._command_queue = Queue()

    def send_command(self, command: str) -> None:
        self.commandLoop.submit(command)

    def _interactive(self) -> None:
        while True:
            try:
                cmd = self._prompt_session.prompt(">>>").strip().lower()
                if not cmd:
                    continue

                self.history.append_string(cmd)
                self.send_command(cmd)
            except (KeyboardInterrupt, EOFError):
                print("\nInterrupted. Exiting...")
                break

    def interactive(self) -> Thread:
        t = Thread(target=self._interactive)
        t.start()
        return t
