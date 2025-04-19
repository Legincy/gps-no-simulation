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
        retain_messages: bool,
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
        self.retain_messages = retain_messages
        self.retained_topics = set()

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

    def publish(self, topic: str, payload: str, retain: bool = None) -> None:
        if not self.connected or not self.mqtt_client:
            logging.warning(
                "There is no connection to the MQTT broker. Cannot publish message."
            )
            return

        if retain is None:
            retain = self.retain_messages

        if retain:
            self.retained_topics.add(topic)

        self.mqtt_client.publish(topic, payload, qos=0, retain=retain)

    def clear_retained_messages(self) -> None:
        if not self.connected or not self.mqtt_client:
            logging.warning(
                "There is no connection to the MQTT broker. Cannot clear retained messages."
            )
            return

        logging.info(
            f"Clearing {len(self.retained_topics)} tracked retained messages..."
        )
        for topic in self.retained_topics:
            try:
                self.mqtt_client.publish(topic, "", qos=0, retain=True)
            except Exception as e:
                logging.error(f"Error clearing retained message for topic {topic}: {e}")

        logging.info("All tracked retained messages cleared")
        self.retained_topics.clear()

    def clear_all_retained_messages(self) -> None:
        if not self.connected or not self.mqtt_client:
            logging.warning(
                "There is no connection to the MQTT broker. Cannot clear retained messages."
            )
            return

        try:
            wildcard_topic = f"{self.base_topic}/#"

            received_topics = set()

            def on_message(client, userdata, msg):
                if msg.retain:
                    received_topics.add(msg.topic)

            previous_on_message = self.mqtt_client.on_message
            self.mqtt_client.on_message = on_message

            self.mqtt_client.subscribe(wildcard_topic)
            logging.info(
                f"Subscribed to {wildcard_topic} to discover retained messages"
            )

            time.sleep(1)

            logging.info(
                f"Clearing {len(received_topics)} discovered retained messages"
            )
            for topic in received_topics:
                try:
                    self.mqtt_client.publish(topic, "", qos=0, retain=True)
                except Exception as e:
                    logging.error(
                        f"Error clearing retained message for topic {topic}: {e}"
                    )

            self.mqtt_client.unsubscribe(wildcard_topic)
            self.mqtt_client.on_message = previous_on_message

            logging.info("Finished clearing retained messages")

        except Exception as e:
            logging.error(f"Error while clearing all retained messages: {e}")

        self.retained_topics.clear()

    def disconnect(self) -> None:
        if self.mqtt_client:
            try:
                if self.connected:
                    self.clear_retained_messages()

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

        station.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for field in updated_fields:
            field_updated = True

            match field:
                case "mac_address":
                    self.publish(f"{base_topic}/device/mac_address", station.mac_address)
                case "name":
                    self.publish(f"{base_topic}/device/name", station.name)
                case "device_type":
                    self.publish(f"{base_topic}/uwb/type", station.device_type_str)
                case "cluster_name":
                    self.publish(
                        f"{base_topic}/uwb/cluster/name",
                        (
                            "None"
                            if station.cluster_name is None
                            else station.cluster_name
                        ),
                    )
                case "cluster_stations":
                    self.publish(
                        f"{base_topic}/uwb/cluster/stations",
                        json.dumps(station.cluster_foreign_mac_addresses),
                    )
                case "randomizer":
                    self.publish(
                        f"{base_topic}/device/randomizer", str(station.randomizer)
                    )
                case "position":
                    pos = station.position
                    self.publish(f"{base_topic}/device/position/x", str(pos["x"]))
                    self.publish(f"{base_topic}/device/position/y", str(pos["y"]))
                case "target_point":
                    target = station.target_point
                    if target and station.device_type == DeviceType.TAG:
                        self.publish(
                            f"{base_topic}/device/target_point/x", str(target["x"])
                        )
                        self.publish(
                            f"{base_topic}/device/target_point/y", str(target["y"])
                        )
                case "ranging_data":
                    self.publish(
                        f"{base_topic}/uwb/ranging",
                        json.dumps(station.ranging_data),
                    )
                case "created_at":
                    self.publish(f"{base_topic}/device/created_at", station.created_at)
                case "updated_at":
                    self.publish(f"{base_topic}/device/updated_at", station.updated_at)
                case "started_at":
                    self.publish(f"{base_topic}/device/started_at", station.started_at)
                case _:
                    field_updated = False

                    logging.warning(
                        f"Unknown field '{field}' in station {station.name} ({station.mac_address})"
                    )

            if field_updated:
                station.remove_from_updated_fields(field)

        self.publish(f"{base_topic}/device/raw", json.dumps(station.as_dict))
        self.publish(f"{base_topic}/device/updated_at", station.updated_at)
        self.publish(f"{base_topic}/device/uptime", station.uptime_in_ms)

    def publish_status(self, stations: List[Station]) -> None:
        if not self.connected or not self.mqtt_client:
            logging.warning(
                "There is no connection to the MQTT broker. Cannot publish status."
            )
            return

        for station in stations:
            self.publish_station(station)
            time.sleep(0.1)
