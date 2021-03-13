import json
import os
import sys
from typing import Any, Optional
from ..utils.logging import get_logger

CONFIG_DIR_NAME = "config"
logger = get_logger("bot")

class BaseConfig(dict):
    DEFAULT_CONFIG = {}

    def __init__(self, file_name: str, required: bool) -> None:
        super().__init__(self)
        self._file_path = os.path.join(os.getcwd(), CONFIG_DIR_NAME, file_name)
        self.required = required
        self._load_from_file()

    def _load_from_file(self) -> None:
        """
        Loads the config from `self._file_path`
        Writes DEFAULT_CONFIG if there is no valid config file at the path
        """
        try:
            with open(self._file_path) as f:
                self.update(json.load(f))
            self._match_default(self, self._file_path)
        except FileNotFoundError:
            logger.warning(f"No file found at {self._file_path}! Writing Default!")
            self._write_default_config(self._file_path)
            if self.required:
                logger.error("Required config file has been generated. Please fill it out and restart!")
                sys.exit()

    @classmethod
    def _write_default_config(cls, file_path: str) -> None:
        """
        Writes the default config as specified in the class
        :param file_path: The path to the file which will be written
        :type file_path: str
        """
        with open(file_path, "w") as f:
            json.dump(cls.DEFAULT_CONFIG, f, indent=4, separators=(",", ":"))

    @classmethod
    def _match_default(cls, instance, file_path) -> None:
        """
        Compares current config with default config, and
        adds all missing keys to the config
        :param instance: The instance config to match
        :type instance: CongigBase
        """
        if cls.DEFAULT_CONFIG.keys() == instance.keys():
            return

        for key in cls.DEFAULT_CONFIG:
            if key not in instance:
                instance[key] = cls.DEFAULT_CONFIG[key]

        instance.save()
        if instance.required:
            logger.error(f"There are new fields in required config at {file_path}. Please fill it out and restart")
            sys.exit()

    def save(self) -> None:
        """
        Saves the current config
        """
        with open(self._file_path, "w") as f:
            json.dump(self, f, indent=4, separators=(",", ":"))


class MainConfig(BaseConfig):
    # The bot's default config
    DEFAULT_CONFIG = {
        "token": "",
        "prefixes": [],
        "server_logo": "",
        "main_guild_id": 1,
        "members_role": [],
        "operators_role": [],
        "api_secret": "",
        "servers": {
            "name": {
                "numerical_server_ip": "",
                "server_port": 25565,
                "rcon_port": 25575,
                "rcon_password": "",
                "operator": True,
                "litetech_additions": {
                    "address": "",
                    "bridge_channel_id": 0
                }
            }
        }
    }

    def __init__(self, file_name: str = "config.json") -> None:
        super().__init__(file_name, True)

class ModuleConfig(BaseConfig):
    def __init__(self, file_name: str = "modules_config.json") -> None:
        super().__init__(file_name, False)

    def _toggle_cog(self, module: str, cog_name: str, val: Optional[bool] = False) -> None:
        """
        Toggles whether or not a cog is enabled,
        sets to false by default or if the cog has not been registered previously.
        :param module: The module the cog belongs to
        :type module: str
        :param cog_name: The name of the cog
        :type cog_name: str
        :param val: The value to set the cog's status to
        :type val: Optional[bool]
        """
        try:
            self[module]["cogs"][cog_name] = val
        except KeyError:
            self[module]["cogs"] = {}
            self[module]["cogs"][cog_name] = val

        self.save()

    def cog_enabled(self, module: str, cog_name: str) -> bool:
        """
        Checks whether a cog is enabled. Registers it as false
        if the cog has not been previously registered
        :param module: The module the cog belongs to
        :type module: str
        :param cog_name: The name of the cog
        :type cog_name: str
        :return: Whether or not the cog is enabled
        :rtype: bool
        :raises: ModuleNotFoundError
        """
        if self.get(module) is None:
            raise ModuleNotFoundError

        try:
            return self[module]["cogs"][cog_name]
        except KeyError:
            self._toggle_cog(module, cog_name)
            logger.warning(f"The cog: {cog_name} for module: {module} has been registered. It is disabled by default, you can enable it at {self._file_path}")
            return False
