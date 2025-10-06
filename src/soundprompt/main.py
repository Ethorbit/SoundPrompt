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


async def main_async():
    import logging

    from soundprompt.config.toml.config import ConfigSystem
    from soundprompt.config import args
    from soundprompt.version import get_version
    args = args.get_args()                     # noqa: E402
    cfg = ConfigSystem(args).config            # noqa: E402
    logging.basicConfig(level=logging.INFO)    # noqa: E402
    logger = logging.getLogger(__name__)       # noqa: E402

    if args.version:
        print(get_version())
        exit()

    if args.load and args.save:
        logger.error("You cannot load and save at the same time!")
        exit()
    if not args.load and not args.save:
        logger.error("You must specify either --load or --save!")
        exit()

    print(get_version())
    logger.info("Loading model..")  # noqa: E402 sentence_transformers: ~7s delay

    from soundprompt.sound import SoundPlayer
    from soundprompt.device import get_device
    from soundprompt.console import Console, CommandQueue
    from soundprompt.retrieval.prompter import Prompter
    from soundprompt.data import database
    from sentence_transformers import SentenceTransformer
    from pynput import keyboard

    event_loop = asyncio.get_event_loop()

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

        def enter_prompt(prompt: str, interactive: bool):
            file = prompter.prompt(prompt)

            try:
                logger.debug(f"Prompted {file}")

                if interactive:
                    sound_player.play(file, blocking=False)
                else:
                    sound_player.play(file, blocking=True)
            except Exception as e:
                logger.error(
                    f"Failed to play sound - {e}"
                )

        def press_stop_sound():
            logger.debug("stop_sound hotkey")
            try:
                sound_player.stop()
            except Exception as e:
                logger.error(f"Failed to stop sound - {e}")

        if args.prompt:
            enter_prompt(args.prompt, interactive=False)
        else:
            keyboard.GlobalHotKeys({
                cfg.hotkeys.stop_sound:
                    press_stop_sound
            }).start()

            command_queue = CommandQueue()
            command_queue.event.subscribe(
                lambda cmd: enter_prompt(cmd, interactive=True)
            )
            console = Console(command_queue)

            asyncio.create_task(command_queue.run())
            console_task = asyncio.create_task(console.run())
            await console_task
            command_queue.stop()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    asyncio.run(main_async())
