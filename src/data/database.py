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

import re
import chromadb
import os
import json
from . import filesystem
from dataclasses import asdict, dataclass
from sentence_transformers import SentenceTransformer


@dataclass
class Metadata:
    file: str
    file_hash: str
    tag: str

    def to_dict(self):
        return asdict(self)


class TaggedFileMissingError(Exception):
    """
    Exception raised for when a file associated with a tag is missing.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# TODO: add progress bar or loading animation
# 100 files takes ~5 seconds to save
# massive libraries could take minutes
class Data:
    """
    Manages a sound library with tag-based metadata and AI embeddings.

    Responsibilities:
    - Validate and manage the data and library directories.
    - Iterate and process tag files and associated audio files.
    - Store metadata in a database (e.g., SQLite or ChromaDB).
    - Encode tags using a SentenceTransformer and manage embeddings.
    - Provide retrieval of data.

    Notes:
    - Tag files must exactly match the associated audio file name
    with a '.txt' suffix.
    - Audio file extensions and tag normalization are handled
    internally.
    - Designed to handle large libraries efficiently
    (hundreds of thousands of files).
    """

    config: dict[str]
    client: chromadb.PersistentClient
    model: SentenceTransformer
    directory: str
    library_directory: str
    key: str
    collection_name: str

    def __init__(
        self,
        config: dict[str],
        model: SentenceTransformer,
        library_directory: str
    ):
        self.config = config
        self.model = model

        data_directory = config["database"]["directory"]
        for d in [data_directory, library_directory]:
            filesystem.validate_directory(d)

        self.directory = data_directory
        self.library_directory = library_directory
        self.set_collection_name(library_directory)
        self.client = chromadb.PersistentClient(
            path=data_directory
        )

    def set_collection_name(self, value: str):
        """
        Sanitizes a string to be a valid ChromaDB Collection name
        - Replaces symbols and whitespaces with an underscore
        """
        pattern = re.compile(r"(\s|\W)")
        self.collection_name = re.sub(pattern, "_", str(value))

    def create_key(self, *parts: str) -> str:
        """
        Standardized format for collection key
        Should always be used when saving entries
        """

        return "::".join(str(p) for p in parts if p)

    def collection_add_config(
        self,
        collection: chromadb.Collection
    ):
        collection.add(
            ids=self.create_key(
                self.library_directory,
                "settings",
            ),
            documents=[json.dumps(self.config)]
        )

    def collection_get_config(
        self,
        collection: chromadb.Collection
    ) -> dict:
        item = collection.get(
            ids=[
                self.create_key(
                    self.library_directory,
                    "settings"
                )
            ],
            include=["documents"]
        )

        if item["ids"]:
            return json.loads(item["documents"][0])

    def collection_add_file(
        self,
        collection: chromadb.Collection,
        tags_file_name: str,
        tags_file_path: str,
        audio_file_path: str
    ):
        """
        Adds a file to a database collection
        - Adds the tag file path
        - Adds the audio file path
        - AI Encodes each of its tags
        """

        with open(
            tags_file_path,
            mode="r",
            encoding="utf-8"
        ) as f:
            tags = [
                tag.strip()
                for tag in f.read().lower().split(",")
            ]

            if self.config["database"]["save_filenames"]:
                file_name, _ = filesystem.split_extension(tags_file_name)
                tags.append(file_name.lower())

            for tag in tags:
                collection.add(
                    ids=self.create_key(
                        self.library_directory,
                        tags_file_name,
                        tag
                    ),
                    embeddings=[self.model.encode(tag)],
                    metadatas={
                        "tag_file": tags_file_path,
                        "audio_file": audio_file_path,
                        "tag": tag
                    }
                )

    def update(self):
        """
        Updates the library in the database
        - Iterates all the files
        - Add missing entries to collection
        """

        collection = self.get_collection(True)

        force_update = False

        # Force an update if crucial settings have changed
        collection_config = self.collection_get_config(collection)
        if collection_config:
            if (
                self.config["database"]["save_filenames"]
                is not collection_config["database"]["save_filenames"]
            ) or (
                # Models change embeddings entirely
                self.config["general"]["model_name"]
                is not collection_config["general"]["model_name"]
            ):
                force_update = True

        file_entries = filesystem.RecursiveScanDir(
            self.library_directory,
            extensions="txt",
            only_files=True
        )

        for file_entry, file_stem, file_ext in file_entries:
            tags_file_path = file_entry.path
            tags_dir = os.path.dirname(tags_file_path)
            audio_file_path = os.path.join(tags_dir, file_stem)

            try:
                filesystem.validate_file(audio_file_path)
            except Exception as e:
                if isinstance(e, FileExistsError):
                    raise TaggedFileMissingError(
                        f"Your tag {tags_file_path} was made "
                        f"for an audio file that doesn't exist: "
                        f"{audio_file_path}\n"
                        f"Make sure the tag's filename is "
                        f"EXACTLY the same as the sound's "
                        f"with .txt appended at the end. "
                        f"e.g.: awesome-explosion.mp3.txt"
                    )
                else:
                    raise e
            finally:
                existing_item = force_update or collection.get(
                    where={
                        "tag_file": tags_file_path,
                    }
                )

                if force_update or not existing_item["ids"]:
                    self.collection_add_file(
                        collection=collection,
                        tags_file_name=file_stem,
                        tags_file_path=tags_file_path,
                        audio_file_path=audio_file_path
                    )

                    continue

                print("Skipped. Check tags")
                # at this point the file exists in collection,

                # check if filenames_included matches arg
                # if not, redo the tags

        self.collection_add_config(collection)

        # Iterate all file paths
        # remove entries for files that aren't valid anymore
        # (otherwise it will try to play invalid sounds)
    def get_collection(self, create: bool = False) -> chromadb.Collection:
        return (
            create and
            self.client.get_or_create_collection(self.collection_name)
            or self.client.get_collection(self.collection_name)
        )
