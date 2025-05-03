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
        self._startedAt = None

        if device_type:
            self.device_type = device_type
        else:
            self.device_type = DeviceType.NONE

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

        if target_point:
            self.target_point = target_point

        if cluster_stations:
            self.cluster_stations = cluster_stations

        if created_at:
            self.created_at = created_at

        self.cluster_name = cluster_name 
        self.cluster_stations = cluster_stations or []
        self.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

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
            "uwb": {
                "device_type": self.device_type_str,
                "cluster": {
                "name": self._cluster_name,
                "devices": [device.mac_address for device in self._cluster_stations],
            },
            },
            "device": {
                "mac_address": self._mac_address,
                "name": self._name,
                "randomizer": self._randomizer,
                "updated_at": self._updated_at,
                "created_at": self._created_at,
                "started_at": self._started_at,
                "uptime": self.uptime_in_ms,
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
    
    @property
    def uptime_in_ms(self) -> int:
        return int(
            (datetime.now() - datetime.strptime(self.started_at, "%Y-%m-%d %H:%M:%S")).total_seconds() * 1000
        )
    
    @property
    def started_at(self) -> str:
        return self._started_at
    
    @started_at.setter
    def started_at(self, new_started_at: str) -> None:
        if "started_at" not in self._updated_fields:
            self._updated_fields.append("started_at")
        self._started_at = new_started_at

    @mac_address.setter
    def mac_address(self, new_mac_address: str) -> None:
        if "mac_address" not in self._updated_fields:
            self._updated_fields.append("mac_address")
        self._mac_address = new_mac_address

    @name.setter
    def name(self, new_name: str) -> None:
        if "name" not in self._updated_fields:
            self._updated_fields.append("name")
        self._name = new_name

    @randomizer.setter
    def randomizer(self, new_randomizer: float) -> None:
        if not (0 <= new_randomizer <= 1):
            raise ValueError("Randomizer must be between 0 and 1.")

        if "randomizer" not in self._updated_fields:
            self._updated_fields.append("randomizer")

        self._randomizer = new_randomizer

    @device_type.setter
    def device_type(self, new_device_type: Union[str, DeviceType]) -> None:
        if "device_type" not in self._updated_fields:
            self._updated_fields.append("device_type")

        if isinstance(new_device_type, str):
            self._device_type = DeviceType[new_device_type.upper()]
        elif isinstance(new_device_type, DeviceType):
            self._device_type = new_device_type
        else:
            raise ValueError("Invalid device type provided.")

    @updated_at.setter
    def updated_at(self, new_updated_at: str) -> None:
        if "updated_at" not in self._updated_fields:
            self._updated_fields.append("updated_at")

        self._updated_at = new_updated_at

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    @created_at.setter
    def created_at(self, new_created_at: str) -> None:
        if "created_at" not in self._updated_fields:
            self._updated_fields.append("created_at")

        self._created_at = new_created_at

    @cluster_name.setter
    def cluster_name(self, new_cluster_name: str) -> None:
        if "cluster_name" not in self._updated_fields:
            self._updated_fields.append("cluster_name")

        self._cluster_name = new_cluster_name

    @position.setter
    def position(self, new_position: Dict[str, float]) -> None:
        if "position" not in self._updated_fields:
            self._updated_fields.append("position")

        self._position = new_position

    @target_point.setter
    def target_point(self, new_target: Dict[str, float]) -> None:
        if "target_point" not in self._updated_fields:
            self._updated_fields.append("target_point")

        self._target_point = new_target

    @cluster_stations.setter
    def cluster_stations(self, devices: List["Station"]) -> None:
        if "cluster_stations" not in self._updated_fields:
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

        anchor_info = {"source_address": self._mac_address , "destination_address": anchor.mac_address, "distance": distance_data}

        for datapoint in self._ranging_data:
            if datapoint["destination_address"] == anchor.mac_address:
                datapoint["distance"] = distance_data
                break
        else:
            self._ranging_data.append(anchor_info)

        if "ranging_data" not in self._updated_fields:
            self._updated_fields.append("ranging_data")
