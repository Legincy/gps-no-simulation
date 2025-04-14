import json
import logging
import time
from datetime import datetime
from typing import Callable, List, Optional

from models.station import DeviceType, Station

try:
    import paho.mqtt.client as mqtt
except ImportError:
    logging.error(
        "Couldn't import paho-mqtt. Please install it with 'pip install paho-mqtt'"
    )
    raise


class MqttService:
    def __init__(
        self,
        broker: str,
        port: int = 1883,
        user: Optional[str] = None,
        password: Optional[str] = None,
        base_topic: str = "gpsno/simulation",
        client_id: Optional[str] = None,
    ):
        self.broker = broker
        self.port = port
        self.user = user
        self.password = password
        self.base_topic = base_topic
        self.client_id = client_id
        self.mqtt_client = None
        self.connected = False
        self.on_connect_callback = None

    def set_on_connect_callback(self, callback: Callable) -> None:
        self.on_connect_callback = callback

    def connect(self) -> bool:
        try:
            try:
                self.mqtt_client = mqtt.Client(
                    client_id=self.client_id, protocol=mqtt.MQTTv5
                )
                self.mqtt_client.on_connect = self._on_connect_v5
            except Exception:
                self.mqtt_client = mqtt.Client(client_id=self.client_id)
                self.mqtt_client.on_connect = self._on_connect_v3

            if self.user and self.password:
                self.mqtt_client.username_pw_set(self.user, self.password)

            self.mqtt_client.connect(self.broker, self.port, 60)
            self.mqtt_client.loop_start()

            timeout = 10
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)

            if self.connected:
                logging.info(
                    f"Successfully connected to MQTT broker: {self.broker}:{self.port}"
                )
                return True
            else:
                logging.error(
                    f"Timeout while connecting to MQTT broker: {self.broker}:{self.port}"
                )
                self.disconnect()
                return False

        except Exception as e:
            logging.error(f"Error while connecting to MQTT broker: {e}")
            return False

    def _on_connect_v5(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            if self.on_connect_callback:
                self.on_connect_callback()
        else:
            logging.error(f"Error while connecting to MQTT broker, code: {rc}")
            self.connected = False

    def _on_connect_v3(self, client, userdata, flags, rc):
        self._on_connect_v5(client, userdata, flags, rc, None)

    def disconnect(self) -> None:
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                logging.info("Disconnected from MQTT broker")
            except Exception as e:
                logging.error(f"Error while disconnecting from MQTT broker: {e}")
        self.connected = False

    def publish_station(self, station: Station) -> None:
        if not self.connected or not self.mqtt_client:
            logging.warning(
                "There is no connection to the MQTT broker. Cannot publish station."
            )
            return []

        updated_fields = station.updated_fields
        base_topic = f"{self.base_topic}/devices/{station.name.replace(' ', '_').replace(':', '')}"

        if len(updated_fields) > 0:
            station.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"{station.as_dict}, {updated_fields}")

            for field in updated_fields:
                field_updated = True
                print(f"handling {field}")

                match field:
                    case "mac_address":
                        self.mqtt_client.publish(
                            f"{base_topic}/mac_address", station.mac_address
                        )
                    case "name":
                        self.mqtt_client.publish(f"{base_topic}/name", station.name)
                    case "device_type":
                        self.mqtt_client.publish(
                            f"{base_topic}/uwb/type", station.device_type_str
                        )
                    case "cluster_name":
                        self.mqtt_client.publish(
                            f"{base_topic}/uwb/cluster/name",
                            (
                                "None"
                                if station.cluster_name is None
                                else station.cluster_name
                            ),
                        )
                    case "cluster_stations":
                        self.mqtt_client.publish(
                            f"{base_topic}/uwb/cluster/stations",
                            json.dumps(station.cluster_foreign_mac_addresses),
                        )
                    case "randomizer":
                        self.mqtt_client.publish(
                            f"{base_topic}/dev/randomizer", str(station.randomizer)
                        )
                    case "position":
                        pos = station.position
                        self.mqtt_client.publish(
                            f"{base_topic}/dev/position/x", str(pos["x"])
                        )
                        self.mqtt_client.publish(
                            f"{base_topic}/dev/position/y", str(pos["y"])
                        )
                    case "target_point":
                        target = station.target_point
                        if target and station.device_type == DeviceType.TAG:
                            self.mqtt_client.publish(
                                f"{base_topic}/dev/target_point/x", str(target["x"])
                            )
                            self.mqtt_client.publish(
                                f"{base_topic}/dev/target_point/y", str(target["y"])
                            )
                    case "ranging_data":
                        self.mqtt_client.publish(
                            f"{base_topic}/uwb/ranging",
                            json.dumps(station.ranging_data),
                        )
                    case "created_at":
                        self.mqtt_client.publish(
                            f"{base_topic}/dev/created_at", station.created_at
                        )
                    case "updated_at":
                        self.mqtt_client.publish(
                            f"{base_topic}/dev/updated_at", station.updated_at
                        )
                    case _:
                        field_updated = False

                        logging.warning(
                            f"Unknown field '{field}' in station {station.name} ({station.mac_address})"
                        )

                if field_updated:
                    station.remove_from_updated_fields(field)

            self.mqtt_client.publish(
                f"{base_topic}/dev/json", json.dumps(station.as_dict)
            )
            self.mqtt_client.publish(f"{base_topic}/dev/updated_at", station.updated_at)

    def publish_status(self, stations: List[Station]) -> None:
        if not self.connected or not self.mqtt_client:
            logging.warning(
                "There is no connection to the MQTT broker. Cannot publish status."
            )
            return

        for station in stations:
            self.publish_station(station)
            time.sleep(0.1)
