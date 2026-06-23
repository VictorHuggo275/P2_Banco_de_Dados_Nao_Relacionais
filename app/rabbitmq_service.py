import json
import logging
import time
from threading import Thread
import pika

logger = logging.getLogger(__name__)


class RabbitMQService:
    def __init__(self, url: str, queue: str):
        self.url = url
        self.queue = queue

    def start_consumer(self):
        Thread(
            target=self._consume_forever,
            daemon=True,
            name="rabbitmq-consumer",
        ).start()

    def publish(self, pedido: dict):
        """Publish a minimal identification payload for the order."""
        connection = None

        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(self.url)
            )

            channel = connection.channel()

            channel.queue_declare(
                queue=self.queue,
                durable=True,
            )

            # FIX: send only the minimal info needed to identify the order,
            # not the full pedido object.
            payload = json.dumps(
                {
                    "evento": "PEDIDO_CRIADO",
                    "pedido_id": pedido["id"],
                },
                ensure_ascii=False,
            )

            channel.basic_publish(
                exchange="",
                routing_key=self.queue,
                body=payload,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )

        finally:
            if connection is not None and connection.is_open:
                connection.close()

    def _consume_forever(self):
        while True:
            connection = None

            try:
                connection = pika.BlockingConnection(
                    pika.URLParameters(self.url)
                )

                channel = connection.channel()

                channel.queue_declare(
                    queue=self.queue,
                    durable=True,
                )

                channel.basic_qos(prefetch_count=1)

                def callback(ch, method, _properties, body):
                    payload = json.loads(body.decode("utf-8"))
                    logger.info(
                        "RabbitMQ mensagem recebida: %s",
                        json.dumps(payload, ensure_ascii=False),
                    )
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                channel.basic_consume(
                    queue=self.queue,
                    on_message_callback=callback,
                )

                channel.start_consuming()

            except pika.exceptions.AMQPConnectionError:
                logger.warning(
                    "RabbitMQ indisponível. Nova tentativa em 3 segundos."
                )

            except Exception:
                logger.exception(
                    "Erro inesperado no consumidor RabbitMQ."
                )

            finally:
                if connection is not None and connection.is_open:
                    connection.close()

            time.sleep(3)
