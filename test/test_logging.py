import unittest
import dummy_call
import json
import pytest
from logma.wech import datlog


class TestLogging(unittest.TestCase):
    def test_logging_notty(self):
        logger = datlog(tty=False)
        logger.info("This is a info log")
        logger.debug({"some": 123, "more": [1, 2, 3, 4]})
        logger.error("This is a error log")
        logger.debug("This is a debug log")
        try:
            raise Exception("Fooo exception")
        except Exception as e:
            logger.exception(e)
        captured = self.capfd.readouterr()
        event = [json.loads(x.strip()) for x in captured.err.split("\n") if x.strip()]
        self.assertEqual(len(event), 5)
        self.assertEqual(event[0]["event"], "This is a info log")
        self.assertTrue("Fooo exception" in event[-1]["event"])

    def test_logging_tty(self):
        logger = datlog(tty=True)
        logger.info("This is a info log")
        logger.debug({"some": 123, "more": [1, 2, 3, 4]})
        logger.error("This is a error log")
        logger.debug("This is a debug log")
        try:
            raise Exception("Fooo exception")
        except Exception as e:
            logger.exception(e)
        captured = self.capfd.readouterr()
        event = [x.strip() for x in captured.err.split("\n") if x.strip()]
        self.assertEqual(len(event), 9)
        self.assertTrue("This is a info log" in event[0])
        self.assertTrue("[test_logging]" in event[0])
        self.assertTrue("Fooo exception" in event[-1])

    def test_logging_notty_user_config(self):
        # XXX add propagate=False to prevent double entries
        config = {
            "dummy_call": {"handlers": ["default"], "level": "INFO", "propagate": False}
        }
        logger = datlog(tty=False, user_config=config)
        logger.info("This is a info log")
        dummy_call.call()
        captured = self.capfd.readouterr()
        event = [json.loads(x.strip()) for x in captured.err.split("\n") if x.strip()]
        self.assertEqual(len(event), 3)
        self.assertEqual(
            [x["logger"] for x in event], ["test_logging", "dummy_call", "dummy_call"]
        )

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd
