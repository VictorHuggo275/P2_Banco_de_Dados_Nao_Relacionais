from pydantic import BaseModel


class PedidoCreate(BaseModel):
    cliente: str
    produto: str
    quantidade: int


class Pedido(BaseModel):
    id: str
    cliente: str
    produto: str
    quantidade: int
    status: str
