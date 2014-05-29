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

## Using the API

Because we're counting on interaction with the user, we'll use the controlled 
version of the API:

1. Pass the query in hope to get an input, if not, ask the user
2. Requests the versions for that input
3. Select the best version
4. Request to download it

We'll allow the user to stop us between every step. When he does so, we'll stop
our automatic flow completely for that query.
