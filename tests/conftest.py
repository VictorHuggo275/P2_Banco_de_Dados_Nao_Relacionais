from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    """
    Build a TestClient with every external dependency mocked out:
      - pymongo.MongoClient  → in-memory list-backed fake collection
      - KafkaService.publish / start_consumer → no-ops
      - RabbitMQService.publish / start_consumer → no-ops
    """

    _store: list[dict] = []

    fake_collection = MagicMock()
    fake_collection.insert_one.side_effect = lambda doc: _store.append(doc)
    fake_collection.find.side_effect = lambda filt, proj: iter(
        [{k: v for k, v in d.items() if k != "_id"} for d in _store]
    )

    with (
        patch("app.database.MongoClient") as mock_mongo,
        patch("app.kafka_service.KafkaService.publish", return_value=None),
        patch("app.kafka_service.KafkaService.start_consumer", return_value=None),
        patch("app.rabbitmq_service.RabbitMQService.publish", return_value=None),
        patch("app.rabbitmq_service.RabbitMQService.start_consumer", return_value=None),
    ):

        mock_mongo.return_value.__getitem__.return_value.__getitem__.return_value = (
            fake_collection
        )

        import importlib
        import app.database as db_module

        db_module.pedidos_collection = fake_collection

        from app.main import app

        yield TestClient(app)
