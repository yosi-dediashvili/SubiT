# SubiT's input processing

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

For the title, we'll have to attribute that specify its name. The first will be 
the raw name, that is the name as it appears originally in the source (provider, 
IMDB, etc.). The second attribute will be a list of normalized name. It will 
contain the raw name after a normalization process was applied to it as follows:

#### Discovering Titles

The first crucial step in the whole flow is to discover the title names. This 
means that when we receive an input string, we need to find out what title 
stands behind it.

In order to do so, we'll use a title discovery module named `titlediscovery` 
that will expose a single method named `discover_title`. The function will 
receive a single string value which may be a simple string or a full path to 
a file (movie/series). If the function will succeed in discovering the title, 
it will return a Title instance (Movie or Series). If not, None will be returned.

```python
def discover_title(query): pass
```

###### Implementation

The current version will use four methods for extracting the title (same as
SubiT 2.x), all of them will work against OpenSubtitles:

1. Sending the query to OpenSubtitles
2. Sending the file hash to OpenSubtitles
3. Sending the file name (no extension) to OpenSubtitles
4. Sending the directory name to OpenSubtitles

In the future, we'll probably add more methods, one, for example, will be 
sending the query/file name/directory to www.torec.net, because they have a 
search mechanism that is capable of discovering subtitles based on the release 
name (which in a lot of cases, is the file name).

#### Name normalization

The normalized names will be stored in a list where each item is the previous 
item with another normalization applied to it, with the first item being the 
raw name left untouched. If a normalization step ended up with the same result
as the previous step, it will not get inserted to the list.

###### The 1st step
1. Return the raw name as-is.

###### The 2nd step

1. Apply the ```Lower()``` function to it.
2. Replace every non-alphanumeric letter (including space) with underscore.
3. Replace any continuous underscore with a single one.
4. Remove any leading/trailing underscores.

###### The 3rd step

