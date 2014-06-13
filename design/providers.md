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

In the new design, we introduce several objects:

### The provider

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
a previous call to `getTitlesVersions()`, and return a tuple of the file name 
that was downloaded from the servers and the buffer (Bytes) itself that is 
the downloaded zip/srt file. It's not the provider's responsibility to deploy
the subtitle. 

With that said, if the there might be providers that will need to 
perform some logic in this phase, because the archive files that will get 
downloaded might contain several subtitles for several versions. In such cases,
the provider will need to perform the action of extracting the right subtitle
from the archive and returning it as the buffer (or putting it in another 
archive).

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

### The requests manager

The managing process will be performed internally in the manager. The providers
will no be aware to the manager logic. This means that the manager will expose
a function to which the provider will send request, and from which it will
receive the response. The function call will be a blocking call, and will not
return until the request was actually sent to the server, and the response got
back.

The manager's function will much like the PerformRequest that is used in the
current version of SubiT.

In order to allow only a single session against some server, the manager will
use a mutex that will get locked when `performRequest()` is called. Each 
instance of the manager will have a different mutex, thus, they will not block
each other. 

With that said, there might be cases where we will not want to wait in the line
for our request to be processed (When we decide to download some version for 
example). Therefore, the manager will expose another function `performRequestNext()` 
that will put the request at the first place in the queue, and thus, making sure 
it will get processed next.

Because several instances of the same provider are guarantee to share the same
instance of the manager, their calls to `performRequest()` will block, thus, 
preserving the synchronous mode.

```python
class RequestsManager:
    def performRequest(domain, url, data, type, more_headers): pass
    def performRequestNext(domain, url, data, type, more_headers): pass
```

### Factories

We'll use factories both for creating provider instances and requests manager
instances.

#### The requests manager factory

The factory for the requests manager will receive a string that identify the 
provider (The provider name), and will return an instance of RequestManager.

The algorithm for the factory will be:

- Prior to usage, allocate an empty dictionary named `D`
- On each call to the factory 
    - Name the provider name `PN`
    - Search for the key `PN` in `D`
    - If found
        + Return the value in `D`
    - Otherwise
        + Create new instance of RequestManager as `R`
        + Store it under the key `PN` in `D`
        + return `R`


The factory will be implemented as a classmethod inside the RequestsManager. 

**The factory method look like this:**
```python
class RequestsManager:
    @classmethod
    def getInstance(provider_name): pass
```

#### The providers factory

The provider factory will be implemented as a function within the providers 
package, and will receive up to three arguments:

**provider_name:** The name of the provider as it appears in the provider's 
class.

**languages (optional):** List of string that specify the languages that the
provider will use. If omitted, the function will use the languages specified 
in SubiT's configuration.

**requests_manager_factory (optional):** The factory function of the requests
manager. We allow passing of the function in order for us to be able to bypass
the default manager (for testing). If omitted, the function will use SubiT's
default manager factory.

```python
def getSubtitlesProviderInstance(
    provider_name, 
    languages = None, 
    requests_manager_factory = None): pass
```

### The Main provider instance

This instance will sum up interaction with the providers into a single point. 

Different instance of this provider will be stored within each Input that is
created in SubiT.

This provider will use the providers in parallel, thus, saving a lot of time.
In order to do so, it will use the multiprocessing module of python. The module
offers the `dummy` process pool that is actually a thread pool that exposes all
the parallel algorithm of the multiprocessing module.

It will implement the `ISubtitleProvider` interface as followed:

###### `__init__()`
Upon initialization, it will retrieve a single instance of every provider by 
using the providers factory. The languages for the providers will be loaded 
from the configuration.

###### `getTitlesVersions()`
This is where we need to perform some work. 

Unite all the version coming from the same title from different providers under
a single Title instance.

In order to perform this, we'll use the following algorithm:

- Create a new empty list of **TitleVersion**, `TV`
- Call `getTitlesVersions()` of each provider using the multiprocessing's map
    function, and name the result `ATV`
- For each `PTV` in `ATV`
    + For each Title `T` in `PTV`
        * If `T` is in `TV`
            * Add the versions associated with the title to the appropriate 
                TitleVersion
        * Otherwise
            * Add `T` to `TV`
- Return `TV`

###### `downloadSubtitleBuffer()`
The function will use the provider instance stored within the version passed
to the function, and call its `downloadSubtitleBuffer()`.

###### `getSuppotedLanguages()`
The function will collect all the supported languages from the providers, and 
return a list contains all of them.