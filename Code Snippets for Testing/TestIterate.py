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
    eadFile = os.path.join(faDir, file)
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

    faString = ET.tostring(fa, pretty_print=True, xml_declaration=True, encoding="utf-8")
    faFile = open(eadFile, "w")
    faFile.write(faString)
    faFile.close()
