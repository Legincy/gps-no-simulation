# GPS:No Simulator

A research tool developed at Bochum University of Applied Sciences for simulating ESP32 devices with DW3000 UWB chip behavior.

## Project Background

This simulator is part of the GPS:No research project at Bochum University of Applied Sciences focused on indoor positioning systems using Ultra-wideband (UWB) technology. It emulates data from ESP32 microcontrollers equipped with DW3000 UWB radio modules, allowing researchers to test positioning algorithms without deploying physical hardware.

## Technical Approach

The simulator creates virtual instances of two device types:
- Anchor nodes with fixed positions
- Mobile tags that collect distance measurements

It calculates realistic distance data based on time-of-flight principles and publishes this information via MQTT, mirroring the behavior of actual UWB hardware. The simulation accounts for typical measurement characteristics of the DW3000 chipset including error patterns and update frequencies.

## Setup and Configuration

### Requirements
- Python 3.10+
- MQTT broker
- Docker (optional)

### Environment Variables
#### MQTT Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| MQTT_BROKER | localhost | MQTT broker hostname or IP |
| MQTT_PORT | 1883 | MQTT broker port |
| MQTT_USERNAME |  | Username for MQTT authentication |
| MQTT_PASSWORD |  | Password for MQTT authentication |
| MQTT_BASE_TOPIC | gpsno/simulation | Base topic for MQTT messages |

#### Simulation Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| UPDATE_INTERVAL | 1.0 | Update frequency in seconds |
| NUM_ANCHORS | 4 | Number of anchor devices |
| NUM_TAGS | 1 | Number of tag devices |
| SIZE_X | 1000 | Environment width (in units)|
| SIZE_Y | 1000 | Environment height (in units)|
| REALISTIC_MOVEMENT | true | Enable realistic movement patterns |
| DISTANCE_SCALING_FACTOR | 1.0 | Adjust distance measurements |
| REGENERATE_POSITIONS | false | Reset positions on startup |
| MOVEMENT_SPEED | 10.0 | Movement speed in units/s |
| TARGET_POINT_OFFSET_RADIUS | 200 | Random target point radius |
| TARGET_POINT_PROXIMITY | 25.0 | Distance to reach target |

#### Storage Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| STORAGE_TYPE | sqlite | Storage backend type |
| DB_PATH | data/simulation.db | Path to SQLite database file |

## Data Protocol

The simulator publishes data to the following MQTT topics:

```
{BASE_TOPIC}/devices/{DEVICE_NAME}/dev/position/x
{BASE_TOPIC}/devices/{DEVICE_NAME}/dev/position/y
{BASE_TOPIC}/devices/{DEVICE_NAME}/dev/target_point/x  # For tags
{BASE_TOPIC}/devices/{DEVICE_NAME}/dev/target_point/y  # For tags
{BASE_TOPIC}/devices/{DEVICE_NAME}/uwb/ranging         # Distance data
{BASE_TOPIC}/devices/{DEVICE_NAME}/dev/json            # Complete device state
{BASE_TOPIC}/devices/{DEVICE_NAME}/name                # Device name
{BASE_TOPIC}/devices/{DEVICE_NAME}/type                # Device type (anchor/tag)
{BASE_TOPIC}/devices/{DEVICE_NAME}/mac_address         # Device MAC address
```

Distance measurements are published in JSON format:
```json
[
  {
    "mac_address": "ab:cd:ef:12:34:56",
    "distance": {
      "raw_distance": 354.6,
      "scaled_distance": 354.6
    }
  }
]
```

## Development

### Local Setup
```bash
# Clone repository
git clone https://github.com/Legincy/gps-no-simulation.git
cd gps-no-simulation

# Install dependencies
pip install -r requirements.txt

# Run simulator
python main.py
```

### Docker Deployment
```bash
# Using docker-compose
docker-compose up -d

# Using docker directly
docker run -d --name gps-no-simulation \
  -v ./data:/app/data \
  --env-file .env \
  git.peth.pl/legincy/gps-no-simulation:latest
```

## Research Application

This simulator supports research on:
- Indoor positioning in GPS-denied environments
- Optimization of trilateration algorithms
- Sensor fusion techniques
- Movement prediction models
