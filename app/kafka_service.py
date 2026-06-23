import json
import logging
import time
from threading import Lock, Thread
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

logger = logging.getLogger(__name__)


class KafkaService:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self._producer = None
        self._lock = Lock()

    def start_consumer(self):
        Thread(
            target=self._consume_forever,
            daemon=True,
            name="kafka-consumer",
        ).start()

    def publish(self, pedido: dict):
        producer = self._get_producer()

        payload = {
            "evento": "PEDIDO_CRIADO",
            "pedido": pedido,
        }

        producer.send(self.topic, payload)
        producer.flush()

    def close(self):
        with self._lock:
            if self._producer:
                self._producer.close()
                self._producer = None

    def _get_producer(self):
        with self._lock:
            if self._producer:
                return self._producer

            while True:
                try:
                    self._producer = KafkaProducer(
                        bootstrap_servers=self.bootstrap_servers,
                        value_serializer=lambda value: json.dumps(value).encode(
                            "utf-8"
                        ),
                    )

                    return self._producer

                except NoBrokersAvailable:
                    logger.warning(
                        "Kafka indisponível. Tentando novamente em 3 segundos..."
                    )
                    time.sleep(3)

    def _consume_forever(self):
        while True:
            consumer = None

            try:
                consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers,
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id="pedidos-api",
                    value_deserializer=lambda value: json.loads(
                        value.decode("utf-8")
                    ),
                )

                for record in consumer:
                    payload = record.value
                    logger.info(
                        "Kafka mensagem recebida: %s",
                        json.dumps(payload, ensure_ascii=False),
                    )

            except NoBrokersAvailable:
                logger.warning(
                    "Kafka indisponível para consumo. Nova tentativa em 3 segundos."
                )

            except Exception:
                logger.exception("Erro inesperado no consumidor Kafka.")

            finally:
                if consumer:
                    consumer.close()

            time.sleep(3)
