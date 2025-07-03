import logging
import json
import os
import sys
import traceback
import inspect
from functools import wraps
from typing import Callable, Any


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # Basic JSON structure
        json_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName
        }

        # Add extra user-defined fields
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord("", "", "", 0, "", (), None).__dict__:
                json_record[key] = value

        return json.dumps(json_record)


def get_json_logger(name="employee_search_json_logger") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def log_json_exceptions(func: Callable) -> Callable:
    logger = get_json_logger()

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error("Exception occurred", extra={
                "exception": str(e),
                "function": func.__name__,
                "traceback": traceback.format_exc()
            })
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("Exception occurred", extra={
                "exception": str(e),
                "function": func.__name__,
                "traceback": traceback.format_exc()
            })
            raise

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
