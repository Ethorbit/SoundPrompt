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

# TODO: add VTT

import asyncio


async def main():
    import logging
    from soundprompt.config.toml.config import ConfigSystem
    from soundprompt.config import args
    args = args.get_args()                     # noqa: E402
    cfg = ConfigSystem(args).config            # noqa: E402
    logging.basicConfig(level=logging.INFO)    # noqa: E402
    logger = logging.getLogger(__name__)       # noqa: E402
    logger.info("Loading model..")  # noqa: E402 sentence_transformers: ~7s delay

    from soundprompt.sound import SoundPlayer
    from soundprompt.device import get_device
    from soundprompt.console import Console, CommandQueue
    from soundprompt.retrieval.prompter import Prompter
    from soundprompt.data import database
    from sentence_transformers import SentenceTransformer
    from pynput import keyboard

    device = get_device(cfg.general.device)
    logger.info(f"Requested device: {device}")

    model_name = cfg.general.model_name
    model = SentenceTransformer(model_name, device=device)
    logger.info("Model ready!")

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.save or args.load:
        logger.info("Loading database...")
        data = database.Data(
            config=cfg,
            model=model,
            library_directory=(args.save or args.load),
            debug=args.debug
        )
        logger.info("Database ready!")

    if args.save:
        logger.info("Saving..")

        try:
            data.update()
        except Exception as e:
            logger.error(f"Failed to save - {e}")
        finally:
            logger.info("Saved")

    if args.load:
        collection = data.get_collection()
        prompter = Prompter(model=model, collection=collection)
        sound_player = SoundPlayer()

        def enter_prompt(prompt: str):
            file = prompter.prompt(prompt)

            try:
                logger.debug(f"Prompted {file}")
                sound_player.play(file)
            except Exception as e:
                logger.error(
                    f"Failed to play sound - {e}"
                )

        def press_stop_sound():
            logger.debug("stop_sound hotkey")
            sound_player.stop()

        if args.prompt:
            enter_prompt(args.prompt)
        else:
            # TODO: fix hotkey and sound blocking
            # this thread that users will be
            # typing prompts on
            keyboard.GlobalHotKeys({
                cfg.hotkeys.stop_sound:
                    press_stop_sound
            }).start()

            command_queue = CommandQueue()
            command_queue.event.subscribe(
                lambda cmd: enter_prompt(cmd)
            )
            console = Console(command_queue)

            asyncio.create_task(command_queue.run())
            console_task = asyncio.create_task(console.run())
            await console_task
            command_queue.stop()

if __name__ == "__main__":
    asyncio.run(main())
