import math
import random
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class DeviceType(Enum):
    ANCHOR = "ANCHOR"
    TAG = "TAG"
    NONE = "NONE"


class Station:
    def __init__(
        self,
        mac_address: Optional[str] = None,
        name: Optional[str] = None,
        device_type: DeviceType = None,
        position: Optional[Dict[str, float]] = None,
        randomizer: Optional[float] = None,
        cluster_name: Optional[str] = None,
        target_point: Optional[Dict[str, float]] = None,
        cluster_stations: Optional[List["Station"]] = None,
        created_at: Optional[str] = None,
    ):
        self._updated_fields = []

        self._mac_address = None
        self._name = None
        self._position = {"x": 0, "y": 0}
        self._randomizer = None
        self._cluster_name = None
        self._target_point = {"x": 0, "y": 0}
        self._cluster_stations = []
        self._ranging_data = []
        self._created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._updated_at = None

        if isinstance(device_type, str):
            try:
                self._device_type = DeviceType[device_type.upper()]
            except KeyError:
                raise ValueError(f"Invalid device type: {device_type}")
        elif isinstance(device_type, DeviceType):
            self._device_type = device_type
        else:
            self._device_type = DeviceType.NONE

        if mac_address:
            self.mac_address = mac_address
        else:
            self.mac_address = self._generate_mac()

        if name:
            self.name = name
        else:
            self.name = self._generate_name()

        if position:
            self.position = position

        if randomizer:
            self.randomizer = randomizer
        else:
            self.randomizer = random.uniform(0.1, 0.9)

        if cluster_name:
            self.cluster_name = cluster_name

        if target_point:
            self.target_point = target_point

        if cluster_stations:
            self.cluster_stations = cluster_stations

        if created_at:
            self.created_at = created_at

    def _generate_mac(self) -> str:
        xx1 = format(random.randint(0, 255), "02x")
        xx2 = format(random.randint(0, 255), "02x")
        xx3 = format(random.randint(0, 255), "02x")
        return f"ab:cd:ef:{xx1}:{xx2}:{xx3}"

    def _generate_name(self) -> str:
        if hasattr(self, "mac_address"):
            parts = self.mac_address.split(":")
            if len(parts) >= 6:
                last_parts = "".join(parts[3:]).lower()
                return f"GPS:No Station-{last_parts}"

        xx1 = format(random.randint(0, 255), "02x")
        xx2 = format(random.randint(0, 255), "02x")
        xx3 = format(random.randint(0, 255), "02x")
        last_six = f"{xx1}{xx2}{xx3}".lower()
        return f"GPS:No Station-{last_six}"

    def set_random_position(self, size_x: int, size_y: int) -> None:
        self.position = {"x": random.randint(0, size_x), "y": random.randint(0, size_y)}

    def set_random_target_point(
        self, size_x: int, size_y: int, offset_radius: int
    ) -> None:
        self.target_point = {
            "x": max(
                0,
                min(
                    size_x,
                    self.position["x"] + random.randint(-offset_radius, offset_radius),
                ),
            ),
            "y": max(
                0,
                min(
                    size_y,
                    self.position["y"] + random.randint(-offset_radius, offset_radius),
                ),
            ),
        }

    @property
    def as_dict(self) -> Dict[str, Any]:
        return {
            "mac_address": self._mac_address,
            "name": self._name,
            "type": self.device_type_str,
            "cluster": {
                "name": self._cluster_name,
                "devices": [device.mac_address for device in self._cluster_stations],
            },
            "dev": {
                "position": self._position,
                "target_point": self._target_point,
                "randomizer": self._randomizer,
                "updated_at": self._updated_at,
                "created_at": self._created_at,
            },
        }

    @property
    def mac_address(self) -> str:
        return self._mac_address

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_type(self) -> str:
        return self._device_type

    @property
    def device_type_str(self) -> str:
        return self._device_type.value

    @property
    def cluster_name(self) -> str:
        return self._cluster_name

    @property
    def cluster_stations(self) -> List["Station"]:
        return self._cluster_stations

    @property
    def cluster_foreign_mac_addresses(self) -> List[str]:
        return [station.mac_address for station in self._cluster_stations]

    @property
    def randomizer(self) -> float:
        return self._randomizer

    @property
    def updated_at(self) -> str:
        return self._updated_at

    @property
    def position(self) -> Dict[str, float]:
        return self._position

    @property
    def target_point(self) -> Dict[str, float]:
        return self._target_point

    @property
    def cluster_stations(self) -> List["Station"]:
        return self._cluster_stations

    @property
    def updated_fields(self) -> List[str]:
        return self._updated_fields

    @property
    def ranging_data(self) -> List[Dict[str, Any]]:
        return self._ranging_data

    @mac_address.setter
    def mac_address(self, new_mac_address: str) -> None:
        if not "mac_address" in self._updated_fields:
            self._updated_fields.append("mac_address")
        self._mac_address = new_mac_address

    @name.setter
    def name(self, new_name: str) -> None:
        if not "name" in self._updated_fields:
            self._updated_fields.append("name")
        self._name = new_name

    @randomizer.setter
    def randomizer(self, new_randomizer: float) -> None:
        if not (0 <= new_randomizer <= 1):
            raise ValueError("Randomizer must be between 0 and 1.")

        if not "randomizer" in self._updated_fields:
            self._updated_fields.append("randomizer")

        self._randomizer = new_randomizer

    @device_type.setter
    def device_type(self, new_device_type: Union[str, DeviceType]) -> None:
        if isinstance(new_device_type, str):
            self._device_type = DeviceType[new_device_type.upper()]
        elif isinstance(new_device_type, DeviceType):
            self._device_type = new_device_type
        else:
            raise ValueError("Invalid device type provided.")

        if not "device_type" in self._updated_fields:
            self._updated_fields.append("device_type")

    @updated_at.setter
    def updated_at(self, new_updated_at: str) -> None:
        if not "updated_at" in self._updated_fields:
            self._updated_fields.append("updated_at")

        self._updated_at = new_updated_at

    @property
    def created_at(self) -> Optional[str]:
        if "created_at" in self._updated_fields:
            self._updated_fields.remove("created_at")

        return self._created_at

    @created_at.setter
    def created_at(self, new_created_at: str) -> None:
        if not "created_at" in self._updated_fields:
            self._updated_fields.append("created_at")

        self._created_at = new_created_at

    @cluster_name.setter
    def cluster_name(self, new_cluster_name: str) -> None:
        if not "cluster_name" in self._updated_fields:
            self._updated_fields.append("cluster_name")

        self._cluster_name = new_cluster_name

    @position.setter
    def position(self, new_position: Dict[str, float]) -> None:
        if not "position" in self._updated_fields:
            self._updated_fields.append("position")

        self._position = new_position

    @target_point.setter
    def target_point(self, new_target: Dict[str, float]) -> None:
        if not "target_point" in self._updated_fields:
            self._updated_fields.append("target_point")

        self._target_point = new_target

    @cluster_stations.setter
    def cluster_stations(self, devices: List["Station"]) -> None:
        if not "cluster_stations" in self._updated_fields:
            self._updated_fields.append("cluster_stations")

        self._cluster_stations = devices

    def remove_from_updated_fields(self, field: str) -> None:
        if field in self._updated_fields:
            self._updated_fields.remove(field)

    def is_anchor(self) -> bool:
        return self._device_type == DeviceType.ANCHOR

    def is_tag(self) -> bool:
        return self._device_type == DeviceType.TAG

    def move(
        self,
        speed: float,
        realistic_movement: bool,
        target_proximity: float,
        size_x: int,
        size_y: int,
    ) -> bool:
        if not self.is_tag():
            return False

        if realistic_movement and random.random() > self._randomizer:
            return False

        dx = self.target_point["x"] - self.position["x"]
        dy = self.target_point["y"] - self.position["y"]
        angle = math.atan2(dy, dx)

        new_x = self.position["x"] + speed * math.cos(angle)
        new_y = self.position["y"] + speed * math.sin(angle)

        new_x = max(0, min(size_x, new_x))
        new_y = max(0, min(size_y, new_y))

        self.position = {"x": new_x, "y": new_y}

        if (
            abs(new_x - self.target_point["x"]) < target_proximity
            and abs(new_y - self.target_point["y"]) < target_proximity
        ):
            self.target_point = {
                "x": random.randint(0, size_x),
                "y": random.randint(0, size_y),
            }

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mac_address": self.mac_address,
            "name": self.name,
            "randomizer": self.randomizer,
            "updated_at": self.updated_at,
            "uwb": self.raw_data,
        }

    def add_distance_to_anchor(
        self, anchor: "Station", distance_data: Dict[str, float]
    ) -> None:
        if not self.is_tag():
            return

        anchor_info = {"mac_address": anchor.mac_address, "distance": distance_data}

        for device in self._ranging_data:
            if device["mac_address"] == anchor.mac_address:
                device["distance"] = distance_data
                break
        else:
            self._ranging_data.append(anchor_info)

        if "ranging_data" not in self._updated_fields:
            self._updated_fields.append("ranging_data")
