# SubiT's providers design

As mentioned in the processing design, the current providers structure needs to 
be changed.

## The current state

There are two problems with the current design:

1. We're assuming that at any given time, only a single input is being 
processed - This lead us to the state were the providers are simply classes with
static methods, that stored static state within it.

2. Our processing logic used the providers directly. This lead to complicated 
code lines that was needed in order to receive results from the providers in 
the processing code. 

## The new design

In the new design, we introduce two objects:

### 1. The provider

The provider is responsible to retrieve versions list and to download a version
from some subtitles site source.

Unlike the old design, the in the new design, a single provider instance will
be responsible for retrieving results for all the languages that are supported
by him. This will be maintained using the following structure:

1. SubiT will have a single place that defines all the languages that it 
supports.
2. Each provider will store a list within it specifying the languages (from 1)
that it supports.

#### The interface

The new provider interface will introduce the following changes:

##### 1. No intermediate function - from the input we will get versions, not movies.
The old design, were we had a method for retrieving the movies, and another one
for retrieving the version, proved to be causing more problems than solving.

By using a single function, we can use much simpler selection mechanism, that 
has all the information it needs right away, and does not need to select movies
based on guessing some times.

##### 2. The use of central requests manager.

The request manager is responsible for making sure that at any given time, there
is only a single request that waits for response from the server for any 
provider. This means that there can be several request waiting for response, but
from different providers.

We use this mechanism in order to avoid sending to much requests at the same 
time to the servers.

* * *

##### The functions:

###### `__init__()`
Upon initialization, the provider receives an instance of requests_manager (The
object is discussed later in the document).

###### `getTitlesVersions()`
The function receive the new Input object, and returns a list of TitleVersions
object.

###### `downloadSubtitleBuffer()`
The function receive a single version from the versions that was retrieved with
a previous call to `getTitlesVersions()`, and return a buffer (Bytes) that is 
the downloaded zip/srt file. It's not the provider's responsibility to deploy
the subtitle.

###### `getSupportedLanguages()`
The function will return a list of string (where each item is a language).

**To sum up, this is the basic structure:**
```python
class ISubtitlesProvider:
    def __init__(self, requests_manager): pass
    def getTitlesVersions(self, input): pass
    def downloadSubtitleBuffer(self, provider_version): pass
    def getSupportedLanguages(self): pass
```

### 2. The requests manager

The managing process will be performed internally in the manager. The providers
will no be aware to the manager logic. This means that the manager will expose
a function to which the provider will send request, and from which it will
receive the response. The function call will be a blocking call, and will not
return until the request was actually sent to the server, and the response got
back.

The manager's function will much like the PerformRequest that is used in the
current version of SubiT.

There will be a different instance of the manager for each provider. Each 
manager instance will have a working thread that starts with it and fetches
requests from an internal queue. The queue will get populated by calls to 
`performRequest()`. 

Each request will be stored in an instance of an internal class that holds both
the request and the response. When the instance will be pushed to the queue, it
will have only the request instance. The `performRequest()` function will check
for the response instance, and once it is present, the response will be return 
to the caller.

```python
class RequestsManager:
    def performRequest(domain, url, data, type, more_headers): pass
```

### The Main provider instance

This instance will sum up interaction with the providers into a single point. 

Different instance of this provider will be stored within each Input that is
created in SubiT.

It will implement the `ISubtitleProvider` interface as followed:

###### `__init__()`
Upon initialization, it will retrieve a single instance of every provider. 
###### `getTitlesVersions()`
This is where we need to perform some work. 

Unite all the version coming from the same title from different providers under
a single Title instance.

In order to perform this, we'll use the following algorithm:

- Create a new empty list of **TitleVersion**, `TV`
- For each provider
    + Call the provider's `getTitlesVersions()` function, name the result `PTV`
    + For each Title `T` in `PTV`
        * If `T` is in `TV`
            * Add the versions associated with the title to the appropriate 
                TitleVersion
        * Otherwise
            * Add `T` to `TV`
- Return `TV`

###### `downloadSubtitleBuffer()`
The function will use the provider instance stored withing the version passed
to the function, and call its `downloadSubtitleBuffer()`.

###### `getSuppotedLanguages()`
The function will collect all the supported languages from the providers, and 
return a list contains all of them.