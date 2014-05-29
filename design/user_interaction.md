# SubiT's user interaction

When it comes to the user interaction in SubiT, we first need to take into 
consideration how the user is going to use it:

1. Opens the program with no arguments, and drags/browse for files/directories.
2. Opens the program with no arguments, and enters a query
3. Opens the program via context menu or command line with one or more files/directories.

In any case, after the user performed the action above, we need to allow him to 
perform the following:

1. Cancel the for one or more inputs
2. Select the right version manually for some input
3. Enter another query for some input (because he simply wants to, or because 
we couldn't figure out what Title was it)
4. Enter one or more additional files/directories/queries

## Interaction modes

SubiT will come with two different modes of interaction:

1. **Interactive GUI** - We'll try not to disturb the user as much as we allowed (
according to the configuration), but if we need to, we'll disturb him.
2. **Non-Interactive CLI** - In this mode we'll not interact with the user, but simply
print out the logs to the console. The user will be able to control us via the
arguments he passes to us. In this mode, whenever we face a case where we need
the user to guide us, we'll stop processing the query.


## Using the API

The way we use the API will vary according to the mode we're in. 

### Interactive GUI

If we're in the Interactive GUI mode, we'll use the controlled version of the 
API:

1. Pass the query in hope to get an input
    - If no input is returned, ask the user to modify the query
2. Request the versions for that input
    - If no version is present, notify the user
3. Select the best version
    - If the criteria for automatic selection is not met, we'll ask the user
4. Request to download it

We'll allow the user to stop us between every step. When he does so, we'll stop
our automatic flow completely for that query. 

### Non-Interactive CLI

If we're in the NonInteractive CLI mode, we'll still use the controlled version
of the API in order to print logs and such, but our action will be the default one:

1. Pass the query and get an Input
    - If input is None, drop the query
2. Request the versions for the query
    - If no version is retrieved, drop the query
3. Select the best matching version
    - If it reaches the minimal criteria for automatic download, use it, 
    otherwise, drop the query.
4. Download the subtitle
