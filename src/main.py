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

from config import args, config as config_import
from data import database
from sentence_transformers import SentenceTransformer
cfg = config_import.load_config()

model_name = cfg["general"]["model_name"]
model = SentenceTransformer(model_name)

args = args.get_args()

if args.save or args.load:
    data = database.Data(
        model=model,
        data_directory=cfg["general"]["db_dir"],
        library_directory=(args.save or args.load)
    )

if args.save:
    data.update()

if args.load:
    collection = data.get_collection()

    while True:
        try:
            prompt = input(">>>").lower()

            # user prompts
            prompt_embedding = model.encode(prompt.lower())
            collection_query = collection.query(
                query_embeddings=[prompt_embedding],
                n_results=10
            )

            print(collection_query["metadatas"])
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break

    # TODO: Implement cumulative scoring per file
    # Right now, retrieval picks the single closest tag embedding.
    # In the future, consider summing/aggregating similarities of all tags
    # for a file to better handle multiple matching tags.
    #
    # NOTE: this can all be done with current data implementation
    #
    # Example:
    # if you say "rubber squeaking" and there is:
    # 1. mouse, squeaking
    # 2. toy, squeaking
    # the more likely match SHOULD be the toy since it's
    # inanimate like rubber, but with the current implementation,
    # BOTH are matched with "squeaking", and the mouse
    # might play
