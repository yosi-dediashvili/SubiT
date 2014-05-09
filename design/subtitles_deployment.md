# SubiT's subtitles deployment

The deployment of the downloaded subtitles is the last step in SubiT's flow.
The input to this step is a buffer that its content might be one of the 
following:

1. Single text file (.srt/.sub etc.)
2. Zip file
3. RAR file

This step is responsible for:

1. **Where** to put the subtitle file/files
2. How to **name** each of the subtitles

While the case in which the buffer is a single subtitle file is simple to 
handle, it's gets complicated when we have several subtitles files in the
archive.

## Archive files

A subtitles archive files contains, most of the time, the following files:

- One or more (In case the version uses several discs) subtitle files
- Zero or more nfo/txt files, etc.

We're only interested in the subtitle files, so we'll not extract the other 
files. 

### Recognizing subtitle files within the archive

We'll recognize the subtitle files within the archive by their extensions. SubiT
will expose via configuration a list of file extensions that are considered to
be subtitle files extensions.

### Identifying cd number within file names

The algorithm for extracting the cd number from the subtitle file (when it's)
within archive, will count on the assumptions:

1. The only part of the name that should be different between two subtitle files
within an archive, is the cd number.
2. The difference will only be a single digit.

Then, the algorithm will be:

- Take two subtitle file names `SA` and `SB`
- Subtract `SB` from `SA` such that `SA` will be left only with the chars 
that are not present in `SB` and name it `SA_CD`
- If `SA_CD` is a single digit
    - Use it as the CD number for `SA`
- Otherwise
    - Define the CD number for `SA` as unknown

## Directory location

We'll offer three options regarding where to deploy the subtitles:

1. At the same directory as the input (if there's any)
2. At a predefined directory
3. Ask the user each time

## File names

We'll use a naming scheme for naming the subtitles. SubiT will offer several 
symbols that will get interpreted during the deployment process. 

### Symbols

For movie and series, we'll have the following symbols:

- `input_file_name` - The name (without the extension) of the input file
- `subtitle_file_name` - The name of the subtitle file itself, as it was 
sent from the servers
- `language` - The language of the version that was downloaded (
Based on the ISO 639-2 standard)
- `title` - The movie/series title
- `year` - The movie/series year

For series, we'll also have the following symbols:

- `season_number_padded` - 2 digits long season number (02, 11, etc.)
- `season_number` - The season number (2, 11, etc.)
- `episode_number_padded` - 2 digits long episode number (02, 11, etc.)
- `episode_number` - The episode number (2, 11, etc.)
- `episode_name` - The name of the episode

For movie, we'll have the following symbols:

- `cd_number` - A one digit long cd number

### Schemes

We'll have three naming scheme:

1. For movies with single cd
2. For movies with multiple cds
3. For series (assumed to be single cd always)

#### Scheme usage

A scheme is simply a static string that we'll hold in the program. Each symbol
`S` in the scheme, will be represented as `${S}`. Any symbol that is located
will be replaced by its appropriate value.

Any other string that will be present in the scheme, will be left untouched.

##### Examples

##### One cd movies

###### Input:

|    Title     |  Year  |           Input file           |  Language |
|--------------|--------|--------------------------------|-----------|
| `The Matrix` | `1999` | `the.matrix.1999.720p.dts.mkv` | `English` |

###### Schemes:

|               Scheme               |             Result             |
|------------------------------------|--------------------------------|
| `${title}.${year}-${language}.srt` | `The Matrix.1999-eng.srt`      |
| `${input_file}.srt`                | `the.matrix.1999.720p.dts.srt` |

##### Multiple cds movies

###### Input:

|    Title     |  Year  | cds |                               Input files                                |  Language |
|--------------|--------|-----|--------------------------------------------------------------------------|-----------|
| `The Matrix` | `1999` |   2 | `the.matrix.dvdrip.ac3.cd1.avi, the.matrix.dvdrip.ac3.cd2.avi` | `English` |

###### Schemes:

|                  Scheme                 |                                 Result                                 |
|-----------------------------------------|------------------------------------------------------------------------|
| `${title}.${year}.disc${cd_number}.srt` | `The Matrix.1999.disc1.srt, The Matrix.1999.disc2.srt`                 |
| `${input_file}-${language}.srt`         | `the.matrix.dvdrip.ac3.cd1-eng.srt, the.matrix.dvdrip.ac3.cd2-eng.srt` |

##### Series

###### Input:

|         Title         |  Year  | Season | Episode |              Name             |                         Input file                        | Language |
|-----------------------|--------|--------|---------|-------------------------------|-----------------------------------------------------------|----------|
| `The Big Bang Theory` | `2013` | `6`    | `3`     | `The Higgs Boson Observation` | `The.Big.Bang.Theory.S06E03.720p.HDTV.X264-DIMENSION.mkv` | `Hebrew` |

###### Schemes:

|                                  Scheme                                  |                             Result                            |
|--------------------------------------------------------------------------|---------------------------------------------------------------|
| `${title}.${year}.S${season_number_padded}E${episode_number_padded}.srt` | `The Big Bang Theory.2013.S06E03.srt`                         |
| `${input_file}-${language}.srt`                                          | `The.Big.Bang.Theory.S06E03.720p.HDTV.X264-DIMENSION-heb.srt` |
| `${title} - ${season_number}x${episode_number} - ${episode_name}.srt`    | `The Big Bang Theory - 6x3 - The Higgs Boson Observation.srt` |

