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