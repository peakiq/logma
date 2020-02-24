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
% cat logex.py 
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

Usage in the console (it uses colorama):

```
% python logex.py       
2020-02-24T22:48:27.779236Z [info     ] Hello                          [logex.py] pid=14144
2020-02-24T22:48:27.779403Z [warning  ] Hello                          [logex.py] pid=14144
2020-02-24T22:48:27.779489Z [error    ] Hello                          [logex.py] pid=14144
2020-02-24T22:48:27.779552Z [debug    ] Hello                          [logex.py] pid=14144
```

Usage in background (json output to stderr):

```
% python logex.py &> logex.log && cat logex.log
{"event": "Hello", "logger": "logex.py", "level": "info", "timestamp": "2020-02-24T22:49:51.656540Z", "pid": 14176}
{"event": "Hello", "logger": "logex.py", "level": "warning", "timestamp": "2020-02-24T22:49:51.656682Z", "pid": 14176}
{"event": "Hello", "logger": "logex.py", "level": "error", "timestamp": "2020-02-24T22:49:51.656754Z", "pid": 14176}
{"event": "Hello", "logger": "logex.py", "level": "debug", "timestamp": "2020-02-24T22:49:51.656815Z", "pid": 14176}
```
