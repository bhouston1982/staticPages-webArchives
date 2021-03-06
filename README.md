
# UWM Web Archives EAD update code

## April 4 Update

I've added two scripts to improve the formatting of our local EADs, to make them more receptive to adding Web Series.
+ createProcessed.py: This takes legacy finding aids (unserialized, components at the base C01 level), downshifts the component levels, and encapsulates them in a <c01+ level="otherlevel" otherlevel="processed"> tag. In addition to making it easier to add web series, this also makes it easier to add accessions later on.
+ serializeEads.py: This takes legacy finding aids (unserialized, components within a c01 "processed" tag) and creates a "General Files" series. This will make it easier to add series in future beyond the Web Archives series. Note that if the components are not nested in a c01 tag already, this script will fail; in this case, run createProcessed.py first.

-------------------


This is, as shown below, a fork of the University of Albany's code to generate subject and collection pages for their web archives collections. (My infinite gratitude to Greg for sharing this code with the community via the Archive-It blog.)

Since I am basically an amateur at this, I have eliminated the sections of code that make updates to HTML and am focusing on updates to EAD only.

Other major changes from the original (other than localization changes):
+ The Web Archives series is written to c02 rather than c01 because of the way we describe our unprocessed accessions.

+ Added additional information about the Archive-It harvester to the Phystech notes, and modified code to append to existing phystech notes if present

+ Added code to generate a scope/content note, pulling from a field in the CollectionsList spreadsheet.

+ Added code to generate a Revision Description change note whenever the script is run. (For right now this also lets me track how many times I have to run the code before I get it right!)

+ Added code to check if a capture is a main page or a subpage, and, if the latter, create the component a level down in the web series

A few usability notes on UWM finding aids:
+ If the contents list is not serialized, it needs to be serialized at the c02 level. I have thus far done this by moving everything into a general "Series 1: General Files, YYYY-YYYY" proxy series.
+ The code REALLY dislikes UTF-8 encoding. Watch for curly quotes and apostrophes when copying from the Archive-It metadata sheet.
+ Series and subseries need to be determined before running the script. If they collide with existing series, the code will crash-- or worse, erase things.


# staticPages-webArchives
Python scripts to generate static navigation pages from collection list and insert Web Archives records using the Archive-It CDX

There are three scripts here:


basicSample.py
--------------
+ A sample example script for making requests from the Archive-It CDX

+ by default this requests http://www.albany.edu/history/course-descriptions.shtml from the www.albany.edu Archive-it collection 3308

To look for a different URL just change Line 3 that begins with "requestURL = ":

	import requests
	
	requestURL = "http://wayback.archive-it.org/3308/timemap/cdx?url=http://www.albany.edu/history/course-descriptions.shtml"
	

Set `requestURL` as `http://wayback.archive-it.org/[Collection#]/timemap/cdx?url=[URL]` with your own URL and collection number.

CDX.py
------
+ A basic command line script for getting the number of captures and a date range from Archive-It URLS

Run in the command line as: `python CDX.py`

+ You will be prompted for a URL and an Archive-It collection number

staticPages.py
--------------
+ An example of the script we are using to make static pages while updating Web Archives records from the Archive-It and Wayback CDX API
+ collectionList.xslx is also included as a sample of the spreadsheet we are used to provide the data for this script

[Wayback CDX API Documentation](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server)
