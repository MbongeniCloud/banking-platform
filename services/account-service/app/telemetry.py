import os
from fastapi import FastAPI

def setup_telemetry(app: FastAPI):
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        return
    try:
        from opencensus.ext.azure.trace_exporter import AzureExporter
        from opencensus.trace.samplers import ProbabilitySampler
        from opencensus.trace.tracer import Tracer
    except ImportError:
        return