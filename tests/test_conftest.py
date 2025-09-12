import sys
import types
import pytest

@pytest.fixture(autouse=True, scope="session")
def mock_powertools():
    """Mock aws_lambda_powertools so tests run without AWS dependencies."""

    # Create fake modules
    fake_powertools = types.ModuleType("aws_lambda_powertools")
    fake_logger = types.ModuleType("aws_lambda_powertools.logging")
    fake_tracing = types.ModuleType("aws_lambda_powertools.tracing")
    fake_metrics = types.ModuleType("aws_lambda_powertools.metrics")

    # Fake Logger
    class Logger:
        def __init__(self, *args, **kwargs): pass
        def info(self, msg): print(f"[MOCK LOGGER] {msg}")
        def error(self, msg): print(f"[MOCK LOGGER] ERROR: {msg}")
        def exception(self, msg): print(f"[MOCK LOGGER] EXC: {msg}")

        def inject_lambda_context(self, func=None, **kwargs):
            def wrapper(event, context):
                return func(event, context)
            return wrapper

    # Fake Tracer
    class Tracer:
        def __init__(self, *args, **kwargs): pass
        def capture_lambda_handler(self, func=None, **kwargs):
            def wrapper(event, context):
                return func(event, context)
            return wrapper

    # Fake Metrics
    class Metrics:
        def __init__(self, *args, **kwargs): pass
        def add_metric(self, *args, **kwargs): pass

    # Attach fakes
    fake_logger.Logger = Logger
    fake_tracing.Tracer = Tracer
    fake_metrics.Metrics = Metrics
    fake_metrics.MetricUnit = type("MetricUnit", (), {"Count": "Count"})

    # Register in sys.modules
    sys.modules["aws_lambda_powertools"] = fake_powertools
    sys.modules["aws_lambda_powertools.logging"] = fake_logger
    sys.modules["aws_lambda_powertools.tracing"] = fake_tracing
    sys.modules["aws_lambda_powertools.metrics"] = fake_metrics

    yield
    # cleanup not required since pytest session fixture
