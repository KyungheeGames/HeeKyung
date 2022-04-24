from discord import Intents
from discord.ext import commands

import os
import logging
from dotenv import load_dotenv

load_dotenv(verbose=True)


class HeeKyung(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("PREFIX")),
            description="HeeKyung",
            intents=Intents.all(),
            help_command=None,
        )
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.INFO)
        fileHandler = logging.FileHandler(
            filename="discord.log", encoding="utf-8", mode="w"
        )
        fileHandler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(streamHandler)
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}")
                self.logger.info(f"Loaded {file}")
        self.load_extension("jishaku")
        self.logger.info("Loaded jishaku")


if __name__ == "__main__":
    HeeKyung().run(os.getenv("TOKEN"))
