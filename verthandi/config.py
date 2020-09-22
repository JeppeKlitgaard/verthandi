"""
Contains configuration related code for Verthandi.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, Union

import appdirs
import tomlkit
from pydantic import BaseSettings

logger = logging.getLogger(__name__)

_ConfigFileT = Optional[Union[str, Path]]


def _get_appdirs_path() -> Path:
    path = Path(appdirs.user_config_dir("Verthandi", False)) / "verthandi.toml"

    return path


class VerthandiSettings(BaseSettings):
    """
    Settings used by Verthandi.
    """

    BASE_URL: str = "https://api.clockify.me/api/v1"
    API_KEY: Optional[str] = None

    def to_str(self) -> str:
        """
        Returns the settings object as a serialised TOML string.

        Returns:
            str: Settings as TOML string.
        """
        return tomlkit.dumps(self.dict())

    @classmethod
    def load(cls, filepath: _ConfigFileT = None) -> VerthandiSettings:
        """
        Loads the User Settings from the user settings file.

        Args:
            filepath (_ConfigFileT, optional): Filepath to load from.
                If None the appdirs settings path will be used.
                Defaults to None.
        """
        if filepath is None:
            filepath = _get_appdirs_path()

        logger.info("Loading User Settings from %s", filepath)

        try:
            with open(filepath, "r") as f:
                data = tomlkit.parse(f.read())

            return cls.parse_obj(data)

        except (PermissionError, FileNotFoundError):
            logger.info("No User Settings file found. Creating empty User Settings.")

            settings_ = cls()
            settings_.save()

            return settings_

    def save(self, filepath: _ConfigFileT = None) -> None:
        """
        Saves the settings to the settings file

        Args:
            filepath (_ConfigFileT, optional): Filepath to save to.
                If None the appdirs settings path will be used.
                Defaults to None.
        """

        if filepath is None:
            filepath = _get_appdirs_path()

        if isinstance(filepath, str):
            filepath = Path(filepath)

        logger.info("Saving config to path: %s", filepath)

        # Create directories if needed
        os.makedirs(filepath.parent, mode=0o775, exist_ok=True)

        with open(filepath, "w") as f:
            f.write(self.to_str())


settings = VerthandiSettings.load()
