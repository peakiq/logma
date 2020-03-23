import json
import pytest


@pytest.fixture
def dummy_call():
    import structlog

    logger = structlog.get_logger("dummy_call")

    def call():
        logger.info("This info call")
        logger.debug("This hidden debug call")
        logger.info("This is another info call")

    return call


@pytest.fixture
def delete_ansi_escape():
    import re
    import functools

    # 7-bit C1 ANSI sequences
    ansi_escape = re.compile(
        r"""
        \x1B    # ESC
        [@-_]   # 7-bit C1 Fe
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    """,
        re.VERBOSE,
    )
    return functools.partial(ansi_escape.sub, "")


def test_logging_notty(capfd):
    from logma.wech import datlog

    logger = datlog(tty=False)
    logger.info("This is a info log")
    logger.debug({"some": 123, "more": [1, 2, 3, 4]})
    logger.error("This is a error log")
    logger.debug("This is a debug log")
    try:
        raise Exception("Fooo exception")
    except Exception as e:
        logger.exception(e)
    captured = capfd.readouterr()
    event = [json.loads(x.strip()) for x in captured.err.split("\n") if x.strip()]
    assert len(event) == 5
    assert event[0]["event"] == "This is a info log"
    assert "Fooo exception" in event[-1]["event"]


def test_logging_tty(capfd, delete_ansi_escape):
    from logma.wech import datlog

    logger = datlog(tty=True)
    logger.info("This is a info log")
    logger.debug({"some": 123, "more": [1, 2, 3, 4]})
    logger.error("This is a error log")
    logger.debug("This is a debug log")
    try:
        raise Exception("Fooo exception")
    except Exception as e:
        logger.exception(e)
    captured = capfd.readouterr()
    event = [x.strip() for x in captured.err.split("\n") if x.strip()]
    assert len(event) == 9
    assert "This is a info log" in event[0]
    assert "[test_logging]" in delete_ansi_escape(event[0])
    assert "Fooo exception" in event[-1]


def test_logging_notty_user_config(capfd, dummy_call):
    from logma.wech import datlog

    # XXX add propagate=False to prevent double entries
    config = {
        "loggers": {
            "dummy_call": {"handlers": ["default"], "level": "INFO", "propagate": False}
        }
    }
    logger = datlog(tty=False, user_config=config)
    logger.info("This is a info log")
    dummy_call()
    captured = capfd.readouterr()
    event = [json.loads(x.strip()) for x in captured.err.split("\n") if x.strip()]
    assert len(event) == 3
    assert [x["logger"] for x in event] == ["test_logging", "dummy_call", "dummy_call"]


def test_process_and_thread_unhandled_exception(capfd):
    from logma.wech import datlog

    logger = datlog(tty=False)
    import multiprocessing
    import threading

    def dummy_func(name):
        raise Exception("Exception from %s" % name)

    proc = multiprocessing.Process(target=dummy_func, args=("Process",))
    proc.start()
    proc.join()
    th = threading.Thread(target=dummy_func, args=("Thread",))
    th.start()
    th.join()

    # logger.info("This is from Main")
    logger.info("This is from Main")

    captured = capfd.readouterr()
    event = [json.loads(x.strip()) for x in captured.err.split("\n") if x.strip()]

    assert len(event) == 3
    exc = [x["exception"] for x in event if x["logger"] == "sys.excepthook"]
    assert len(exc) == 2
