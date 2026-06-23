import logging
import uuid
from fastapi import FastAPI
from app.config import Settings
from app.database import pedidos_collection
from app.kafka_service import KafkaService
from app.models import PedidoCreate
from app.rabbitmq_service import RabbitMQService

logging.basicConfig(level=logging.INFO)

settings = Settings.from_env()

kafka_service = KafkaService(
    settings.kafka_bootstrap_servers,
    settings.kafka_topic,
)

rabbitmq_service = RabbitMQService(
    settings.rabbitmq_url,
    settings.rabbitmq_queue,
)

app = FastAPI(
    title="API de Gerenciamento de Pedidos",
    version="1.0.0",
)


@app.on_event("startup")
def startup() -> None:
    kafka_service.start_consumer()
    rabbitmq_service.start_consumer()


@app.on_event("shutdown")
def shutdown() -> None:
    kafka_service.close()


@app.get("/")
def root():
    return {
        "mensagem": "API de Pedidos",
        "rotas": [
            "POST /pedidos",
            "GET /pedidos",
        ],
    }


@app.post("/pedidos")
def criar_pedido(payload: PedidoCreate):
    pedido = {
        "id": str(uuid.uuid4()),
        "cliente": payload.cliente,
        "produto": payload.produto,
        "quantidade": payload.quantidade,
        "status": "PENDENTE",
    }

    pedidos_collection.insert_one(pedido)

    kafka_service.publish(pedido)

    rabbitmq_service.publish(pedido)

    return pedido


@app.get("/pedidos")
def listar_pedidos():
    pedidos = list(
        pedidos_collection.find(
            {},
            {
                "_id": 0,
            },
        )
    )

    return pedidos
