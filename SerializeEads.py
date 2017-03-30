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

#Update the revisiondesc note
        now = datetime.date.today()
        newchange = ET.Element("change")
        newchange.set("encodinganalog","583")
        changedate = ET.SubElement(newchange, "date")
        changedate.set("normal", now.isoformat())
        changedate.text = now.strftime("%B %d, %Y")
        changeitem = ET.SubElement(newchange, "item")
        changeitem.text = "Brad Houston is testing this script."
        fa.find(".//revisiondesc").insert(0,newchange)

        #Move all components in the processed collection down one level.
        #When I get better at this I will have it automatically count the levels and do that many loops.
        #For now, we're just going to do it this way, through the c06 level.
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

        oldseries = fa.find("archdesc/dsc/c01[1]")
        olddid = oldseries.find("did[1]")
        uid = olddid.find("unitid[1]")
        title = olddid.find("unittitle[1]")
        #olddid.remove(uid)     [not working yet]
        unitdate = olddid.find("unitdate[1]")
        extent = olddid.find("physdesc[1]")
        #olddid.remove(extent) [not working yet]
        olddid.remove(title)
        oldtitle = ET.Element("unittitle")
        oldtitle.text = "1. General Files, "
        olddid.insert(1, oldtitle)
        oldseries.tag = "c02"
        oldseries.set("level", "series")
        oldseries.set("id", "series1")
        parent = oldseries.getparent()
        parent.remove(oldseries)

#Add the new processed component and nest the old one within as Series 1

        newseries = ET.Element("c01")
        newseries.set("level", "otherlevel")
        newseries.set("otherlevel", "processed")
        newdid = ET.SubElement(newseries, "did")
        newtitle = ET.SubElement(newdid, "unittitle")
        newtitle.text = "Records, "
        #newdid.insert(2, uid) [Not working yet]
        #newdid.insert(3, unitdate) [Not Working yet]
        #newdid.insert(4, extent) [Not Working yet]
        newseries.insert(5, oldseries)
        parent.insert(1, newseries)

        
#Don't forget to save your work!
                            
        faString = ET.tostring(fa, pretty_print=True, xml_declaration=True, encoding="utf-8")
        faFile = open(eadFile, "w")
        faFile.write(faString)
        faFile.close()


