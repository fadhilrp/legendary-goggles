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
thought process:
1. right now it could simulate the basic things, there should be edge cases where it would go wrong
2. generative AI should be good with accelerating the integration of error handling and logging, let's use it

explanation:
1. on every bit of script, identify errors
2. add error handling by sending logs to the identified errors

example output:
![example output mission 3a](https://github.com/fadhilrp/legendary-goggles/blob/main/img/example_out3a.png)
![example output mission 3b](https://github.com/fadhilrp/legendary-goggles/blob/main/img/example_out3b.png)
the output is the result of this function down here
```python
@app.get("/logs/{log_id}")
def read_log(log_id: int, session: SessionDep) -> Log:
    log = session.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
```

## Mission 4
thought process:
1. health checks should be based on the connection with the RabbitMQ, because the thing that's always alive is the message broker, and it's crucial to our services
2. there should be a lot of libraries out there that should provide placeholders for health checks, another way to accelerate development. but we should do it our own next time if given the chance, it could potentially be better.

explanation:
1. import fastapi_healthz
2. use placeholder to see how is the status of our services

example output:
![example output mission 4a](https://github.com/fadhilrp/legendary-goggles/blob/main/img/example_out4a.png)
![example output mission 4b](https://github.com/fadhilrp/legendary-goggles/blob/main/img/example_out4b.png)

## Mission 5
thought process:
1. as someone who would assess other's people work, it would be tedious if I need to install a lot of things to my environment locally.
2. as someone who is being assessed I would want to streamline that.
3. before I was experimenting on pure rpc messaging, I should add the norm of HTTP endpoints. I'd use FastAPI for quick deployments (Netflix also use FastAPI)
4. connecting FastAPI to RabbitMQ becomes easy with the integration of FastStreams, a trending integration library that helps accelerate integration between services
5. dockerize the application for easy deployment. docker allows us to easily create multiple identical instances of our application (containers) and distribute them across different servers. hence the portability of this microservice makes it easy to deploy and maintain.
6. for future use and references, the log should be saved into a proper database. SQLite.

explanation:
1. FastStreamer allows the router to seem instantaneously click with the fastapi app
2. making dockerfiles for client and server
3. support dockerfiles with docker-compose.yml because the rabbitmq should start first before the server (second) and the fastapi client (third)
4. integrate SQLite on client code, auto generating a database on-start, hence accessing logs is also a possibility

### Generative AI Usage
- dockerfile troubleshooting
- docker-compose generation
- error handling generation
- combination of legacy files into one or various files

### Dataset
A big thank you to Antrixsh Gupta on kaggle for uploading [Prompt Engineering and Responses Datas](https://www.kaggle.com/datasets/antrixsh/prompt-engineering-and-responses-dataset). This dataset is used for simulating the responses to the messages that are inserted into the queues.
