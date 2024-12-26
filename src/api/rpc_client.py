#!/usr/bin/env python
import pika
import uuid
import pandas as pd

class DatasetManager:
    def __init__(self, path='../../components/prompt_engineering_dataset.csv'):
        try:
            self.df = pd.read_csv(path)
            if 'Prompt' not in self.df.columns or 'Response' not in self.df.columns:
                raise ValueError("CSV file must contain 'Prompt' and 'Response' columns.")
        except FileNotFoundError:
            print("Error: The specified CSV file could not be found.")
            self.df = None
        except Exception as e:
            print(f"Error loading CSV: {e}")
            self.df = None

    def get_response(self, m):
        if self.df is None:
            return "Dataset unavailable."
        row = self.df[self.df['Prompt'] == m]
        return row.iloc[0]['Response'] if not row.empty else "No match found."

class MessageRpcClient(object):

    def __init__(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error: Unable to connect to RabbitMQ server: {e}")
            exit(1)

        try:
            self.channel = self.connection.channel()
        except pika.exceptions.ChannelError as e:
            print(f"Error: Failed to create a channel: {e}")
            self.connection.close()
            exit(1)

        try:
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.callback_queue = result.method.queue
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f"Error: Queue declaration failed: {e}")
            self.connection.close()
            exit(1)

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, m):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='rpc_queue',
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=str(m))
        except pika.exceptions.ChannelError as e:
            print(f"Error: Failed to publish message: {e}")
            return None

        try:
            while self.response is None:
                self.connection.process_data_events(time_limit=5)
        except pika.exceptions.AMQPError as e:
            print(f"Error: AMQP Error during data event processing: {e}")
            return None
        return str(self.response)


if __name__ == "__main__":
    # Initialize DatasetManager
    dataset_manager = DatasetManager('../../components/prompt_engineering_dataset.csv')

    if dataset_manager.df is None:
        print("Error: Dataset is not available. Exiting.")
        exit(1)

    # Create a MessageRpcClient instance
    message_rpc = MessageRpcClient()

    # Iterate through the dataset's 'Prompt' column
    for m in dataset_manager.df['Prompt']:
        print(f"Sending prompt: {prompt}")
        try:
            # Send prompt via RPC client
            response = message_rpc.call(prompt)
            if response is None:
                print(f"Error: No response received for prompt '{prompt}'")
            else:
                print(f" [x] Requesting response for '{prompt}'")
                print(f" [.] Got response: {response}")
        except Exception as e:
            print(f"Error: An unexpected error occurred for prompt '{prompt}': {e}")
