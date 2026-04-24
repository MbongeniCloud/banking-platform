import os
from azure.cosmos.aio import CosmosClient

ENDPOINT = os.getenv("COSMOS_ENDPOINT")
KEY = os.getenv("COSMOS_KEY")
DATABASE = os.getenv("COSMOS_DATABASE", "banking")
CONTAINER = os.getenv("COSMOS_CONTAINER", "transactions")

client = None
container_client = None

async def init_db():
    global client, container_client
    client = CosmosClient(ENDPOINT, credential=KEY)
    database = client.get_database_client(DATABASE)
    container_client = database.get_container_client(CONTAINER)

async def get_container():
    return container_client