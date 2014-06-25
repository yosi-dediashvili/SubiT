# SubiT's logging design

## Goals

When it comes to logging, we have several goals in SubiT:

1. An API user will be able to receive API logs.
2. The API will not expose a logging mechanism of its own as part of its API 
services.
3. The API will only be dependent on external or built-in libraries. This means
that it cannot use, for example, a logging mechanism that is implemented as part
of the whole SubiT program.
4. From outside the API, we want to be able to receive a portion of the logs 
from the API, for example, receive only logs from the providers module, etc.
5. Receive logs no only to the console but also to:
    - File
    - Callback function

## Implementation

In order to fulfill the goals, we'll use python's built-in logging module.

### Usage of the logging module

Any logger instance inside SubiT (including the API), will use the basic logging
channel named 'subit'.

#### SubiT's API

The API will use the logging module directly, and its root channel will be named
`subit.api`. Each module inside the API will have its own logging "Channel" 
inside the logging module.

Each module will set its channel name such that it contains the names of all
its parents, with a dot between each one. So for example, the channel name for 
the providers module will be `subit.api.providers`, and a specific provider 
inside the provider module will have its short name (in the case of www.torec.net 
for example) `subit.api.providers.torec`.

```python
import logging
logger = logging.getLogger("subit.api.providers")
logger.info("Info message from the providers module.")
```

#### The rest of SubiT

The rest of SubiT's modules will write their log to the `subit.rest` channel.

```python
import logging
logger = logging.getLogger("subit.rest")
logger.info("Info message from the SubiT program.")
```
#### Log levels

We'll use three log levels in SubiT: `DEBUG`, `INFO` and `ERROR`. 

##### Level selection

We'll allow the user to select both the logging level and the channels, such 
that from one side, he will be able to receive only `ERROR` logs from the `rest`
or the `api` channels, and from the other side, he will be able to receive the
`DEBUG` logs from all the channels.

### Interpreting the messages

In order for us to receive the logs from the logger, we'll implement an handler
for the logging, and register it at SubiT's startup.

We'll have three types of handlers:

* Writes to the log window in GUI mode
* Writes to the console
* Writes to file

Those handlers will be registered under the root logger channel `subit` by 
calling the `addHandler` method of the logger, and therefor, will receive all 
the logs.


## Usage

### Receiving logs from the API

The examples uses the logging default handler (the console). First, we retrieve
the logger, and only after we aquire it, we create an instance of API, otherwise
we might miss log records.

```python
from api import SubiTAPI
import logging
# Get the logger for the API.
logger = logging.getLogger("subit.api")
# Receive debug messages also.
logger.setLevel(logging.DEBUG)
# Create an instance of the API
subit_api = SubiTAPI()
```