1. Convert each Arabic formatted number that is located either at the start or 
the end of the normalized name (and is followed/preceded by underscore), or 
is surrounded with two underscores to a lower case Latin one (`22' becomes `xxii`).

###### The 4th step

1. Convert each [Ordinal number](http://en.wikipedia.org/wiki/English_numerals#Ordinal_numbers) 
to its string alphabet equivalent (```1st``` becomes ```first```). We'll perform
the operation up to the number 20 (Past that it gets to complicated to guess how
it will be represented).

##### Examples

|         Before         |                                      After                                       |
|------------------------|----------------------------------------------------------------------------------|
| The Godfather: Part II | ```['The Godfather: Part II', 'the_godfather_part_ii']```                        |
| Schindler's List       | ```['Schindler's List', 'schindler_s_list']```                                   |
| Amélie                 | ```['Amélie', 'am_lie']```                                                       |
| The Godfather: Part 2  | ```['The Godfather: Part 2', 'the_godfather_part_2', 'the_godfather_part_ii']``` |
| The Third Man          | ```['The Third Man', 'the_third_man']```                                         |
| The 3rd Man            | ```['The 3rd Man', 'the_3rd_man', 'the_third_man']```                            |

* * *


#### Comparing titles

The title will provide a method for comparing it to another title. 

Given two titles, the equality check will return ```True``` according in any of 
the following cases:

* The IMDB's id is identical, and is not empty.
* The IMDB's id is empty in at least one title, the year matches (zero is 
    acceptable), and the normalized names share at least one name.

* * *
We have two version of Title. The first is the MovieTitle, and the second is the
SeriesTitle.

#### MovieTitle

Currently adds nothing to Title. It's simply makes it easier to distinguish 
between movie and series.

#### SeriesTitle

Adds episode numbering to the title, and the episode name. The episode name has
the same normalization mechanism as the Title's name. In this title, the `imdb_id`
value specifies the id of the **Series**, and another value, `episode_imdb_id` 
specifies the **Episode** id.

##### Comparing Series titles

When two series titles are compared, the check will return ```True``` in any 
of the following cases:

* **In any case, the Title's equality check should return True**
* The episode id is identical and is not empty.
* The season and episode number matches, and are not equal to zero.
* The season and episode number equal to zero, and the episode's normalized 
    names share at least one name.

* * *

**To sum up, the basic structure will look like this:**

```python
class Title:
    name = ""
    normalized_names = [name, ...]
    year = 0
    imdb_id = ""

class MovieTitle(Title):
    pass

class SeriesTitle(Title):
    episode_imdb_id = ""
    season_number = 0
    episode_number = 0
    episode_name = ""
    episode_normalized_names = [episode_name, ...]
```


### Version

The version specify the format of the title that is being searched. In format 
we mean: Sound/Video quality, number of CDs, etc. The version does not care 
about the title that is being search, only about the format of that title, 
therefore, it does not care about what's the type of title (movie/series).

For usability, the version will have reference to its associated title.

The version will be used both for specifying what is being searched (via the 
Input object), and what is present in each provider.

#### Identifiers
The identifiers attribute within the version object will contain all the 
strings (in lower-case format), that represent the version.

We'll have a module that its sole purpose is to extract identifiers for inputs.
The module name will be **IdentifierExtractor**, and it will expose a single 
method, named `extract_identifiers`, that will receive a `Title` instance and 
a query string which might be a full path to a movie file, or just a movie 
release name.

Within it, the module will have several methods for extracting identifiers.

The first step of the extraction will be to decide what will be the input for
the algorithm, the options are:
1. The query itself
2. The directory name, if the query is path to a movie file
3. The release name from OpenSubtitles after querying for the file hash/query

In the future, we might add some more sophisticated implementation like
extracting the video and sound quality by parsing the file headers etc.

***

**The basic structure of the Version will look like this:**
```python
class Version:
    title = None
    identifiers = [""]
    # -1 means unknown.
    num_of_cds = 0
```


#### ProviderVersion

This object will derive from Version, and will be used by the providers. It will
represent a single version result in each provider.

The object will have a language attribute that will determine the language of 
that version. Also, it will have a reference to the provider that generated it.

A instance of the class will have a rank value that should be set at initialization
by the creator (probably the provider). The rank algorithm is specified later, or
by some other logic determined by the creator (for example, if the provider
is certain that the version matches the one we're looking for, it might set the
rank to 100 without using the ranking algorithm).

Lastly, any other attribute that the provider will need to store under the 
version instance will be inserted into the attributes dictionary.

**The basic structure of ProviderVersion:**

```python
class ProviderVersion(Version):
    language = ""
    provider = None
    version_string = ""
    # Provider's specific attributes.
    attributes = {}
    rank = 0
    rank_group = 0
```

### Input

The input is the first step when it comes to processing some query. It will 
contain under it a single Title and Version instances that represents what is 
being searched.

This object is what the provider will receive in order to supply versions.

The Input object will first define whether the query was entered manually by 
the user (via the -q argument to the program, or via the search box and 
 ```os.path.exists()``` returned false), or is an actual file on the system 
(i.e. the user dragged it to the program, or passed it via -f argument).

The Input will provide a factory method that will construct the appropriate 
input object (with movie or series Title). For example:
```python
movie_input = Input.new("The Matrix")
# Will yield true
isinstance(movie_input.title, MovieTitle)
series_input = Input.new("The Big Bang Theory S05E15")
# Will yield true
isinstance(series_input.title, SeriesTitle)
```

The input is initialized only with a single input string which might be a full 
path to a file, or a simple search. It's the Input's job to figure out the type 
of the input.

Access to the provider will be made via a main provider instance. This provider
will store the actual results from the providers, and will pass the providers 
the input in order to receive results. This way, we keep the providers logic out
of the Input's logic

#### InputStatus

In order to specify where are we in the whole process of locating the right
subtitle, the Input uses a status, a class within the BaseInput that serves as 
Enum. The class describes the status in which the input processing is currently 
in:
```python
class InputStatus:
    # The input instance was created. It might take some time from this step to
    # the next step if there are several inputs in the queue.
    CREATED = 0 
    # States regarding the Title lookup
    TITLE_SEARCH
    TITLE_FOUND
    TITLE_FAILURE # We can't find a title
    # States regarding the versions lookup for the title
    VERSIONS_SEARCH
    VERSIONS_FOUND
    VERSIONS_FAILURE # We can't find versions
    # States regarding matching a version to our version
    VERSION_MATCHED
    VERSION_FAILURE # Can't find matching version
    # States regarding the download process (not deployment)
    DOWNLOAD_START
    DOWNLOAD_SUCCESS
    DOWNLOAD_FAILURE
    # States regarding the deployment process (extracting and saving the files)
    DEPLOYMENT_START
    DEPLOYMENT_SUCCESS
    DEPLOYMENT_FAILURE
    # Last states
    SUCCEEDED # Subtitle file/s downloaded
    FAILED # No subtitle got downloaded
```

***

**To sum up, the Input will have the following structure:**
```python
class Input:
    # Zero or more full paths to the title's files. For series, it'll always 
    # have one item at most, but for movie, it might have several, if the 
    # movies has several discs.
    full_path = [""]
    # The status in which the input is in.
    status = InputStatus.CREATED
    # The title instance
    title = None
    # The version instance
    version = None
    # The main provider, wraps the use of all the providers.
    main_provider = None
```


## Collection

The second step is the collection of subtitles using the providers. Because the 
previous version of SubiT used the SubFlow mechanism, that didn't really stored 
the providers result in some useful structure, we need to construct such 
structure.

Additionally, while the previous design of the provider was one that used 2 
steps in order to get to a subtitle version, the current design will have only
one step. This will allow us to select the right version while we have all the
versions from all the providers, and not just portion of it.

### TitleVersions

In this version, we're dropping the stages mechanism. In order to receive 
versions from the providers, we'll pass them the Input object. And in return, we
will get a list of **TitleVersions** instances, that is a simple structure that 
unites several **ProviderVersion** under a single **Title**.

When a provider returns us a list of versions that might match the input that 
was passed to it, it will group the versions by title, thus, we'll have **Zero**
or more titles for each input, and under each title, it will have **One** or 
more **ProviderVersions**.

The **versions** attribute will be a dictionary that its keys are the languages
and the values are also dictionary that is keys are the rank group and the 
values are tuples of the provider rank and the provider version falling under 
that group.

Notice that the provider will not drop version because they come from a 
different title. That's not its job.

A TitleVersions will be constructed using a single Title instance, and zero or
more ProviderVersion instances (the list does not need to be sorted). Each 
version passed, will be inserted to the dictionary using the `add_version` 
method, with the default provider_rank value.

The class will expose a function named `add_version` which inserts a 
provider_version to the versions dictionary in the appropriate position. The 
function will receive an optional parameter `provider_rank` that defaults to 1,
and can be changed (will be different when the MainProvider will create its 
TitleVersions). The algorithm for the function is described later.

**The basic structure of the TitleVersions will look like that:**
```python
class TitleVersions:
    title = None
    # {language, {rank_group: [(provider_rank, provider_version), ...]}}
    versions = {"" : [None]}
    def __init__(title, versions = []): pass
    def add_version(provider_version, provider_rank = 1): pass
```

### Performance
One of the cons of the current structure of SubiT is that the providers are 
being used in an synchronous mode, were each provider gets used only after the 
previous one finished. There's no single reason to do that, and therefore, we 
need to change the way the providers are implemented. 

There are two facts that we should consider: 

1. More than one input might be processed in any given time (each in a 
different location in the flow)
2. While we want to allow asynchronous operations with the providers, we don't 
want the same provider to start more than one active communication with the 
server. 

With this in mind, the new structure will look like this:

* Prior to the initialization of each provider, we'll initialize some sort of 
Connection/Request manager for each provider. This manager will be initialized 
with a domain (the provider's domain), and will have a queue to which it will 
post request, then, at any given time it will fetch at most one request from 
that queue, and post it to the site.
* Whenever a provider is initialized, it will be given an instance the instance 
of the manager that was initialized with its domain.
* The provider will always perform requests via the manager.
* Each input will have only one instance of each provider (inputs will not share 
instances of providers). The provider will live as long as the input lives.
* The input will not operate directly on the providers, instead, it will have 
some sort of a single, generic provider, that will hold all the other providers, 
and that will wrap all the operation with the providers. 

## Selection

The selection phase is the most important step in the flow. Our goal is to 
select the best matching version that is present in the TitleVersions.

#### Matching titles

The first step will be to select the right title from the ones that we 
collected. In order to do so, we simply use the Title's equality check. Note 
that we expect only single (at most) title from the collected titles to match 
the Input's title. Otherwise, something went wrong in the process.

If we fail to match against a title, we'll not proceed to version matching, and
instead, use the behavior that is specified in the configuration (exit/ask the 
user/etc.).

#### Matching versions

After the title got chosen, we'll select a single version out of it. We divide 
the process into two steps:

##### 1. Sorting the versions

The sorting process consist also of two steps:

###### 1. Giving the ProviderVersion instances a rank

The rank will be a value from 0 to 100, where 100 specify a perfect match, and
0 specify the worst possible match.

The ranking algorithm will be as follows:

- Group the version based on their language
    - For each language
        - For each version
            - Rank it using the rank algorithm.

A single version will be ranked with the following algorithm:

- If at least one of the versions has a `num_of_cds` values of `UNKNOWN` or 
    their `num_of_cds` is equal, continue in the rank, otherwise, give the 
    version a rank of 0.
- Count the number of identifiers in the input version as `IIC` and in the
    provider version as `PIC`.
- If either `PIC` or `IIC` is 0, give the version rank of 0.
- Count the number of identifiers that **only** appears in the provider's 
    version as `POC`, and in the input's as `IOC`
- Define `100 = IR/PR` as the ration between the input's identifiers and the 
    provider's ones. (`IR` and `PR` will be configured in the configuration)
- Calculate the rank as: `100 - ((IR * (IOC / IIC)) + (PR * (POC / PIC)))`

For example:

If the configuration specify a ratio of 60:40 for the Input identifiers:

```python
input_identifiers = ["720p", "ac3", "bluray", "chd"]
provider_identifiers = ["720p", "ac3", "wtf"]

IIC = len(input_identifiers)
PIC = len(provider_identifiers)

IOC = float(len(set(input_identifiers).difference(provider_identifiers)))
POC = float(len(set(provider_identifiers).difference(input_identifiers)))

IR = 60
PR = 40

# rank will be equal to 56.66...
rank = 100 - ((IR * (IOC / IIC)) + (PR * (POC / PIC)))
```

###### 2. Sorting within each rank group

After we ranked all the version, we'll divide the versions into groups based on
their rank. The first group will be versions with rank **0** to **10**, the 
second will be from **11** to **20**, the third from **21** to **30** etc.

Within each group, we'll sort the versions based on the provider's order that
is defined in the configuration.

For example:

If version #1 has a rank of 100 with provider that is placed 2nd in the 
configuration, and version #2 has a rank of 95 with provider that is placed 1st,
version #2 will be placed before version #1.

##### 2. Selecting the first version

The final step is to select the version. In order to do that, we use two values
that defines the behavior. The first value is the minimal rank that is required
in order for us to download a version without asking the user (in the example,
we'll name it `MAR`). The second value is the maximum rank, that if not passed,
we'll try to find a subtitle version in a different selected language (we'll 
name this value `MLR`).

NOTE: Both values should be set to one of the values from `[0, 10, 20, ..., 90]`.

The selection algorithm will be as followed:

- For each language that is specified in the configuration (starting from the 
    first)
    - If the first version in the versions list has a rank higher than `MAR`, 
        select it.
    - Otherwise, if the first version has a value lower than `MLR`, continue 
        to the next language.
- If no version was selected, perform the action that is specified in the 
configuration.
