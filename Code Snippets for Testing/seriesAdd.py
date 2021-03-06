# -*- coding: utf-8 -*-

from lxml import etree as ET
from openpyxl import load_workbook
from operator import itemgetter
import os
import copy
import requests
import datetime


#lxml parser for parsing XML files from strings
parser = ET.XMLParser(remove_blank_text=True)

if os.name == "nt":
	#Windows Directory Names
	
	#Finding Aid Directory
	faDir = "g:\WebArch"
	#Collection and Subject spreadsheets directory
	spreadDir = "g:\WebArch"
	#parse Collection List spreadsheet
collectionListFile = os.path.join(spreadDir, "collectionList.xlsx")
collectionWorkbook = load_workbook(filename = collectionListFile)
collectionList = collectionWorkbook.active

#Parse List of Collections to list of lists
rowIndex = 0
collections = []
for row in collectionList.rows:
	rowIndex = rowIndex + 1
	if rowIndex > 1:
		collection = [str(rowIndex), row[0].value, row[1].value, row[2].value, row[3].value, row[4].value, row[5].value, row[6].value, row[7].value, row[8].value, row[9].value, row[10].value, row[11].value]
		collections.append(collection)
	
#Function to make DACS and Normal (ISO) dates from CDX timestamp
def makeDate(stamp):
	calendar = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}
	year = stamp[:4]
	month = stamp[4:6]
	day = stamp[-2:]
	normal = year + "-" + month + "-" + day
	if day.startswith("0"):
		day = day[-1:]
	dacs = year + " " + calendar[month] + " " + day
	return dacs, normal
					
		
        ###################################################################################	
        #Web Archives Section
        ###################################################################################
