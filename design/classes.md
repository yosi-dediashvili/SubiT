# Design of SubiT's processing flow


## Input
The input is the first step when it comes to processing some query. It's as soon as this stage that we distinguish between movie and series in the query.

# BaseInput
The base class for inputs. First, it will define whether the query was entered manually by the user (via the -q argument to the program, or via the search box and os.path.exists returned false), or is an actual file on the system (i.e. the user dragged it to the program, or passed it via -f argument).

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

## MovieInput
Input of movie. Will derive from BaseInput.

## SeriesInput
Input of series. Will derive from BaseInput.

Will define the season number and the episode number (as numbers, not encoded to string). 