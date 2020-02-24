# logma 

[![Build](https://github.com/peakiq/logma/workflows/logma/badge.svg)](https://github.com/peakiq/logma)
[![PyPI version fury.io](https://badge.fury.io/py/logma.svg)](https://pypi.python.org/pypi/logma/)

future place of great logging

# example

```
import logging

from logma.wech import datlog

# auto detects tty and outputs json or text accordingly
datlog()


log = logging.getLogger(__file__)

log.info("Hello")
log.warn("Hello")
log.error("Hello")
log.debug("Hello")
```
