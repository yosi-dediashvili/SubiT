# Design of SubiT's API

The idea behind the API is to allow us to use SubiT in other programs (XBMC etc.), 
and also, separate between the core of SubiT, to everything else. This means that
SubiT will also use the API internally.

## Goals

Our goal for the API is to supply the following features:

1. Retrieve all the version for some query
2. Rank the versions
3. Retrieve the subtitle buffer for some version
4. Deploy the subtitle for some version
5. Multi-Threading support

The API will **NOT** supply:

1. Ability to perform several queries via single function (The user of the API 
will handle this)
2. User interaction inside API calls

## Separation

Via the API, we want to be able to override any configuration value. This means
that all the functions in the API will receive the configuration values relevant
for them via the arguments.

SubiT's configuration is not considered to be part of the core, so, the API will
not use it. Instead, when we'll use the API internally, we'll read the 
configuration and pass it to the API.

Additionally, any interaction with the user will be kept outside of the API.

## Usage

### Controlled usage

The first step is to retrieve an instance of the API:
```python
from SubiT import SubiTAPI
subit_api = SubiTAPI()
```

Now, suppose we have a version of the movie `Big Buck Bunny` in the path: 
`D:\Movies\Big Buck Bunny\big.buck.bunny.720p.dts.mkv`. And we 

We'll retrieve an Input instance for the query, and after that, all the versions
that are available:

```python
my_input = subit_api.get_input(
    r"D:\Movies\Big Buck Bunny\big.buck.bunny.720p.dts.mkv")
title_versions = subit_api.get_title_versions(my_input)
```

`title_versions` is a list that contains `Titles` that stores within them `Version`
that matches those titles.

We'll select some version, and retrieve its subtitle name and buffer:

```python
version = title_versions[0].versions[0]
subtitle_name, subtitle_buffer = subit_api.get_subtitle_buffer(my_input, version)
```

Additionally, we can request SubiT to deploy the subtitle for us (note that 
this function will have several other arguments that will allow us to control
the naming schemes, extensions, etc.):

```python
subit_api.deploy_subtitle(my_input, version, r"D:\Movies\Big Buck Bunny")
```

### Automatic usage

SubiT's API will allow much simpler usage also

```python
from SubiT import SubiTAPI
subit_api = SubiTAPI()
subit_api.download_subtitle(
    r"D:\Movies\Big Buck Bunny\big.buck.bunny.720p.dts.mkv",
    r"D:\Movies\Big Buck Bunny")
```

The function will retrieve the versions, rank them, select the best match and 
deploy it in the desired folder.