#Archive-It CDX API request
for collection in collections:
        

        webUrl = str(collection[12])
        archiveItCollection = str(collection[11])
        print "looking for web archives captures for collection  " + str(collection[1])
        archiveIt = False
        wayback = False
        requestURL = "http://wayback.archive-it.org/" + archiveItCollection + "/timemap/cdx?url=" + webUrl
        #for debugging:
        print requestURL
        response = requests.get(requestURL)
        responseText  = response.text

        #variable to count number of captures:
        aiCount = 0
        #if lenght of HTTP response is greater than 5, aribitrary value to check for any captures
        if len(responseText) > 5:
                archiveIt = True
                responseLines = responseText.split("\n")
                firstPage = responseLines[0]
                for textLine in responseLines:
                        aiCount = aiCount + 1
                        if len(textLine) > 5:
                                lastPage = textLine
                #get date range of captures
                firstDate = firstPage.split(" ")[1][:8]
                lastDate = lastPage.split(" ")[1][:8]


        #general Wayback CDX API request
        wayRequestURL = "http://web.archive.org/cdx/search/cdx?url=" + webUrl
        #for debugging:
        #print wayRequestURL
        wayResponse = requests.get(wayRequestURL)
        wayResponseText  = wayResponse.text
        waybackCount = 0
        if len(wayResponseText) > 120:
                wayback = True
                wayResponseLines = wayResponseText.split("\n")
                wayFirstPage = wayResponseLines[0]
                for wayLine in wayResponseLines:
                        if len(wayLine) > 5:
                                waybackCount = waybackCount + 1
                                wayLastPage = wayLine
                #get date range of captures
                wayFirstDate = wayFirstPage.split(" ")[1][:8]
                wayLastDate = wayLastPage.split(" ")[1][:8]

        #check if actually found any captures and convert to DACS and Normal (ISO) dates
        if archiveIt == False and wayback == False:
                pass
        else:
                if archiveIt == False:
                        #get DACS and normal dates
                        dateRange = [wayFirstDate, wayLastDate]
                        seriesMax = max(dateRange)
                        seriesMin = min(dateRange)
                        seriesMaxDacs, seriesMaxNormal = makeDate(seriesMax)
                        seriesMinDacs, seriesMinNormal = makeDate(seriesMin)
                        seriesDacs = seriesMinDacs + "-" + seriesMaxDacs
                        seriesNormal = seriesMinNormal + "/" + seriesMaxNormal
                        
                elif wayback == False:
                        #get DACS and normal dates
                        dateRange = [firstDate, lastDate]
                        seriesMax = max(dateRange)
                        seriesMin = min(dateRange)
                        seriesMaxDacs, seriesMaxNormal = makeDate(seriesMax)
                        seriesMinDacs, seriesMinNormal = makeDate(seriesMin)
                        seriesDacs = seriesMinDacs + "-" + seriesMaxDacs
                        seriesNormal = seriesMinNormal + "/" + seriesMaxNormal
                        
                else:
                        dateRange = [firstDate, lastDate, wayFirstDate, wayLastDate]
                        seriesMax = max(dateRange)
                        seriesMin = min(dateRange)
                        seriesMaxDacs, seriesMaxNormal = makeDate(seriesMax)
                        seriesMinDacs, seriesMinNormal = makeDate(seriesMin)
                        seriesDacs = seriesMinDacs + "-" + seriesMaxDacs
                        seriesNormal = seriesMinNormal + "/" + seriesMaxNormal



                #Show feedback for web archvies
                print "found Web Archives for " + str(collection[1])
                
                #parse EAD file for collection
                eadFile = os.path.join(faDir, str(collection[1]) + ".xml")
                faInput = ET.parse(eadFile, parser)
                fa = faInput.getroot()
               
                #Get Web Archvies Series Semantic ID
                webArchSeries = "series" + str(collection[10])
                webArchSub = "subseries" + str(collection[8])

                now = datetime.date.today()
                newchange = ET.Element("change")
                newchange.set("encodinganalog","583")
                changedate = ET.SubElement(newchange, "date")
                changedate.set("normal", now.isoformat())
                changedate.text = now.strftime("%B %d, %Y")
                changeitem = ET.SubElement(newchange, "item")
                changeitem.text = "Brad Houston updated the finding aid to reflect addition of new web URLs(" + webArchSeries +", " + webArchSub +")."
                fa.find(".//revisiondesc").insert(0,newchange)
                              
                           
                
             #find or create Web Archvies Series
                if fa.find("archdesc/dsc") is None:
                        print "creating web archives series"
                        dsc = ET.Element("dsc")
                        fa.find("archdesc").append(dsc)
                        series = ET.Element("c01")
                        series.set("id", webArchSeries)
                        dsc.append(series)
                else:
                        match = False
                        for series in fa.find("archdesc/dsc/c01[@otherlevel='processed']/c02[@id='series2']"):
                                if series.tag == "c03":
                                        if series.attrib["id"] == webArchSub:
                                                match = True
                        if match == False:
                                newSeries = ET.Element("c03")
                                newSeries.set("id", webArchSub)
                                fa.find("archdesc/dsc/c01[@otherlevel='processed']/c02[@id='series2']").append(newSeries)

                #iterate though EAD and find matching series
                for series in fa.find("archdesc/dsc/c01[@otherlevel='processed']/c02[@id='series2']"):
                        if series.tag == "c03":
                                if series.attrib["id"] == webArchSub:
                                        #for debugging:
                                        print "found series"
                                        series.set("level", "file")\
                                        #find or create <did>
                                        if series.find("did") is None:
                                                did = ET.Element("did")
                                                series.insert(0, did)
                                        #find or create <unitid>
                                        if series.find("did/unitid") is None:
                                                unitid = ET.Element("unitid")
                                                unitid.text = "subseries" + str(collection[8])
                                                series.find("did").insert(0, unitid)
                                        #update <unittitle>
                                        if series.find("did/unittitle") is None:
                                                unittitle = ET.Element("unittitle")
                                                unittitle.text =str(collection[7])
                                                series.find("did").insert(1, unittitle)
                                        #remove existing <unitdate>s
                                        if not series.find("did/unitdate") is None:
                                                series.find("did").remove(series.find("did/unitdate"))
                                        #Add new <unitdate>
                                        unitdate = ET.Element("unitdate")
                                        unitdate.set("type", "inclusive")
                                        unitdate.set("normal", seriesNormal)
                                        unitdate.text = seriesDacs
                                        series.find("did").insert(2, unitdate)
                                        #remove existing <physdesc>
                                        if not series.find("did/physdesc") is None:
                                                series.find("did").remove(series.find("did/physdesc"))
                                        #Add new <physdesc> with count of captures
                                        physdescElement = ET. Element ("physdesc")
                                        extentElement = ET.Element("extent")
                                        extentElement.text = str(aiCount + waybackCount)
                                        extentElement.set("unit", "captures")
                                        physdescElement.append(extentElement)
                                        series.find("did").append(physdescElement)
                                       
                                                
                                        #remove existing web archives links
                                        for oldc02 in series:
                                                if oldc02.tag == "c04":
                                                        series.remove(oldc02)
                                        #variable to make new semantic IDs
                                        idCount = 0
                                        
                                        #Make Archive-it <c03>
                                        if archiveIt == True:
                                                idCount = idCount + 1
                                                aiFile = ET.Element("c04")
                                                aiFile.set("id", webArchSeries + "_" + str(idCount))
                                                aiDid = ET.SubElement(aiFile, "did")
                                                aiContainer = ET.SubElement(aiDid, "container")
                                                aiContainer.set("type", "Web-Archive")
                                                aiContainer.text = "1"
                                                aiUnittitle = ET.SubElement(aiDid, "unittitle")
                                                aiUnittitle.text = webUrl + " - University Archives collection"
                                                aiUnitdate = ET.SubElement(aiDid, "unitdate")
                                                firstDacs, firstNormal = makeDate(firstDate)
                                                lastDacs, lastNormal = makeDate(lastDate)
                                                aiUnitdate.set("normal", firstNormal + "/" + lastNormal)
                                                aiUnitdate.text = firstDacs + "-" + lastDacs
                                                aiDao = ET.SubElement(aiDid, "dao")
                                                aiDao.set("actuate", "onrequest")
                                                aiDao.set("linktype", "simple")
                                                aiDao.set("show", "new")
                                                aiDao.set("href", "http://wayback.archive-it.org/" + archiveItCollection + "/*/" + webUrl)
                                                series.append(aiFile)
                                                
                                                
                                        
                                        #add general Wayback <c03>
                                        if wayback == True:
                                                idCount = idCount + 1
                                                wayFile = ET.Element("c04")
                                                wayFile.set("id", webArchSeries + "_" + str(idCount))
                                                wayDid = ET.SubElement(wayFile, "did")
                                                wayContainer = ET.SubElement(wayDid, "container")
                                                wayContainer.set("type", "Web-Archive")
                                                wayContainer.text = "2"
                                                wayUnittitle = ET.SubElement(wayDid, "unittitle")
                                                wayUnittitle.text = webUrl + " - Internet Archive collection"
                                                wayUnitdate = ET.SubElement(wayDid, "unitdate")
                                                firstDacs, firstNormal = makeDate(wayFirstDate)
                                                lastDacs, lastNormal = makeDate(wayLastDate)
                                                wayUnitdate.set("normal", firstNormal + "/" + lastNormal)
                                                wayUnitdate.text = firstDacs + "-" + lastDacs
                                                wayDao = ET.SubElement(wayDid, "dao")
                                                wayDao.set("actuate", "onrequest")
                                                wayDao.set("linktype", "simple")
                                                wayDao.set("show", "new")
                                                wayDao.set("href", "https://web.archive.org/web/*/" + webUrl)
                                                series.append(wayFile)
               
                                                                                      
                faString = ET.tostring(fa, pretty_print=True, xml_declaration=True, encoding="utf-8")
                faFile = open(eadFile, "w")
                faFile.write(faString)
                faFile.close()
