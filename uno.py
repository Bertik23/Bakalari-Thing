import pybakalib
import getpass
from time import time, gmtime
import xml.etree.ElementTree as et

url = "bakalari.gymso.cz"
if (input("Login? ") == "a"):
    username = input('Username: ')
    password = getpass.getpass('Password: ')
else:
    username = ""
    password = ""

client = pybakalib.client.BakaClient(url)
client.login(username, password)
#print(client.get_module("znamky"))
#print(client.is_module_available("rozvrh"))
predmety = [p.find("nazev").text for p in et.fromstring(client.get_resource({"pm":"predmety"})).find("predmety").findall("predmet")]
date = [str(gmtime(time() - time() % 86400)[i]) for i in [0, 1, 2]]
today = gmtime(time() - time() % 86400)[6]
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
        if hodina.find("pr") != None:
            rozvrhTentoTyden[dny.index(den)].append(hodina)#.find("pr"))
        elif hodina.find("nazev") != None:
            rozvrhTentoTyden[dny.index(den)].append(hodina.find("nazev").text)
        elif hodina.find("typ").text == "X":
            rozvrhTentoTyden[dny.index(den)].append("Volná hodina")

for den in rozvrhTentoTyden:
    for hodina in den:
        if den.index(hodina) == 0 and hodina == "Volná hodina":
            den.pop(den.index(hodina))
    hod = len(den) - 1
    while hod >= 0:
        #print(hod)
        if den[hod] == "Volná hodina":
            den.pop()
        else:
            break
        hod -= 1
#print(date)
rozvrhDnes = rozvrhTentoTyden[today]
try:
    print("První hodina je " + rozvrhDnes[0].find("pr").text + " a je v: " + rozvrhDnes[0].find("zkrmist").text + ".")
except:
    print("Hele kámo nemám tušení, kde jsi první hodinu, ale je to: " + rozvrhDnes[0] + ".")
