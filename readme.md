# legendary-goggles
legendary-goggles is a repository that is configured as a message broker that is intended to simulate microservices during high traffic. It tries to mimmick the behavior of chatbots with its message-reply format. It utilizes Python with [RabbitMQ](https://www.rabbitmq.com/) as its message broker, [FastAPI](https://fastapi.tiangolo.com/) as its web framework for building APIs, [FastStream](https://faststream.airt.ai) connects the services to queue making it possible to interact with event streams, and [Docker](https://www.docker.com/) for scalability. Oh, and [SQLite](https://www.sqlite.org/) as our database.
![System Diagram](https://github.com/fadhilrp/legendary-goggles/blob/main/img/legendary-goggles.png)

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

### How to send a message
sending a message and getting back a reply is the backbone of our system, here's how you do it.
#### FastAPI Docs
```http request
localhost:8080/docs
```
after successfully serving the microservice without errors, this endpoint should be available for you to access. here you could easily select the endpoints you want to use. for our case, select `/prompt` and try entering your message as a string as the key to the `m` your message. if successful, your message should pop. if the service said it doesn't know how to answer your message, try sending a message from the dataset inside `components`, (e.g. "Where do you see yourself in 5 years?").
#### Postman
you could import the postman collection that is included inside this repository. you could then select the one that says `http://localhost:8000/prompt` and bombs away.

### How to simulate high traffic
to simulate high traffic you should run `simu.py` inside `src/api` the script would then try to send all the available prompts that are inside our dataset.
```python
python3 simu.py
```

### How to get database
to get the database, you would need to be inside our lovely container. to do that we could run,
```shell
docker exec -it <container id> /bin/bash
```
then copying the database file by running,
```shell
docker cp <container id>:/legendary-goggles/database.db .
```

### How to add server instance
to add a server instance we could do that from adding a server instance inside the `docker-compose.yml`
```dockerfile
  rpc_server2:
    build:
      context: .
      dockerfile: Dockerfile.server
    environment:
      - RABBITMQ_HOST=rabbitmq
      - SERVER_NAME=server2
      - QUEUE_NAME=rpc_queue2
    depends_on:
      rabbitmq:
        condition: service_healthy
      rpc_server1:
        condition: service_started
```
increment the numbers (e.g. 2 to 3) it should be good to go.

### How to check health
to check the health of our service we could use 
#### FastAPI Docs
selecting the `/health` endpoint should give the health of our current connection with RabbitMQ.
#### Postman
you could select the one that says `http://localhost:8000/health` and bombs away.

### How to see & delete logs
#### FastAPI Docs
- to see all logs
selecting the `GET /logs/` endpoint should show all of our current logs.
- to see a specific log
selecting the `GET /logs/{logs_id}` endpoint should show the log you are currently looking for.
- to delete a specific log
selecting the `DELETE /logs/{logs_id}` endpoint deletes the log you want to delete.
#### Postman
same endpoints apply to the functions.

## Mission 1
thought process:
1. since there are only four days left, despite its performance cutbacks python's general purpose helps speeds up development
2. again with the general purpose, RabbitMQ should do the job where if a system simply needs to notify another part of the system to start to work on a task.
3. get a dataset worth of prompts so it would simulate the real world scenario of chatbots.

explanation:
1. establish a simple pub/sub pipeline
2. read the dataset, take the prompt as the input
3. send all prompts to the subscriber through the publisher
4. make sure the subscriber gets all of the message

example output:
![example output mission 1](https://github.com/fadhilrp/legendary-goggles/blob/main/img/example_out1.png)
 
## Mission 2
thought process:
1. the subscriber should then reply after receiving the message
2. one thing to do that is through a rpc server because it has a `reply_to` function
3. use the responses from the dataset for the replies to the received messages

explanation:
1. convert both pub/sub to a rpc client and server.
2. use the dataset to match the received message with the answer.
3. make a placeholder to receive the answer.
4. make sure the answer is received.
5. add a condition if there are no matched answers in the dataset based on the message

example output:
![example output mission 2](https://github.com/fadhilrp/legendary-goggles/blob/main/img/example_out2.png)

## Mission 3
sample log outputs
## Mission 4
health stuff
## Mission 5
thought process and enhancements

### Generative AI Usage
- dockerfile troubleshooting
- docker-compose generation
- error handling generation
- combination of legacy files

### Dataset
A big thank you to Antrixsh Gupta on kaggle for uploading [Prompt Engineering and Responses Datas](https://www.kaggle.com/datasets/antrixsh/prompt-engineering-and-responses-dataset). This dataset is used for simulating the responses to the messages that are inserted into the queues.
