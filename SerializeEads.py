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
                
for file in os.listdir(faDir):
        eadFile = os.path.join(faDir, str(file))
        faInput= ET.parse(eadFile, parser)
        fa = faInput.getroot()

        now = datetime.date.today()
        newchange = ET.Element("change")
        newchange.set("encodinganalog","583")
        changedate = ET.SubElement(newchange, "date")
        changedate.set("normal", now.isoformat())
        changedate.text = now.strftime("%B %d, %Y")
        changeitem = ET.SubElement(newchange, "item")
        changeitem.text = "Brad Houston is testing this script."
        fa.find(".//revisiondesc").insert(0,newchange)                

        oldseries = fa.find("archdesc/dsc/c01[1]")
        olddid = oldseries.find("did[1]")
        uid = olddid.find("unitid")
        title = olddid.find("unittitle[1]")
        #olddid.remove(uid)     
        unitdate = title.find("unitdate[1]")
        #title.remove(unitdate)
        extent = olddid.find("physdesc[1]")
        #olddid.remove(extent)
        olddid.remove(title)
        oldtitle = ET.Element("unittitle")
        oldtitle.text = "1. General Files, "
        olddid.insert(1, oldtitle)
        #olddid.insert(2, unitdate)
        oldseries.tag = "c02"
        oldseries.set("level", "series")
        oldseries.set("id", "series1")
        parent = oldseries.getparent()
        parent.remove(oldseries)

        newseries = ET.Element("c01")
        newseries.set("level", "otherlevel")
        newseries.set("otherlevel", "processed")
        newdid = ET.SubElement(newseries, "did")
        newtitle = ET.SubElement(newdid, "unittitle")
        newtitle.text = "Records, "
        #newdid.insert(2, uid)
        #newdid.insert(3, unitdate)
        #newdid.insert(4, extent)
        newdid.insert(5, oldseries)
        parent.insert(1, newseries)

                            
        faString = ET.tostring(fa, pretty_print=True, xml_declaration=True, encoding="utf-8")
        faFile = open(eadFile, "w")
        faFile.write(faString)
        faFile.close()


