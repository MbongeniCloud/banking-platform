import os
import json
from azure.servicebus.aio import ServiceBusClient
from app.rules import evaluate

CONNECTION_STRING = os.getenv("SERVICE_BUS_CONNECTION_STRING")
TOPIC = os.getenv("SERVICE_BUS_TRANSACTION_TOPIC", "transactions")
SUBSCRIPTION = os.getenv("SERVICE_BUS_FRAUD_SUBSCRIPTION", "fraud-detection")

async def start_subscriber():
    async with ServiceBusClient.from_connection_string(CONNECTION_STRING) as client:
        async with client.get_subscription_receiver(
            topic_name=TOPIC,
            subscription_name=SUBSCRIPTION
        ) as receiver:
            async for message in receiver:
                try:
                    transaction = json.loads(str(message))
                    result = evaluate(transaction)
                    if result["is_flagged"]:
                        print(f"FRAUD ALERT: {result}")
                    await receiver.complete_message(message)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await receiver.abandon_message(message)