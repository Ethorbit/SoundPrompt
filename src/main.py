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
from data import database, retrieval
from sentence_transformers import SentenceTransformer
cfg = config_import.load_config()

model_name = cfg["general"]["model_name"]
model = SentenceTransformer(model_name)

args = args.get_args()

if args.save or args.load:
    data = database.Data(
        config=cfg,
        model=model,
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

            top_results = retrieval.get_top_results(
                collection,
                embedding=prompt_embedding,
                limit=10
            )

            deduplicated_top_results = retrieval.deduplicate_results(
                top_results
            )

            scored_files = retrieval.get_cumulative_file_scores(
                collection,
                embedding=prompt_embedding,
                result=deduplicated_top_results
            )

            selected_file = retrieval.get_highest_scored_file(scored_files)

            print(top_results)
            print(scored_files)
            print(selected_file)

            # If it's not interactive, stop immediately
            if args.prompt:
                break
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break
