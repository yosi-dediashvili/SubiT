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
Upon initialization, the provider receives a list of Languages it should use, 
and an instance of requests_manager (The object is discussed later in the document).

The provider might not support all the languages it receives, but it will must
not use other languages than those.

###### `get_titles_versions()`
The function receive the new Input object, and returns a list of TitleVersions
object.

###### `download_subtitle_buffer()`
The function receive a single version from the versions that was retrieved with
a previous call to `get_titles_versions()`, and return a tuple of the file name 
that was downloaded from the servers and the buffer (Bytes) itself that is 
the downloaded zip/srt file. It's not the provider's responsibility to deploy
the subtitle. 

With that said, if the there might be providers that will need to 
perform some logic in this phase, because the archive files that will get 
downloaded might contain several subtitles for several versions. In such cases,
the provider will need to perform the action of extracting the right subtitle
from the archive and returning it as the buffer (or putting it in another 
archive).

###### `languages_in_use`

The function will be a property of instances, and return a list of Language items 
that specify for what languages this instance of the provider returns versions 
for (i.e., the languages it was initialized with).

###### `suppoert_languages`

A class attribute in each provider that returns a Language list that specify
the languages that the provider can support.

**To sum up, this is the basic structure:**
```python
class IProvider:
    supported_languages = []
    def __init__(self, languages, requests_manager): pass
    def get_titles_versions(self, input): pass
    def download_subtitle_buffer(self, provider_version): pass
    @property
    def languages_in_use(self): pass
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
use a mutex that will get locked when `perform_request()` is called. Each 
instance of the manager will have a different mutex, thus, they will not block
each other. 

With that said, there might be cases where we will not want to wait in the line
for our request to be processed (When we decide to download some version for 
example). Therefore, the manager will expose another function `perform_request_next()` 
that will put the request at the first place in the queue, and thus, making sure 
it will get processed next.

Because several instances of the same provider are guarantee to share the same
instance of the manager, their calls to `perform_request()` will block, thus, 
preserving the synchronous mode.

```python
class RequestsManager:
    def perform_request(domain, url, data, type, more_headers): pass
    def perform_request_next(domain, url, data, type, more_headers): pass
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
    def get_instance(provider_name): pass
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
def get_provider_instance(
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

It will implement the `IProvider` interface as followed:

###### `__init__()`
Upon initialization, it will retrieve a single instance of every provider by 
using the providers factory. The languages for the providers will be loaded 
from the configuration.

###### `get_titles_versions()`
This is where we need to perform some work. 

In here, we'll unite all the version coming from the same title from different 
providers under a single Title instance.

**The Title instance will be united using the following rules:**

- Given a list of Title instances named `TITLES` that share the same Title type 
and returns True in the equality check
- A new Title `T_` will be created (with the same type as `A` and `B`)
- Its `name` value will be set to the name that is shared between most of the 
titles in `TITLES`
- Its `normalized_names` list will contain all the normalized names appeared 
- Its `year` value will be set to the same year as the first title in `TITLES` that
has a year other than `0`, or `0` if no such title exists
- The same logic will be applied to the `imdb_id` value
- If the Title is SeriesTitle
    + The `episode_number` and `season_number` value will be determined by applying
    the same logic applied in `year`'s value
    + The `episode_name` will use the same logic as the `name`
    + The `episode_normalized_names` will use the same logic as the `normalized_names`

**The TitleVersion will be united using the following algorithm:**

- Create a new empty list of **TitleVersion**, `TV`
- Call `get_titles_versions()` of each provider using the multiprocessing's map
    function, and name the result `ATV`
- For each `PTV` in `ATV`
    + For each Title `T` in `PTV`
        * If `T` is in `TV`
            * Add the versions associated with the title to the appropriate 
                TitleVersion
            * Update the Title instance
        * Otherwise
            * Add `T` to `TV`
- Return `TV`

###### `download_subtitle_buffer()`
The function will use the provider instance stored within the version passed
to the function, and call its `download_subtitle_buffer()`.

###### `languages_in_use`
The function will collect all the languages from the providers, and return a 
list contains all of them.

###### `supported_languages`
The function will return all the languages present in the languages module, 
because a language is present in there only if at least single provider supports
it.