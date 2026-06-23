from dataclasses import dataclass
import os

@dataclass(slots=True)
class Settings:
    kafka_bootstrap_servers: str
    kafka_topic: str

    rabbitmq_url: str
    rabbitmq_queue: str

    mongodb_url: str
    mongodb_database: str
    mongodb_collection: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            kafka_bootstrap_servers=os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS", "localhost:9094"
            ),
            kafka_topic=os.getenv(
                "KAFKA_TOPIC", "pedidos-events"
            ),
            rabbitmq_url=os.getenv(
                "RABBITMQ_URL",
                "amqp://guest:guest@localhost:5672/%2F",
            ),
            rabbitmq_queue=os.getenv(
                "RABBITMQ_QUEUE",
                "pedidos-events",
            ),
            mongodb_url=os.getenv(
                "MONGODB_URL",
                "mongodb://localhost:27017",
            ),
            mongodb_database=os.getenv(
                "MONGODB_DATABASE",
                "ecommerce",
            ),
            mongodb_collection=os.getenv(
                "MONGODB_COLLECTION",
                "pedidos",
            ),
        )
