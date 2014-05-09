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


