# Design of SubiT's processing flow

The processing flow is divided into three steps:

1. **Identification:**  
The first step is to identify what exactly we're looking for (A movie? A 
series? What resolution? What is the title? etc.)
2. **Collection:**  
The second step is collection subtitles that might be related to the title that 
we identified in the first step.
3. **Selection:**  
The last step is to select that the subtitle that matches the most to the title 
identified.

## Identification

In order to make it easier to identify the right result, we need a strong 
separation between the movie/series as a title, and the format of that movie 
(sound quality, video quality etc.). 

In order to do that, we divide each input to SubiT into two. The title that is 
being searched, and the version of that title.

### Title

In order to support that separation, we introduce the Title object. The title
is not concerned about the format of the title. It contains information like the
name of the title, what year it was published, etc.

We have two version of Title. The first is the MovieTitle, and the second is the
SeriesTitle.

#### MovieTitle

Currently adds nothing to Title. It's simply makes it easier to distinguish 
between movie and series.

#### SeriesTitle

Adds episode numbering to the title, and the episode name.

**To sum up, the basic structure will look like this:**

```python
class Title:
    name = ""
    year = 0
    imdb_id = ""

class MovieTitle(Title):
    pass

class SeriesTitle(Title):
    season_number = 0
    episode_number = 0
    episode_name = ""
```


### Version

The version specify the format of the title that is being searched. In format 
we mean: Sound/Video quality, number of CDs, etc. The version does not care 
about the title that is being search, only about the format of that title, 
therefore, it does not care about what's the type of title (movie/series).

The version will be used both for specifying what is being searched (via the 
Input object), and what is present in each provider.

#### Identifiers
The identifiers attribute withing the version object will contain all the strings that represent the version.

**The basic structure will look like this:**
```python
class Version:
    identifiers = [""]
    # -1 means unknown.
    num_of_cds = 0
```


### Input

The input is the first step when it comes to processing some query. It will 
contain under it a single Title and Version instances that represents what is 
being searched.

This object is what the provider will receive in order to supply versions.

The Input object will first define whether the query was entered manually by the user (via the -q argument to the program, or via the search box and ```os.path.exists()``` returned false), or is an actual file on the system (i.e. the user dragged it to the program, or passed it via -f argument).

The Input will provide a factory method that will construct the appropriate input object (movie or series Title). For example:
```python
movie_input = Input.new("The Matrix")
# Will yield true
isinstance(movie_input.title, MovieTitle)
series_input = Input.new("The Big Bang Theory S05E15")
# Will yield true
isinstance(series_input.title, SeriesTitle)
```

The input is initialized only with a single input string which might be a full path to a file, or a simple search. It's the Input's job to figure out the type of the input.

##### InputStatus
A class within the BaseInput that serves as Enum. The class describes the status in which the input processing is currently in:
```python
class InputStatus:
    # The input is waiting in the queue.
    WAITING     = 0
    # The input's processing was started.
    PROCESSING  = 1
    # Finished, a subtitle was downloaded.
    SUCCEEDED   = 2
    # Finished, a subtitle was not downloaded.
    FAILED      = 3
```

In order to collect the identifiers, we introduce a new mechanism: **IdentifiersExtractors** The mechanism will use one or more implementation of an interface called IIDentifersExtractor. The goal of an implementation is to supply identification string given an Input class.

For starters, the implementations will be:
* OpenSubtitlesIdentifiersExtractor - Extracts identifiers by sending the file hash / file name to OpenSubtitle's service.
* FileNameIdentifiersExtractor - All the strings in the file name excepts for the title and year.
* DirectoryNameIdentifiersExtractor - All the strings in the directory name excepts for the title and year.

In the future, we might add some more sophisticated implementation like extracting the video and sound quality by parsing the file headers etc.

To sum up, the **BaseInput** will have the following attributes:
```python
# Zero or more full paths to the title's files. For series, it'll always have
# one item at most, but for movie, it might have several, if the movies has
# several discs.
full_path = [""]
# The title we're searching. For movies, it'll be the movie name, and for
# series, only the series name (without the season/episode number).
title = ""
# The year in which the title was released (For series, it will be the year in
# which the episode was aired).
year = 0
# The status in which the input is in.
status = InputStatus.WAITING
identifiers = [""]
```

#### MovieInput
Represents a search for a movie. Will derive from BaseInput.

#### SeriesInput
Represents a search for a series. Will derive from BaseInput. Additionally, will define two numbers, the **SeasonNumber** and the **EpisodeNumber**

## Collection

The second step is the collection of subtitles using the providers. Because the previous version of SubiT used the SubFlow mechanism, that didn't really stored the providers result in some useful structure, we need to construct such structure.

### Performance
One of the cons of the current structure of SubiT is that the providers are being used in an synchronous mode, were each provider gets used only after the previous one finished. There's no single reason to do that, and therefore, we need to change the way the providers are implemented. 

There are two facts that we should consider:

1. More than one input might be processed in any given time (each in a different location in the flow)
2. While we want to allow asynchronous operations with the providers, we don't want the same provider to start more than one active communication with the server. 

With this in mind, the new structure will look like this:
* Prior to the initialization of each provider, we'll initialize some sort of Connection/Request manager for each provider. This manager will be initialized with a domain (the provider's domain), and will have a queue to which it will post request, then, at any given time it will fetch at most one request from that queue, and post it to the site.
* Whenever a provider is initialized, it will be given an instance the instance of the manager that was initialized with its domain.
* The provider will always perform requests via the manager.
* Each input will have only one instance of each provider (inputs will not share instances of providers). The provider will live as long as the input lives.
* The input will not operate directly on the providers, instead, it will have some sort of a single, generic provider, that will hold all the other providers, and that will wrap all the operation with the providers. 

## Selection
 bla bla~ Yah YTah!~::