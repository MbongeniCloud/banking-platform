import os
from fastapi import FastAPI
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.fastapi.fastapi_middleware import FastAPIMiddleware
from opencensus.trace.samplers import ProbabilitySampler

def setup_telemetry(app: FastAPI):
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        return
    app.add_middleware(
        FastAPIMiddleware,
        exporter=AzureExporter(connection_string=connection_string),
        sampler=ProbabilitySampler(1.0)
    )