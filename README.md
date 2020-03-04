# logma

[![Build](https://github.com/peakiq/logma/workflows/logma/badge.svg)](https://github.com/peakiq/logma)
[![PyPI version fury.io](https://badge.fury.io/py/logma.svg)](https://pypi.python.org/pypi/logma/)

Great default logging.

## Usage

Install:

```
% pip install logma
```

Example file:

```
% cat example/logex.py
from logma.wech import datlog
import structlog


# auto detects tty and outputs json or text accordingly
datlog()


log = structlog.get_logger("logex")


def main():
    log.info("Hello")
    log.warn("Hello")
    log.error("Hello")
    log.debug("Hello")


if __name__ == "__main__":
    main()
```

Usage in the console (it uses colorama):

```
% env/bin/python example/logex.py
2020-03-04T11:27:41.523012Z [info     ] Hello                          [logex] func=main lineno=13 module=__main__
2020-03-04T11:27:41.529786Z [warning  ] Hello                          [logex] func=main lineno=14 module=__main__
2020-03-04T11:27:41.529982Z [error    ] Hello                          [logex] func=main lineno=15 module=__main__
2020-03-04T11:27:41.530156Z [debug    ] Hello                          [logex] func=main lineno=16 module=__main__
```

Usage in background (json output to stderr):

```
% env/bin/python example/logex.py &> logex.log && cat logex.log
{"event": "Hello", "level": "info", "logger": "logex", "timestamp": "2020-03-04T11:28:17.565149Z", "module": "__main__", "lineno": 13, "func": "main"}
{"event": "Hello", "level": "warning", "logger": "logex", "timestamp": "2020-03-04T11:28:17.571626Z", "module": "__main__", "lineno": 14, "func": "main"}
{"event": "Hello", "level": "error", "logger": "logex", "timestamp": "2020-03-04T11:28:17.571821Z", "module": "__main__", "lineno": 15, "func": "main"}
{"event": "Hello", "level": "debug", "logger": "logex", "timestamp": "2020-03-04T11:28:17.571995Z", "module": "__main__", "lineno": 16, "func": "main"}
```
