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

import os
from collections.abc import Generator


class RecursiveScanDir:
    path: str
    only_files: bool

    def __init__(
        self,
        path: str,
        extensions: str | list[str] | None = None,
        only_files: bool = False
    ):
        self.path = path
        if extensions is not None:
            if isinstance(extensions, str):
                extensions = [extensions]

            # Extensions: normalize lowercase & dot
            self.extensions = {
                ext.lower()
                if ext.startswith(".") else f".{ext.lower()}"
                for ext in extensions
            }
        self.only_files = only_files

    def __iter__(self) -> Generator[os.DirEntry, None, None]:
        yield from self._scan(self.path)

    def _scan(self, path: str) -> Generator[os.DirEntry, None, None]:
        for entry in os.scandir(path):
            is_dir = entry.is_dir(follow_symlinks=False)

            if is_dir:  # recursive, add subdir's contents
                yield from self._scan(entry.path)
            else:
                if self.extensions is not None:
                    _, ext = os.path.splitext(entry.name)

                    if ext.lower() in self.extensions:
                        yield entry
                else:
                    yield entry

            # Add the dir itself too if allowed
            if not self.only_files and is_dir:
                yield entry


def validate_directory(directory: str):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"{directory} doesn't exist.")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} is not a directory.")
