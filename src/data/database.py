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

    client: chromadb.PersistentClient
    model: SentenceTransformer
    directory: str
    library_directory: str
    key: str
    collection_name: str

    def __init__(
        self,
        model: SentenceTransformer,
        data_directory: str,
        library_directory: str
    ):
        self.model = model

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

    def create_key(self, file_hash: str, tag: str) -> str:
        return file_hash + "_" + tag

    def add_file_to_collection(
        collection: chromadb.Collection,
        tags_file_path: str,
        audio_file_path: str
    ):
        """
        Adds a file to a database collection
        - Adds the tag file path
        - Adds the audio file path
        - AI Encodes each of its tags
        """
        return

    def update(self):
        """
        Updates the library in the database
        - Iterates all the files
        - Add missing entries to collection
        """

        collection = self.client.get_or_create_collection(
            self.collection_name
        )

        # add an auto tag which is the filename itself

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
                existing_item = collection.get(
                    where={
                        "tags_file_path": tags_file_path,
                        "audio_file_path": audio_file_path
                    }
                )

                if not existing_item["ids"]:
                    self.add_file_to_collection(
                        collection=collection,
                        tags_file_path=tags_file_path,
                        audio_file_path=audio_file_path
                    )

                    continue

                # at this point the file exists in collection,
                # make sure its metadata tags match current tags
                # if it does, skip it, otherwise redo its entry

        # old dummy code:
        # for entry in files:
        #     # <do the checks here first!>
        #     for tag in entry["tags"]:
        #         key = self.create_key(
        #             file_hash=entry["hash"],
        #             tag=tag
        #         )
        #         embedding = model.encode(tag.lower())
        #         metadata = Metadata(
        #             file=entry["file"],
        #             file_hash=entry["hash"],
        #             tag=tag
        #         ).to_dict()

        #         collection.add(
        #             ids=[key],
        #             embeddings=[embedding],
        #             metadatas=[metadata]
        #         )

        # Iterate all metadata file hashes
        # remove entries for files that aren't found

    def get_collection(self) -> chromadb.Collection:
        return self.client.get_collection(self.collection_name)
