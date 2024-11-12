from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from typing_extensions import Self

from ..name import SchemaName
from .base import SchemaBase
from .registry import SCHEMAS

__all__ = ("Sensor", "SensorModality")


class SensorModality(str, Enum):
    """An enum to represent sensor modalities.

    Attributes:
        LIDAR: Lidar sensor.
        CAMERA: Camera sensor.
        RADAR: Radar sensor.
    """

    LIDAR = "lidar"
    CAMERA = "camera"
    RADAR = "radar"


@dataclass
@SCHEMAS.register(SchemaName.SENSOR)
class Sensor(SchemaBase):
    """A dataclass to represent schema table of `sensor.json`.

    Attributes:
        token (str): Unique record identifier.
        channel (str): Sensor channel name.
        modality (SensorModality): Sensor modality.

    Shortcuts:
    ---------
        first_sd_token (str): The first sample data token corresponding to its sensor channel.
    """

    token: str
    channel: str
    modality: SensorModality

    # shortcuts
    first_sd_token: str = field(init=False)

    @staticmethod
    def shortcuts() -> tuple[str] | None:
        return ("first_sd_token",)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        token: str = data["token"]
        channel = data["channel"]
        modality = SensorModality(data["modality"])

        return cls(token=token, channel=channel, modality=modality)
