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
# If not, see <https://www.gnu.org/licenses/>.

# TODO: add VTT and multithreading to handle both VTT
# and console commands

from soundprompt.console import Console, CommandLoop
from soundprompt.retrieval.prompter import Prompter
from soundprompt.config import args
from soundprompt.config.config import load_config
from soundprompt.data import database
from sentence_transformers import SentenceTransformer
cfg = load_config()

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
    else:
        def on_command(cmd: str):
            print(f"Yes. {cmd}")

        commandLoop = CommandLoop()
        commandLoop.event.subscribe(on_command)
        console = Console(commandLoop)
        t1 = commandLoop.start()
        t2 = console.interactive()
        t2.join()
        commandLoop.stop()
