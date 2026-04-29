import os
import logging
from fastapi import FastAPI
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

def setup_telemetry(app: FastAPI):
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        return

    try:
        exporter = AzureExporter(connection_string=connection_string)
        sampler = ProbabilitySampler(1.0)

        logger = logging.getLogger("account-service")
        logger.addHandler(AzureLogHandler(connection_string=connection_string))
        logger.setLevel(logging.INFO)

        @app.middleware("http")
        async def trace_requests(request, call_next):
            tracer = Tracer(exporter=exporter, sampler=sampler)
            with tracer.span(name=str(request.url.path)):
                response = await call_next(request)
                return response

    except Exception:
        return