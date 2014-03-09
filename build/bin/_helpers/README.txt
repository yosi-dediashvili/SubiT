 _____       _     _ _____ 
/  ___|     | |   (_)_   _|
\ `--. _   _| |__  _  | |  
 `--. \ | | | '_ \| | | |  
/\__/ / |_| | |_) | | | |  
\____/ \__,_|_.__/|_| \_/ 

First of all, feel free to contact us with any problem at:
http://www.subit-app.sourceforge.net/contact.html

For Windows users:
	It's recommended that you will use the win32 setup file of SubiT in order to perform the installation.
	However, if you refuse to do so, follow this steps:
	
	How To Install: 
		1. Extract files from the rar archive
		2. For right click association, Click Start->Run->Cmd, and type in the location of SubiT.exe 
		   file and pass it the -associate param, i.e. "SubiT.exe -associate" (without the quotes)
		3. Use right click on a movie/ TV show or just run SubiT.exe

	How To Uninstall:
		1. For right click association, Click Start->Run->Cmd, and type in the location of SubiT.exe 
		   file and pass it the -unassociate param, i.e. "SubiT.exe -disassociate" (without the quotes)
		2. Delete SubiT's folder

	*NOTE: If the right click menu doesn't work (complains about missing file or something like that), Execute 
	SubiT and go to Settings->Context Menu, and uncheck the "Associate extensions" check box, click apply, and
	recheck the checkbox, and finally, click Apply.

For Linux users:
	1. SubiT source code is compiled using python 2.7.3
	2. The tar.gz comes with everything needed for SubiT to run (except for python)
	3. Currently, a right click association is not supported under linux
	4. Simply extract the files from the tar.gz file, and execute SubiT
	* If you like, we also provide a pyc version of SubiT, which is just the pure byte-code created from the source of SubiT

For OSX users:
	From minor checks that we've made, SubiT is capable of running under OSX after the PySide module is installed
	on the System. We currently not supporting OSX. Contact us if you're interested on running SubiT under 
	apple's OS.


Using SubiT in Command Line mode (CLI):
	After several requests for cli mode in SubiT, we added this feature in version 2.0.0. To activate it, 
	you need to manually edit the config.ini file of SubiT (located under SubiTs folder, in the Settings 
	directory). The relevant key in the configuration is the Global.interaction_type.

	In order to apply gui, set the value to 0.
	In order to apply silent gui mode, set the value to 1 (won't work, set for future implementation).
	In order to apply cli, set the value to 2.
	In order to apply silent cli mode, set the value to 3 (Probably won't work that good).

	Launch SubiT as usual.

===========================================================================
Changelog:
===========================================================================
* Version 2.2.1 - 
Fixed Subscenter's provider

* Version 2.2.0 -
Added support for www.subscene.com
Added fake subtitle check to Torec's provider (we'll no longer download the fake subtitles)
Fixed SubsCenter's provdier
Improved the logic in Addic7ed's provider (Distinguish between serieses and movies results)
Added more languages (Spanish, Turkish, Slovak and Czech)
Added Unit Testing for the SubProviders
Fixed compilation scripts so they do not contain staic paths
Search line is kept after the subtitle is downloaded
Close on finish is set to False by default

* Version 2.1.2 -
Fixed Torec's and Subtitle's providers.

* Version 2.1.1 -
Fixed major bug occured when the user input is needed in order to determine the right subtitle version
Fixed major bug when trying to download a subtitle file from a free-query
Fixed ContextMenuHandler registration under 64bit versions of windows
Fixed www.Torec.net's provider in to bypass the new blocking system

* Version 2.1.0 -
Use argparse to parse the arugments
Save the last window size (when the program closes) for the next program startup
Remember the visibility of the log window
Add option to select between startup point of center screen or mouse position
Add option (in config) to simply use all the providers (instead of choosing them all)
Fix empty result returned by Addic7ed's provider
Return Win32_Error to notify failure in download
Distribute SubiT with no language selected
Create new Context Menu for windows platform
Adjust latin numbering for the ranking functions
Fix TorecProvider blocking
Create a new SubFlow.
Put movie name in the textbox when it's past as a parameter to SubiT

* Version 2.0.2 (Linux only) - 
Major bug fix in SubiT's console mode

* Version 2.0.1 - 
Critical Bug fix in the ranking functions
Edge case Bug fix in movie name formatting function
Bug fix in the update notification

* Version 2.0.0 - 
New head version!
Major GUI improvments and changes
Added support for www.addic7ed.com
Movie file drop to SubiT's main window is now supported
Added support for default download location
Improved log messages
Subtitles selection flow improved
Subtitles Ranking function improved
Improved provider selection (both language and site)
Fixed update mechanizm
Privilage elevation is requested when performing right-click association in none Admin account (under Windows)
Crashing fixed completely

* Version 1.3.1 - 
Added support for primary and secondary language subtitles search
Removed auto-update feature (the feature will return on later version)
Improved function for subtitles versions ranking
Added support for Linux (Checked under ununtu)
Right-click registration problem - Fixed (still need to run as administrator for registration)
Changed www.sratim.co.il handler to work with the latest changes on the site
Changed www.torec.net handler to work with the latest changes on the site
Fixed several minor bugs

* Version 1.3.0 - 
Added full support for www.sratim.co.il
Added full support for www.subscenter.org
Added upate mechanizm (AutoUpdate&Update notification)
Using www.OpenSubtitles.org's file hash&name data to identify movies (and serieses) 
Moved to unified configuration file and better settings window
Enabled auto-close on finish

* Version 1.2.0 - 
Added support to www.subscenter.org subtitles (Movies only)
Added restart options in settings windows
Fixed crashing problems

* Version 1.1.0 - 
Added support to www.OpenSubtitles.org subtitle services Added support for selecting different subtitle handler 
Gui Improvments 

* Version 1.0.0 - 
Bug fix and new features 

* Version 0.9.9 - 
Initial release


--==Special thanks to www.OpenSubtitles.org for delivering their API==--