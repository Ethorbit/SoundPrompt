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
            # TODO: make interactive prompt have a history like a terminal
            prompt = args.prompt or input(">>>").lower()

            prompt_embedding = model.encode(prompt.lower())
            top_n_results = collection.query(
                query_embeddings=[prompt_embedding],
                n_results=10
            )

            # TODO: add Reranking & Rerank model
            # The current query is pretty accurate, but
            # there are a few times where out of the 10
            # items, the first is not the most accurate
            # Reranking can solve that issue

            # Deduplicate, keep only the first tag of a file
            unique_metadatas = []
            unique_distances = []
            seen_files = set()
            for metadata, distance in zip(
                top_n_results["metadatas"][0],
                top_n_results["distances"][0]
            ):
                file_path = metadata["tag_file"]
                if file_path not in seen_files:
                    seen_files.add(file_path)
                    unique_metadatas.append(metadata)
                    unique_distances.append(distance)

            distinct_top_n_results = {
                "metadatas": [unique_metadatas],
                "distances": [unique_distances]
            }

            # We need to do chunk-level scoring with file-level
            # aggregation
            #
            # 1. Each tag is treated as a chunk
            # 2. We compute the similarity between the query
            # embedding and the embedding of each tag individually.
            # 3. This gives a score per chunk.

            for meta, dist in zip(
                distinct_top_n_results["metadatas"][0],
                distinct_top_n_results["distances"][0]
            ):
                # Get meta file_path, do query to get all tags OF file_path
                # Create a list of scores by iterating each tag and appending
                # the simularity from the tag to the prompt
                #
                # Choose the file with the best score - that's the match!
                file_results = collection.get(
                    where={"tag_file": meta["tag_file"]}
                )

                for file_result in file_results["metadatas"]:
                    print(file_result["tag_file"])
                    print(file_result["tag"])

            if args.prompt:
                break
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
