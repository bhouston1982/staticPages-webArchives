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
        if not fa.find("archdesc/dsc/c01[@otherlevel='processed']") is None:
                print "The EAD for " + str(file) + " already has a processed component."
                
                
        else:
#Update the revisiondesc note
                now = datetime.date.today()
                newchange = ET.Element("change")
                newchange.set("encodinganalog","583")
                changedate = ET.SubElement(newchange, "date")
                changedate.set("normal", now.isoformat())
                changedate.text = now.strftime("%B %d, %Y")
                changeitem = ET.SubElement(newchange, "item")
                changeitem.text = "Brad Houston updated the contents list to add a processed component."
                try:
                        fa.find(".//revisiondesc").insert(0,newchange)
                except:
                        continue
                #Move all components in the processed collection down one level.
                #When I get better at this I will have it automatically count the levels and do that many loops.
                #For now, we're just going to do it this way, through the c06 level.
                print "Adjusting component levels for " + str(file) + "."
                for c01 in fa.find("archdesc/dsc"):
                        for c02 in c01:
                                for c03 in c02:
                                        for c04 in c03:
                                                if c04.tag == "c04":
                                                        c04.tag = "c05"
                                        if c03.tag == "c03":
                                                c03.tag = "c04"
                                if c02.tag == "c02":
                                        c02.tag = "c03"
                        if c01.tag == "c01":
                                c01.tag = "c02"

        #Cleanup the current processed contents list and prep for moving
                try:
                        print "Creating processed component for " + str(file) + "."
                        oldseries = fa.xpath("//dsc")[0]
                        parent = oldseries.getparent()
                        colldate = fa.xpath("//unitdate")[0]
                        uid = str(file)[:9]
                        unitid = fa.xpath("//unitid")[0]
                        extent = fa.xpath("//physdesc")[0]
                        ext = extent.xpath("//extent")[0]
                        ext.attrib.pop("encodinganalog", None)

                        #Uncomment below for debugging
                        #print "successfully extracted processed metadata"

                        #Set the dsc as c01 and clean it up
                        oldseries.remove(oldseries.find("head"))
                        oldseries.tag = "c01"
                        oldseries.set("level", "otherlevel")
                        oldseries.set("id", uid)
                        oldseries.set("otherlevel", "processed")
                        oldseries.attrib.pop("type")
                        #Uncomment below for debugging
                        #print "successfully added c01 attributes"

                        #Add the new elements extracted from the header to a Processed component did
                        newDid= ET.Element("did")
                        newDid.insert(0, unitid)
                        #Uncomment below for debugging
                        #print "successfully added unitid"
                        CollTitle = ET.SubElement(newDid, "unittitle")
                        CollTitle.text = "Records, "
                        #Uncomment below for debugging
                        #print "successfully added title"
                        colldate.attrib.pop("encodinganalog", None)
                        newDid.insert(2, colldate)
                        #Uncomment below for debugging
                        #print "successfully added date"
                        extent.attrib.pop("label", None)
                        newDid.insert(3, extent)
                        #Uncomment below for debugging
                        #print "successfully added extent"
                        
                        #Insert the new did and contents list to the new c01, then create a new dsc and add the new c01
                        oldseries.insert(0, newDid)
                        newDsc = ET.SubElement(parent, "dsc", type="in-depth")
                        newDsc.insert(0, oldseries)
                        for unitid in newDsc.xpath("//unitid[@*]"):
                                unitid.attrib.clear()
                        
                        
                        print "Success! Processed component created for " + str(file) + "."
                        
                        


                
                #Error notification. Unfortunately this doesn't do the traceback so it will be
                #necessary to turn on the debug flags to see where it's screwing up
                        
                except Exception, Argument:
                        print "One or more elements in " + str(file) + " is busted, as follows: \n " + str(Argument)
                        continue

                #Don't forget to save your work!               
                faString = ET.tostring(fa, pretty_print=True, xml_declaration=False, encoding="utf-8")
                faFile = open(eadFile, "w")
                faFile.write('<?xml version="1.0" encoding="utf-8"?>\n<!-- <!DOCTYPE ead PUBLIC "+//ISBN 1-931666-00-8//DTD ead.dtd (Encoded Archival Description (EAD) Version 2002)//EN" "http://lcweb2.loc.gov/xmlcommon/dtds/ead2002/ead.dtd"  [ <!ENTITY uwmlogo SYSTEM "foo.jpg" NDATA jpeg>] > -->\n'+faString)
                faFile.close()


