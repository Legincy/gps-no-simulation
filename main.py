import logging
import signal
import sys
import time

import config
from models.station import DeviceType, Station
from models.storage import SqliteStorage, get_storage_instance
from services.mqtt_service import MqttService
from services.simulation_service import SimulationService


def setup_logging() -> None:
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)
    logging.info(f"Initialized logging with level: {log_level}")


def prepare_stations(
    simulation_service: SimulationService,
    storage,
    num_anchors: int,
    num_tags: int,
    regenerate_positions: bool = False,
) -> None:
    fetched_tags = storage.load_stations_by_device_type(DeviceType.TAG, num_tags)
    fetched_anchors = storage.load_stations_by_device_type(
        DeviceType.ANCHOR, num_anchors
    )
    simulation_service.stations.extend(fetched_tags + fetched_anchors)

    anchors_needed = max(0, num_anchors - len(simulation_service.anchors))
    tags_needed = max(0, num_tags - len(simulation_service.tags))

    if anchors_needed > 0:
        for _ in range(anchors_needed):
            new_anchor = Station(
                device_type=DeviceType.ANCHOR, cluster_name=config.DEFAULT_CLUSTER
            )

            new_anchor.set_random_position(size_x=config.SIZE_X, size_y=config.SIZE_Y)

            simulation_service.add_station(new_anchor)

    if tags_needed > 0:
        for _ in range(tags_needed):

            new_tag = Station(
                device_type=DeviceType.TAG, cluster_name=config.DEFAULT_CLUSTER
            )
            simulation_service.add_station(new_tag)

    for anchor in simulation_service.anchors:
        if regenerate_positions:
            anchor.set_random_position(size_x=config.SIZE_X, size_y=config.SIZE_Y)

        storage.update_station(anchor)

    for tag in simulation_service.tags:
        tag.position = {"x": 0, "y": 0}
        tag.set_random_target_point(
            size_x=config.SIZE_X,
            size_y=config.SIZE_Y,
            offset_radius=config.TARGET_POINT_OFFSET_RADIUS,
        )

        storage.update_station(tag)

    if anchors_needed > 0 or tags_needed > 0:
        logging.info(f"Created {anchors_needed} new anchors and {tags_needed} new tags")

        simulation_service.update_device_knowledge()

        for tag in simulation_service.tags:
            simulation_service.update_tag_distances(tag)

        storage.save_stations(simulation_service.stations)


def run_simulation(
    simulation_service: SimulationService,
    mqtt_service: MqttService,
    storage: SqliteStorage,
    interval: float,
) -> None:
    mqtt_service.publish_status(simulation_service.stations)

    logging.info("Started simulation loop")
    try:
        while True:
            num_moved = 0

            for tag in simulation_service.tags:
                if tag.move(
                    speed=config.MOVEMENT_SPEED,
                    realistic_movement=config.REALISTIC_MOVEMENT,
                    target_proximity=config.TARGET_POINT_PROXIMITY,
                    size_x=config.SIZE_X,
                    size_y=config.SIZE_Y,
                ):

                    simulation_service.update_tag_distances(tag)
                    num_moved += 1

            for station in simulation_service.stations:
                if len(station.updated_fields) > 0:
                    storage.update_station(station)
                    mqtt_service.publish_station(station)

            time.sleep(interval)

    except Exception as e:
        logging.error(f"Fehler in der Simulationsschleife: {e}")
        storage.save_stations(simulation_service.stations)


def setup_signal_handlers(mqtt_service, storage, simulation_manager):
    def signal_handler(sig, frame):
        logging.info("\nReceived signal to terminate. Saving state...")

        storage.save_stations(simulation_manager.stations)
        mqtt_service.disconnect()

        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    setup_logging()

    simulation_service = SimulationService(
        size_x=config.SIZE_X,
        size_y=config.SIZE_Y,
        distance_scaling_factor=config.DISTANCE_SCALING_FACTOR,
    )

    storage = get_storage_instance(
        storage_type=config.STORAGE_TYPE,
        db_path=config.DB_PATH,
        json_path=config.JSON_PATH,
    )

    prepare_stations(
        simulation_service=simulation_service,
        storage=storage,
        num_anchors=config.NUM_ANCHORS,
        num_tags=config.NUM_TAGS,
        regenerate_positions=config.REGENERATE_POSITIONS,
    )

    mqtt_service = MqttService(
        broker=config.MQTT_BROKER,
        port=config.MQTT_PORT,
        user=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD,
        base_topic=config.MQTT_BASE_TOPIC,
        client_id=config.MQTT_CLIENT_ID,
    )

    mqtt_connected = mqtt_service.connect()
    if not mqtt_connected:
        logging.warning("MQTT connection is not available - exiting simulation")
        sys.exit(1)

    setup_signal_handlers(mqtt_service, storage, simulation_service)

    run_simulation(
        simulation_service=simulation_service,
        mqtt_service=mqtt_service,
        storage=storage,
        interval=config.UPDATE_INTERVAL,
    )


if __name__ == "__main__":
    main()
