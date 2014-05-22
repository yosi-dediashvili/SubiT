# SubiT's single input flow

The flow for a single input that will be passed to SubiT will be as follows:

* Create an Input instance, passing it the input string as-is
    - The Title instance will be created
    - The Version instance will be created
    - A Main provider instance will be retrieved from the factory
    - The status will be set to `QUEUED`
* The status will be set to `PROCESSING`
* The Main provider `getTitlesVersions()` method will be called
* The Right title will get selected
* The best matching version will get selected
* If no version can be selected, we either set the status to `FAILED` or 
`WAITING` if the user should help us.
* The Main provider `downloadSubtitleBuffer()` method will be called with the 
version.
* `deploySubtitle()` will be called with the input, version and subtitle buffer.
* The status will be set to `FINISHED`
