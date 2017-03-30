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
        if fa.find("archdesc/dsc/c01[@otherlevel='processed']/c02[@level='series']") is None:
                print "Contents List for " + str(file) + " needs to be updated!"
        if not fa.find("archdesc/dsc/c01[@otherlevel='processed']//c06") is None:
                print "Renaming c06"
                for tag in fa:
                        fa = fa.replace(fa.find("c06"), "c07")
        if not fa.find("archdesc/dsc/c01[@otherlevel='processed']//c05") is None:
                print "Renaming c05"
                fa = fa.replace(fa.find("c05"), "c06")
        if not fa.find("archdesc/dsc/c01[@otherlevel='processed']//c04") is None:
                print "Renaming c04"
                fa = fa.replace(fa.find("c04"), "c05")
        if not fa.find("archdesc/dsc/c01[@otherlevel='processed']//c03") is None:
                print "Renaming c03"
                fa = fa.replace(fa.find("c03"), "c04")
        if not fa.find("archdesc/dsc/c01[@otherlevel='processed']//c03") is None:
                print "Renaming c02"
                fa = fa.replace(fa.find("c02"), "c03")
        print "moving the existing contents into a variable"
       
        
        faString = ET.tostring(fa, pretty_print=True, xml_declaration=True, encoding="utf-8")
        faFile = open(eadFile, "w")
        faFile.write(faString)
        faFile.close()


