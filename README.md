# API de Gerenciamento de Pedidos

## Descrição

Este projeto é uma API desenvolvida com FastAPI para gerenciamento de pedidos, utilizando MongoDB como banco de dados principal e integração com sistemas de mensageria assíncrona (Kafka e RabbitMQ).

Quando um novo pedido é criado, ele é armazenado no MongoDB, publicado como evento no Kafka e publicado como mensagem no RabbitMQ.

A aplicação também possui consumidores que escutam os brokers e armazenam as mensagens recebidas em memória.

## Tecnologias Utilizadas

Python 3.11, FastAPI, MongoDB, Kafka, RabbitMQ, Zookeeper, Docker, Docker Compose e Pytest.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

app/main.py: aplicação principal FastAPI responsável pelos endpoints de criação e listagem de pedidos.  
app/config.py: configurações da aplicação e variáveis de ambiente.  
app/database.py: conexão com o MongoDB.  
app/models.py: modelos de dados utilizando Pydantic.  
app/kafka_service.py: integração com Kafka (produção e consumo de eventos).  
app/rabbitmq_service.py: integração com RabbitMQ (produção e consumo de mensagens).  
tests/test_main.py: testes automatizados da API.

## Funcionalidades

### Criar Pedido (POST /pedidos)

Cria um novo pedido contendo id gerado automaticamente, cliente, produto, quantidade e status inicial PENDENTE.

Após a criação, o pedido é salvo no MongoDB, um evento é enviado para o Kafka e uma mensagem é enviada para o RabbitMQ.

### Listar Pedidos (GET /pedidos)

Retorna todos os pedidos armazenados no MongoDB.

## Formato do Pedido

{
  "id": "uuid-gerado",
  "cliente": "Nome do cliente",
  "produto": "Nome do produto",
  "quantidade": 1,
  "status": "PENDENTE"
}

## Mensageria

### Kafka

Tópico: pedidos-events

Formato do evento:

{
  "evento": "PEDIDO_CRIADO",
  "pedido": {
    "id": "...",
    "cliente": "...",
    "produto": "...",
    "quantidade": 1,
    "status": "PENDENTE"
  }
}

### RabbitMQ

Fila: pedidos-events

Formato da mensagem:

{
  "evento": "PEDIDO_CRIADO",
  "pedido": {
    "id": "...",
    "cliente": "...",
    "produto": "...",
    "quantidade": 1,
    "status": "PENDENTE"
  }
}

## Como Executar o Projeto

Pré-requisitos: Docker e Docker Compose instalados.

1. Clonar o repositório:
git clone <url-do-repositorio>
cd <nome-do-projeto>

2. Subir os containers:
docker-compose up --build

Este comando inicia a API FastAPI, MongoDB, Kafka, RabbitMQ e Zookeeper.

3. Acessar a aplicação:
API: http://localhost:8000  
Swagger: http://localhost:8000/docs

4. Testar endpoints:

Criar pedido:
POST http://localhost:8000/pedidos

Exemplo de corpo:
{
  "cliente": "João",
  "produto": "Notebook",
  "quantidade": 1
}

Listar pedidos:
GET http://localhost:8000/pedidos

## Como Executar os Testes

Executar:
pytest

Opcional com cobertura:
pytest --cov=app

## Variáveis de Ambiente

KAFKA_BOOTSTRAP_SERVERS: endereço do Kafka  
KAFKA_TOPIC: nome do tópico  
RABBITMQ_URL: URL do RabbitMQ  
RABBITMQ_QUEUE: nome da fila  
MONGODB_URL: URL do MongoDB  
MONGODB_DATABASE: nome do banco  
MONGODB_COLLECTION: nome da coleção  

## Arquitetura do Sistema

Fluxo da aplicação:

O cliente envia uma requisição para a API.  
A API gera um ID e define o status como PENDENTE.  
O pedido é salvo no MongoDB.  
Um evento é publicado no Kafka.  
Uma mensagem é publicada no RabbitMQ.  
Consumidores processam eventos em background e armazenam logs em memória.