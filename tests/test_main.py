def test_criar_pedido(client):
    resposta = client.post(
        "/pedidos",
        json={
            "cliente": "João",
            "produto": "Notebook",
            "quantidade": 2,
        },
    )

    assert resposta.status_code == 200
    dados = resposta.json()
    assert "id" in dados
    assert dados["cliente"] == "João"
    assert dados["produto"] == "Notebook"
    assert dados["quantidade"] == 2
    assert dados["status"] == "PENDENTE"


def test_listar_pedidos(client):
    resposta = client.get("/pedidos")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert isinstance(dados, list)
