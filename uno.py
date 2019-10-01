import pybakalib
import bakalariHandeling as baka
import getpass
from time import time, gmtime
import xml.etree.ElementTree as et
import PySimpleGUI as sg

def get_pmd(next_week = False):
    date = [str(gmtime(time() - time() % 86400)[i]) for i in [0, 1, 2]]
    if next_week:
        date = [str(gmtime(time() - time() % 86400 + 7 * 86400)[i]) for i in [0,1,2]]
    if len(date[1]) == 2:
        pass
    else:
        date[1] = "0" + date[1]
    if len(date[2]) == 2:
        pass
    else:
        date[2] = "0" + date[2]
    nowtime = ""
    for e in date:
        nowtime += e
    return nowtime

def makeText(toText):
    if toText == None:
        return  None
    else:
        return toText.text

def rozvrh_XML_to_class(rozvrh):
    rozvrhTentoTyden = [[],[],[],[],[]]
    dny = rozvrh.find("rozvrh").find("dny").findall("den")
    for den in dny:
        hodiny = den.find("hodiny").findall("hod")
        for hodina in hodiny:
            rozvrhTentoTyden[dny.index(den)].append(Hodina(hodina))
    deleteFirstHour = False
    isZerothHour = True
    for den in rozvrhTentoTyden:
        for hodina in reversed(den):
            if hodina.__str__() == "Volná hodina":
                den.pop(den.index(hodina))
            else:
                break
    try:
        for i in range(2):
            for den in rozvrhTentoTyden:
                for hodina in den:
                    if den.index(hodina) == 0 and hodina.__str__() == "Volná hodina":
                        if deleteFirstHour:
                            den.pop(den.index(hodina))
                    elif den.index(hodina) == 0:
                        raise GetOutOfLoop
            deleteFirstHour = True
            isZerothHour = False
    except GetOutOfLoop:
        pass
    return (rozvrhTentoTyden, isZerothHour)

def get_next_hour(rozvrh):
    global zacatkyHodin
    global konceHodin
    timeNow = gmtime(time()+7*86400)
    if timeNow[6] >= 5 or (timeNow[6] == 4 and timeNow[3] > zacatkyHodin[rozvrh[-1][-1].caption][0] and timeNow[4] > zacatkyHodin[rozvrh[-1][-1].caption][1]):
        return rozvrh_XML_to_class(et.fromstring(client.get_rozvrh(get_pmd(next_week = True))))[0][0][0]
    for hodina in rozvrh[timeNow[6]]:
        if timeNow[3] > zacatkyHodin[hodina.caption][0] and timeNow[4] > zacatkyHodin[hodina.caption][1] and timeNow[3] < konceHodin[hodina.caption][0] and timeNow[4] < konceHodin[hodina.caption][1]:
            if rozvrh[timeNow[6]].index(hodina)+1 <= len(rozvrh[timeNow[6]]):
                return rozvrh[timeNow[6]][rozvrh[timeNow[6]].index(hodina)+1]
        else:
            return rozvrh[timeNow[6]+1][0]


class GetOutOfLoop(Exception):
    pass

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
    def __str__(self):
        if self.pr != None:
            return self.pr
        elif self.nazev != None:
            return  self.nazev
        elif self.typ == "X":
            return "Volná hodina"
    def __repr__(self):
        if self.zkrpr != None:
            return self.zkrpr
        elif self.nazev != None:
            return  self.nazev
        elif self.typ == "X":
            return ""
    def table_look(self):
        pass

url = "https://bakalari.gymso.cz"
if (input("Login? ") == "a"):
    username = input('Username: ')
    password = getpass.getpass('Password: ')
else:
    username = "0306252184"
    password = "3rthmywp"

client = baka.Client() #pybakalib.client.BakaClient(url)
client.set_url(url)
client.login(username, password)

today = gmtime(time())[6]
print(time)
rozvrhTentoTydenXML = client.get_rozvrh(get_pmd(next_week = True)) #get_resource({"pm": "rozvrh", "pdm": time})
print(rozvrhTentoTydenXML)
rozvrhAsi = et.fromstring(rozvrhTentoTydenXML)
#print(type(rozvrhAsi), type(rozvrhTentoTydenXML))
zacatkyHodin = {}
konceHodin = {}
for hodina in rozvrhAsi.find("rozvrh").find("hodiny").findall("hod"):
    zacatkyHodin[hodina.find("caption").text] = [int(i) for i in hodina.find("begintime").text.split(":")]
    konceHodin[hodina.find("caption").text] = [int(i) for i in hodina.find("endtime").text.split(":")]
print(zacatkyHodin)


rozvrh, isZerothHour = rozvrh_XML_to_class(rozvrhAsi)

nextHour = get_next_hour(rozvrh)
print(nextHour)
try:
    nextHourTxt = "Příští hodina je " + nextHour.__str__() + " a je v: " + nextHour.zkrmist + "."
except:
    nextHourTxt = "Hele kámo nemám tušení, kde jsi první hodinu, ale je to: " + nextHour.__str__() + "."

print(nextHourTxt)
rozvrhTentoTydenSTR = [[hodina.__repr__() for hodina in den] for den in rozvrh]

#GUI
maxHours = 0
for den in rozvrhTentoTydenSTR:
    if len(den) > maxHours:
        maxHours = len(den)
hourHeadings = ["Nultá","První","Druhá","Třetí","Čtvrtá","Pátá","Šestá","Sedmá","Osmá","Devátá","Desátá"]
if not isZerothHour:
    firstHeading = 1
else:
    firstHeading = 0
layout = [[sg.Text(nextHourTxt)],[sg.Table(rozvrhTentoTydenSTR, headings=hourHeadings[firstHeading:maxHours+1])]]
window = sg.Window("Rozvrh?", layout=layout, size=(500,500), resizable=True)
while True:
    event, values = window.read()
    if event == None:
        break
window.close()
