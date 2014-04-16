# Design of SubiT's processing flow

The processing flow is divided into three steps:

1. **Identification:**  
The first step is to identify what exactly we're looking for (A movie? A series? What resolution? What is the title? etc.)
2. **Collection:**  
The second step is collection subtitles that might be related to the title that we identified in the first step.
3. **Selection:**  
The last step is to select that the subtitle that matches the most to the title identified.

## Input
The input is the first step when it comes to processing some query. It's as soon as this stage that we distinguish between movie and series in the query.

It should be noted that it's not the input's responsibility to supply the right query for the providers. It should only supply the full information about what is being searched, and gather as much info as it can regarding that search.

# BaseInput
The base class for inputs. First, it will define whether the query was entered manually by the user (via the -q argument to the program, or via the search box and ```os.path.exists()``` returned false), or is an actual file on the system (i.e. the user dragged it to the program, or passed it via -f argument).

Also, we'll information about the title that we're searching (for movie it will be the movie name, and for series it will be the series name without the episode). 

The BaseInput will provide a factory method that will construct the appropriate input object (movie or series). For example:
```python
movie_input = BaseInput.new("The Matrix")
# Will yield true
isinstance(movie_input, MovieInput)
series_input = BaseInput.new("The Big Bang Theory S05E15")
# Will yield true
isinstance(series_input, SeriesInput)
```

The input is initialized only with a single input string which might be a full path to a file, or a simple search. It's the Input's job to figure out the type of the input.

#### InputStatus
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

#### Identifiers
The identifiers attribute withing the input object will have all the strings that was located regarding the input, that are not the title and the year of the input. For example:
```python
matrix_input = BaseInput.new("The.Matrix.720p.dts")
# Will print ['720p', 'dts']
print matrix_input.identifiers
```

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

## MovieInput
Represents a search for a movie. Will derive from BaseInput.

## SeriesInput
Represents a search for a series. Will derive from BaseInput. Additionally, will define two numbers, the **SeasonNumber** and the **EpisodeNumber**

```python
# The season number of the episode that is searched.
season_number = 0
# The episode number.
episode_number = 0
```
