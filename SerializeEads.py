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
	faDir = "H:\Departments\Archives\Students\Web Archiving\serialize"

#Iterate through files in the directory                
for file in os.listdir(faDir):
        eadFile = os.path.join(faDir, str(file))
        faInput= ET.parse(eadFile, parser)
        fa = faInput.getroot()
        if fa.find("archdesc/dsc/c01[@otherlevel='processed']") is None:
                print "The EAD for " + str(file) + " doesn't have a processed component. Please fix it and try again."
                
        elif not fa.find("archdesc/dsc/c01[@otherlevel='processed']/c02[@level='series']") is None:
                print "The EAD for " + str(file) + " has already been serialized."
                
        else:
#Update the revisiondesc note
                try:
                        now = datetime.date.today()
                        newchange = ET.Element("change")
                        newchange.set("encodinganalog","583")
                        changedate = ET.SubElement(newchange, "date")
                        changedate.set("normal", now.isoformat())
                        changedate.text = now.strftime("%B %d, %Y")
                        changeitem = ET.SubElement(newchange, "item")
                        changeitem.text = "Brad Houston serialized the contents list to prepare for insertion of web archives."
                        fa.find(".//revisiondesc").insert(0,newchange)
                except:
                        print "No revisiondescription note!"
                        pass
                #Move all components in the processed collection down one level.
                #When I get better at this I will have it automatically count the levels and do that many loops.
                #For now, we're just going to do it this way, through the c06 level.
                print "Adjusting component levels for " + str(file) + "."
                for c02 in fa.find("archdesc/dsc/c01[@otherlevel='processed']"):
                        for c03 in c02:
                                for c04 in c03:
                                        for c05 in c04:
                                                if c05.tag == "c05":
                                                        c05.tag = "c06"
                                        if c04.tag == "c04":
                                                c04.tag = "c05"
                                if c03.tag == "c03":
                                        c03.tag = "c04"
                        if c02.tag == "c02":
                                c02.tag = "c03"

        #Cleanup the current processed contents list and prep for moving
                try:
                        print "Moving series for " + str(file) + "."
                        oldseries = fa.xpath("//c01")[0]
                        serID = oldseries.attrib.get("id")
                        olddid = oldseries.find("did[1]")
                        uid = olddid.find("unitid[1]")
                        title = olddid.find("unittitle[1]")                        
                        olddid.remove(uid)     
                        unitdate = title.find("unitdate[1]")
                        try:
                                title.text = "1. General Files, " + unitdate.text
                        except:
                                unitdate = olddid.find("unitdate[1]")
                                title.text = "1. General Files, " + unitdate.text
                        olddid.insert(1, unitdate)
                        print "inserted series unitdate"
                        extent = olddid.find("physdesc[1]")
                        olddid.remove(extent) 
                        olddid.remove(title)
                        olddid.insert(0, title)
                        print "inserted series title"
                        oldseries.tag = "c02"
                        oldseries.set("level", "series")
                        oldseries.set("id", "series1")
                        oldseries.attrib.pop("otherlevel")
                        parent = oldseries.getparent()
                        parent.remove(oldseries)

                #Add the new processed component and nest the old one within as Series 1

                        newseries = ET.Element("c01")
                        newseries.set("id", serID)
                        print "set newseriesID"
                        newseries.set("level", "otherlevel")
                        newseries.set("otherlevel", "processed")
                        newdid = ET.SubElement(newseries, "did")
                        newtitle = ET.SubElement(newdid, "unittitle")
                        newtitle.text = "Records, "
                        newdid.insert(0, uid)
                        print "added processed id"
                        newdid.insert(3, unitdate)
                        print "added processed date"
                        newdid.insert(4, extent)
                        print "added processed extent"
                        newseries.insert(5, oldseries)
                        print "added records as series1"
                        parent.insert(1, newseries)
                        print "Success! Serialized " + str(file) + "."

                        #Create the arrangement note (unless it already exists)
                        if fa.find("archdesc/arrangement") is None:
                                arrangement = ET.Element("arrangement")
                                arrangement.set("encodinganalog", "351")
                                arrP = ET.SubElement(arrangement, "p")
                                arrP.text = "The collection is organized into the following series:"
                                arrList = ET.SubElement(arrangement, "list")
                                arrList.set("type", "ordered")
                                arrList.set("numeration", "arabic")
                                arrItem = ET.SubElement(arrList, "item")
                                arrRef = ET.SubElement(arrItem, "ref")
                                arrRef.set("target", "series1")
                                arrRef.set("show", "replace")
                                arrRef.set("actuate", "onrequest")
                                arrRef.text = "General Files, " + unitdate.text
                                fa.find("archdesc").insert(3, arrangement)
                        elif fa.find("archdesc/arrangement/list[@type='ordered']") is None:
                                arrangement = fa.find("archdesc/arrangement")
                                arrP = ET.SubElement(arrangement, "p")
                                arrP.text = "The collection is organized into the following series:"
                                arrangement.append(arrP)
                                arrList = ET.SubElement(arrangement, "list")
                                arrList.set("type", "ordered")
                                arrList.set("numeration", "arabic")
                                arrItem = ET.SubElement(arrList, "item")
                                arrRef = ET.SubElement(arrItem, "ref")
                                arrRef.set("target", "series1")
                                arrRef.set("show", "replace")
                                arrRef.set("actuate", "onrequest")
                                arrRef.text = "General Files, " + unitdate.text
                                arrangement.append(arrList)
                        else:
                                print "The arrangement note with series is already there!"
                                
                                

                
        #Don't forget to save your work!
                except Exception, Argument:
                        print "One or more elements in " + str(file) + " is busted, as follows: \n " + str(Argument)
                        continue
                                    
                faString = ET.tostring(fa, pretty_print=True, xml_declaration=False, encoding="utf-8")
                faFile = open(eadFile, "w")
                faFile.write('<?xml version="1.0" encoding="utf-8"?>\n<!-- <!DOCTYPE ead PUBLIC "+//ISBN 1-931666-00-8//DTD ead.dtd (Encoded Archival Description (EAD) Version 2002)//EN" "http://lcweb2.loc.gov/xmlcommon/dtds/ead2002/ead.dtd"  [ <!ENTITY uwmlogo SYSTEM "foo.jpg" NDATA jpeg>] > -->\n'+faString)
                faFile.close()


