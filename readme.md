# legendary-goggles
legendary-goggles is a repository that is configured as a message broker that is intended to simulate microservices during high traffic. It tries to mimmick the behavior of chatbots with its message-reply format. It utilizes Python with [RabbitMQ](https://www.rabbitmq.com/) as its message broker, [FastAPI](https://fastapi.tiangolo.com/) as its web framework for building APIs, [FastStream](https://faststream.airt.ai) connects the services to queue making it possible to interact with event streams, and [Docker](https://www.docker.com/) for scalability (here lies the diagram)

## Running
to run, first we need to clone this repository.
```shell
git clone https://github.com/fadhilrp/legendary-goggles.git
```
second, we need to build.
```shell
docker compose build
```
third, we need to compose
```shell
docker compose up
```
our microservice is up and running!

### How to send message
open postman
### How to simulate high traffic
### How to get database
### How to easily access endpoints
### How to add server instance
### How to produce errors
### How to check health
## Mission 1
## Mission 2
## Mission 3
## Mission 4
## Mission 5
### Generative AI Usage
### Postman/Endpoint Collection