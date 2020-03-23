import os
import sys
import json
import inspect
import threading
import logging
import logging.config

import structlog

from structlog._frames import _find_first_app_frame_and_name
from structlog.processors import JSONRenderer


def stringify_dict_keys(obj):
    if isinstance(obj, list):
        obj = [stringify_dict_keys(item) for item in obj]
    elif isinstance(obj, tuple):
        obj = tuple(stringify_dict_keys(item) for item in obj)
    elif isinstance(obj, dict):
        obj = {str(key): stringify_dict_keys(value) for key, value in obj.items()}
    return obj


def add_thread_info(logger, method_name, event_dict):  # pylint: disable=unused-argument
    thread = threading.current_thread()
    event_dict["__thread_id"] = thread.ident
    event_dict["__thread_name"] = thread.name
    return event_dict


def add_caller_info(logger, _, event_dict):
    f, name = _find_first_app_frame_and_name(additional_ignores=["logging", __name__])
    if not f:
        return event_dict
    frameinfo = inspect.getframeinfo(f)
    if not frameinfo:
        return event_dict
    module = inspect.getmodule(f)
    if not module:
        return event_dict
    if frameinfo and module:
        event_dict["__module"] = module.__name__
        event_dict["__lineno"] = frameinfo.lineno
        event_dict["__func"] = f.f_code.co_name
    return event_dict


def datlog(
    *,
    level=logging.DEBUG,
    capture_warnings=True,
    redirect_print=False,
    tty=None,
    user_config=None,
    json_renderer=None,
    hook_thread=True,
    hook_process=True
):
    """Setup struct logging.

    :param tty: if `False` the log will appear in json format
    :param level: the root logger level
    :param redirect_print: hijacks stdout/err
    :param capture_warnings: capture warnings
    :param user_config: merge user config with default log config
    :param json_renderer: a custom json renderer
    """
    if json_renderer is None:
        json_renderer = JSONRenderer(
            serializer=lambda obj, **kwargs: json.dumps(
                stringify_dict_keys(obj), **kwargs
            )
        )
    if tty is None:
        tty = sys.stdout.isatty()
    renderer = structlog.dev.ConsoleRenderer() if tty else json_renderer
    timestamper = structlog.processors.TimeStamper(fmt="ISO", utc=True)
    pre_chain = [
        # XXX log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.format_exc_info,
        timestamper,
        add_os_pid,
    ]

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": renderer,
                "foreign_pre_chain": pre_chain,
            }
        },
        "handlers": {
            "default": {"class": "logging.StreamHandler", "formatter": "structured"}
        },
        "loggers": {"": {"handlers": ["default"], "level": level, "propagate": True}},
    }

    if user_config:
        merge_dict(config, user_config)

    logging.config.dictConfig(config)

    logging.captureWarnings(capture_warnings)
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        add_os_pid,
        add_caller_info,
        add_thread_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    if redirect_print:
        # redirect stdio print
        print_log = structlog.get_logger("print")
        sys.stderr = StdioToLog(print_log)
        sys.stdout = StdioToLog(print_log)

    # log uncaught exceptions
    sys.excepthook = uncaught_exception
    if hook_thread:
        install_thread_excepthook()
    if hook_process:
        install_process_excepthook()
    logger = structlog.get_logger()
    return logger


class StdioToLog:
    """Delegate sys.stdout to a logger."""

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):  # noqa
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):  # noqa
        pass


def add_os_pid(logger, method_name, event_dict):  # noqa
    """Add the logger name to the event dict."""
    # XXX if we run ProcessPoolExecutor we at least need the right pid
    event_dict["__pid"] = os.getpid()
    return event_dict


def uncaught_exception(ex_type, ex_value, tb):  # noqa: C0103
    log_ = structlog.get_logger("sys.excepthook")
    log_.critical(event="uncaught exception", exc_info=(ex_type, ex_value, tb))


def merge_dict(dest, source):
    """Merge `source` into `dest`.

    `dest` is altered in place.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = dest.setdefault(key, {})
            merge_dict(node, value)
        else:
            dest[key] = value
    return dest


def install_thread_excepthook():
    """
    Patch run method so we can get exception message also in sys.excepthook

    This is only need in python < 3.8 in 3.8 use:

    https://docs.python.org/3.8/library/threading.html#threading.excepthook
    """
    import threading
    import sys

    run_orig = threading.Thread.run

    def run(*args, **kwargs):
        try:
            run_orig(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            sys.excepthook(*sys.exc_info())

    threading.Thread.run = run


def install_process_excepthook():
    """
    Patch run method so we can get exception message also in sys.excepthook

    """
    import multiprocessing
    import sys

    run_orig = multiprocessing.Process.run

    def run(*args, **kwargs):
        try:
            run_orig(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            sys.excepthook(*sys.exc_info())

    multiprocessing.Process.run = run
