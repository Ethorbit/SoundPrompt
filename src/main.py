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

import readline
from retrieval.prompter import Prompter
from config import args, config as config_import
from data import database
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
    prompter = Prompter(model=model, collection=collection)

    if args.prompt:
        file = prompter.prompt(args.prompt)
        print(file)
    else:  # Interactive
        while True:
            try:
                cmd = input(">>>").strip().lower()
                if not cmd:
                    continue

                readline.add_history(cmd)
                file = prompter.prompt(cmd)
                print(file)
            except (KeyboardInterrupt, EOFError):
                print("\nInterrupted. Exiting...")
                break
