#!/usr/bin/env python
import pika
from pika.exceptions import AMQPConnectionError
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Load dataset
    df = pd.read_csv('components/prompt_engineering_dataset.csv')
except FileNotFoundError as e:
    logging.error(f"Dataset file not found: {e}")
    exit(1)
except pd.errors.EmptyDataError as e:
    logging.error(f"Dataset file is empty: {e}")
    exit(1)
except Exception as e:
    logging.error(f"Error loading dataset: {e}")
    exit(1)

try:
    # Set up RabbitMQ connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', port=5672, socket_timeout=2))
    channel = connection.channel()
    channel.queue_declare(queue='rpc_queue')
except pika.exceptions.AMQPConnectionError as e:
    logging.error(f"Error connecting to RabbitMQ: {e}")
    exit(1)
except Exception as e:
    logging.error(f"Error setting up RabbitMQ: {e}")
    exit(1)


def res(m): #used chatgpt
    try:
        m = m.decode('utf-8')
        # Locate the row where 'Prompt' matches 'm'
        row = df[df['Prompt'] == m]
        # If a match is found, return the corresponding 'Response'
        if not row.empty:
            return row.iloc[0]['Response']
        return "No match found"
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return "Internal server error"


def on_request(ch, method, props, body):
    try:
        m = body #<-debugged with chatgpt
        logging.info(f" [.] message ({m})")
        response = res(m)
        logging.info(f" [.] response ({response})")
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(f"Error handling RPC request: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Optionally avoid requeuing on fatal error


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

logging.info(" [x] Awaiting RPC requests")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    logging.info("Gracefully shutting down...")
    connection.close()
except Exception as e:
    logging.error(f"Error during consuming messages: {e}")
    connection.close()
