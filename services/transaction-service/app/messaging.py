import os
import json
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

CONNECTION_STRING = os.getenv("SERVICE_BUS_CONNECTION_STRING")
TOPIC = os.getenv("SERVICE_BUS_TRANSACTION_TOPIC", "transactions")

async def publish_transaction_event(transaction: dict):
    async with ServiceBusClient.from_connection_string(CONNECTION_STRING) as client:
        async with client.get_topic_sender(topic_name=TOPIC) as sender:
            message = ServiceBusMessage(json.dumps(transaction))
            await sender.send_messages(message)