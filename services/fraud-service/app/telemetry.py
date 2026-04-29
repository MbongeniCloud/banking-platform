import os
from fastapi import FastAPI
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.fastapi.fastapi_middleware import FastAPIMiddleware
import logging

def setup_telemetry(app: FastAPI):
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        return

    try:
        app.add_middleware(
            FastAPIMiddleware,
            exporter=AzureExporter(connection_string=connection_string),
            sampler=ProbabilitySampler(1.0),
        )

        logger = logging.getLogger("fraud-service")
        logger.addHandler(AzureLogHandler(connection_string=connection_string))
        logger.setLevel(logging.INFO)

    except ImportError:
        return