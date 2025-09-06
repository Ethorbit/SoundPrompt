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

# Save a library on demand (folder of sound files
# each tagged with a tag file consisting of
# ~1-10 descriptive words)
#
# Iterate each file
# for each file:
# 1. encode each tag word as a SentenceTransformer embedding
# add to the annoy database, an iterator variable being the key
# 2. add entry for each tag word to metadata database,
# assigning embedding key to the respective sound file
#
# So output is two databases:
# 1. SQLite for human-readable metadata
# 2. Annoy for SentenceTransformer embeddings
# in the end, both have a commonality for identification (numerical key)
#
# Load an annoy library on demand along with its metadata
#
# Take input prompt, encode it as a SentenceTransformer embedding
# and get the closest annoy embedding match, use metadata db
# to get the filename: play the sound file!

import chromadb
from dataclasses import asdict, dataclass
from pathlib import Path
from sentence_transformers import SentenceTransformer
from config import load_config

config = load_config()

client = chromadb.PersistentClient(
    path=Path(config["general"]["db_dir"])
)

files = [
    {
        "file": "man-says-hello.wav",
        "hash":
        "a3f5b8c2d9e1f407b6c3e2a1d4f9b8c7e1a2f3d4c5b6a7e8f9d0c1b2a3e4f5d6",
        "tags": [
            "Hi",
            "Bye",
            "Thanks"
        ]
    },
    {
        "file": "yell-bye.wav",
        "hash":
        "c7d9e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0",
        "tags": [
            "Goodbye",
            "Leaving"
        ]
    },
    {
        "file": "haha.wav",
        "hash":
        "f1e2d3c4b5a6978877665544332211ffeeddccbbaa99887766554433221100aa",
        "tags": [
            "Laughing",
            "Happy",
            "Humor"
        ]
    }
]


@dataclass
class Metadata():
    file: str
    file_hash: str
    tag: str

    def to_dict(self):
        return asdict(self)


def create_key(file_hash: str, tag: str):
    return file_hash + "_" + tag


def update_collection(model: SentenceTransformer, library_name: str):
    collection = client.get_or_create_collection(library_name)

    # If file hash not present
    # -> new file
    # -> add all tag embeddings
    #
    # If file hash present
    # -> check tags
    # -> if differs
    # -> re-add all tag embeddings
    #
    for entry in files:
        # <do the checks here first!>
        for tag in entry["tags"]:
            key = create_key(entry["hash"], tag)
            embedding = model.encode(tag)
            metadata = Metadata(
                file=entry["file"],
                file_hash=entry["hash"],
                tag=tag
            ).to_dict()

            collection.add(
                ids=[key],
                embeddings=[embedding],
                metadatas=[metadata]
            )

    # Iterate all metadata file hashes
    # remove entries for files that aren't found


def load_collection(library_name: str) -> chromadb.Collection:
    return client.get_collection(library_name)
