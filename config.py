import os
import random

from dotenv import load_dotenv

load_dotenv()

# Mqtt Configuration
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
MQTT_BASE_TOPIC = os.environ.get("MQTT_BASE_TOPIC", "gpsno/simulation")
MQTT_CLIENT_ID = os.environ.get(
    "MQTT_CLIENT_ID",
    f"gps-no-simulation_{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}",
)
RETAIN_MESSAGES = os.environ.get("RETAIN_MESSAGES", "True").lower() in (
    "true",
    "1",
    "t",
)
CLEAR_RETAINED_ON_START = os.environ.get(
    "CLEAR_RETAINED_ON_START", "False"
).lower() in (
    "true",
    "1",
    "t",
)

# General Configuration
UPDATE_INTERVAL = float(os.environ.get("UPDATE_INTERVAL", "1.0"))
NUM_ANCHORS = int(os.environ.get("NUM_ANCHORS", "4"))
NUM_TAGS = int(os.environ.get("NUM_TAGS", "1"))
SIZE_X = int(os.environ.get("SIZE_X", "1000"))
SIZE_Y = int(os.environ.get("SIZE_Y", "1000"))
REALISTIC_MOVEMENT = os.environ.get("REALISTIC_MOVEMENT", "False").lower() in (
    "true",
    "1",
    "t",
)
DISTANCE_SCALING_FACTOR = float(os.environ.get("DISTANCE_SCALING_FACTOR", "1.0"))
REGENERATE_POSITIONS = os.environ.get("REGENERATE_POSITIONS", "False").lower() in (
    "true",
    "1",
    "t",
)
MOVEMENT_SPEED = float(os.environ.get("MOVEMENT_SPEED", "10.0"))
TARGET_POINT_OFFSET_RADIUS = int(os.environ.get("TARGET_POINT_OFFSET_RADIUS", "200"))
TARGET_POINT_PROXIMITY = float(os.environ.get("TARGET_PROXIMITY", "25.0"))
FORCE_CLUSTER_RANGING = os.environ.get(
    "FORCE_CLUSTER_RANGING", "False"
).lower() in ("true", "1", "t")

# Storage Configuration
STORAGE_TYPE = os.environ.get("STORAGE_TYPE", "sqlite")
DB_PATH = os.environ.get("DB_PATH", "simulation.db")
JSON_PATH = os.environ.get("JSON_PATH", "simulation.json")

# Cluster-Konfiguration
DEFAULT_CLUSTER = os.environ.get("DEFAULT_CLUSTER", None)

# Logging-Konfiguration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
