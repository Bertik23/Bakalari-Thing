import pybakalib
import getpass
from time import time, gmtime
import xml.etree.ElementTree as et
import PySimpleGUI as sg

def makeText(toText):
    if toText == None:
        return  None
    else:
        return toText.text

class Hodina:
    def __init__(self, xml):
        self.pr = xml.find("pr")
        self.typ = xml.find("typ")
        self.zkrpr = xml.find("zkrpr")
        self.uc = xml.find("uc")
        self.zkruc = xml.find("zkruc")
        self.mist = xml.find("mist")
        self.zkrmist = xml.find("zkrmist")
        self.abs = xml.find("abs")
        self.zkrabs = xml.find("zkrabs")
        self.tema = xml.find("tema")
        self.skup = xml.find("skup")
        self.zkrskup = xml.find("zkrskup")
        self.cycle = xml.find("cycle")
        self.uvol = xml.find("uvol")
        self.chng = xml.find("chng")
        self.caption = xml.find("caption")
        self.notice = xml.find("notice")
        self.nazev = xml.find("nazev")
        self.pr, self.typ, self.zkrpr, self.uc, self.zkruc, self.mist, self.zkrmist, self.abs, self.zkrabs, self.tema, self.skup, self.zkrskup, self.cycle, self.uvol, self.chng, self.caption, self.notice, self.nazev = list(map(makeText, [self.pr, self.typ, self.zkrpr, self.uc, self.zkruc, self.mist, self.zkrmist, self.abs, self.zkrabs, self.tema, self.skup, self.zkrskup, self.cycle, self.uvol, self.chng, self.caption, self.notice, self.nazev]))
        print(self.pr, self.typ, self.zkrpr, self.uc, self.zkruc, self.mist, self.zkrmist, self.abs, self.zkrabs, self.tema, self.skup, self.zkrskup, self.cycle, self.uvol, self.chng, self.caption, self.notice, self.nazev)
    def __str__(self):
        if self.pr != None:
            return self.pr
        elif self.nazev != None:
            return  self.nazev
        elif self.typ == "X":
            return "Volná hodina"
    def __repr__(self):
        return self.__str__()
    def rozvrhView(self):
        if self.zkrpr != None:
            return self.zkrpr
        elif self.nazev != None:
            return  self.nazev
        elif self.typ == "X":
            pass

url = "bakalari.gymso.cz"
if (input("Login? ") == "a"):
    username = input('Username: ')
    password = getpass.getpass('Password: ')
else:
    username = "0306252184"
    password = "3rthmywp"

client = pybakalib.client.BakaClient(url)
client.login(username, password)
#print(client.get_module("znamky"))
#print(client.is_module_available("rozvrh"))
predmety = [p.find("nazev").text for p in et.fromstring(client.get_resource({"pm":"predmety"})).find("predmety").findall("predmet")]
date = [str(gmtime(time() - time() % 86400)[i]) for i in [0, 1, 2]]
today = gmtime(time())[6]
#print(gmtime(time() - time() % 86400 + 7 * 86400))
if len(date[1]) == 2:
    pass
else:
    date[1] = "0" + date[1]
if len(date[2]) == 2:
    pass
else:
    date[2] = "0" + date[2]
time = ""
for e in date:
    time += e
#time = "20190902"
#time = "perm"
#print(time)
rozvrhTentoTydenXML = client.get_resource({"pm": "rozvrh", "pdm": time})
#print(rozvrhTentoTydenXML)
rozvrhAsi = et.fromstring(rozvrhTentoTydenXML)
#print(type(rozvrhAsi), type(rozvrhTentoTydenXML))
rozvrhTentoTyden = [[],[],[],[],[]]
dny = rozvrhAsi.find("rozvrh").find("dny").findall("den")
for den in dny:
    hodiny = den.find("hodiny").findall("hod")
    #print(i.text for i in hodiny)
    #print(hodiny)
    for hodina in hodiny:
        #print(hodina.text)
        rozvrhTentoTyden[dny.index(den)].append(Hodina(hodina))

for den in rozvrhTentoTyden:
    for hodina in den:
        if den.index(hodina) == 0 and hodina.__str__() == "Volná hodina":
            den.pop(den.index(hodina))
    hod = len(den) - 1
    while hod >= 0:
        #print(hod)
        if den[hod].__str__() == "Volná hodina":
            den.pop()
        else:
            break
        hod -= 1
#print(date)
rozvrhDnes = rozvrhTentoTyden[today]
try:
    print("První hodina je " + rozvrhDnes[0].__str__() + " a je v: " + rozvrhDnes[0].zkrmist + ".")
except:
    print("Hele kámo nemám tušení, kde jsi první hodinu, ale je to: " + rozvrhDnes[0].__str__() + ".")

rozvrhTentoTydenSTR = [[hodina.__str__() for hodina in den] for den in rozvrhTentoTyden]
#GUI
table = [["Jedna", "Dva","Tři"],["Čtyři"],["","","Pět","Šest"]]
layout = [[sg.Text("Ahoj")],[sg.Table(rozvrhTentoTydenSTR, headings=["První","Druhá","Třetí","Čtvrtá","Pátá","Šestá","Sedmá"])]]
window = sg.Window("Rozvrh?", layout=layout, size=(500,500), resizable=True)
while True:
    event, values = window.read()
    if event == None:
        break
window.close()


######TO DO:
""" Hodina.rozvrhView"""
