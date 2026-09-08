import logging
import sys
import structlog
from contextvars import ContextVar
import ulid

# Context variable to hold request_id across async call chains
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def generate_request_id() -> str:
    return str(ulid.new())


def add_request_id(logger, method_name, event_dict):
    req_id = request_id_ctx.get()
    if req_id:
        event_dict["request_id"] = req_id
    return event_dict


def setup_logging(debug: bool = False):
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        add_request_id,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if debug:
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
    else:
        processors = shared_processors + [structlog.processors.JSONRenderer()]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
    )


def get_logger(name: str = "verifyd"):
    return structlog.get_logger(name)
