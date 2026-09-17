import json
import os
import time
from datetime import datetime

from kafka import KafkaConsumer

import database


def _kafka_env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value if value else default


def _wait_for_db(max_attempts: int = 30) -> None:
    for _ in range(max_attempts):
        if database.check_connection():
            return
        time.sleep(1)
    raise RuntimeError("Database is unavailable for Kafka consumer")


def _build_consumer(max_attempts: int = 30) -> KafkaConsumer:
    topic = _kafka_env("KAFKA_TOPIC", "predictions")
    bootstrap_servers = _kafka_env("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    group_id = _kafka_env("KAFKA_GROUP_ID", "prediction-consumer")

    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            )
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1)

    raise RuntimeError("Kafka is unavailable for consumer") from last_error


def run_consumer() -> None:
    _wait_for_db()
    consumer = _build_consumer()

    for message in consumer:
        payload = message.value
        request_data = payload.get("request_data", {})
        prediction = payload.get("prediction")
        raw_timestamp = payload.get("timestamp")

        if prediction is None:
            continue

        parsed_timestamp = None
        if isinstance(raw_timestamp, str):
            try:
                parsed_timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            except ValueError:
                parsed_timestamp = None

        try:
            database.save_prediction(request_data, prediction, parsed_timestamp)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to persist Kafka message: {exc}")


if __name__ == "__main__":
    run_consumer()
