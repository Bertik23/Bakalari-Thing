import requests
import getpass
import exceptions
import pprint
import json
from prettytable import PrettyTable
from dearpygui.dearpygui import *
import webview

username = input("Username: ")
password = getpass.getpass("Password: ")

schoolURL = "https://bakalari.gymso.cz/"

def deleteDuplicates(l):
    l2 = []
    for i in l:
        if i not in l2:
            l2.append(i)
    return l2

class Client:
    def __init__(self,schoolURL, username, password):
        self.schoolURL = schoolURL
        self.access_token, self.refresh_token = self.login(username, password)
    def get_marks(self):
        self.marks = json.loads(client.get_resource("api/3/marks").text)

    def htmlMarks(self):
        tableHtml = ["<h1>Marks<h1><table>"]
        for subject in self.marks["Subjects"]:
            tableHtml.extend(["<tr><td><table class=withoutOuterBorder><tr><td>",subject["Subject"]["Name"],"</td></tr><tr><td>Průměr:",subject["AverageText"] ,"</td></tr></table></td>"])
            for mark in subject["Marks"]:
                tableHtml.extend(["<td>",mark["MarkText"],"</td>"])
            tableHtml.extend(["</tr>"])
        tableHtml.append("</table>")

        return "".join(tableHtml)

    def get_timetable(self,date):
        t = json.loads(self.get_resource("api/3/timetable/actual",params={"date":date}).text)
        self.timetable = Timetable(t)
        self.timetable.pairThings()
    def login(self, username, password):
        response = requests.post("https://bakalari.gymso.cz/api/login",data={"client_id":"ANDR","grant_type":"password","username":username,"password":password},headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            access_token = response.json()["access_token"]
            refresh_token = response.json()["refresh_token"]
        except KeyError:
            raise exceptions.WrongLogin("Špatné jméno nebo heslo")
        return access_token, refresh_token

    def get_resource(self,url,method="get",**kwargs):
        return requests.request(method, schoolURL+url,**kwargs, headers={"Authorization" : f"Bearer {self.access_token}"})

class Timetable:
    def __init__(self, timetable):
        self.hours = timetable["Hours"]
        self.rooms = timetable["Rooms"]
        self.days = timetable["Days"]
        self.groups = timetable["Groups"]
        self.teachers = timetable["Teachers"]
        self.subjects = timetable["Subjects"]
    def pairThings(self):
        self.timetable = []
        for dayI, day in enumerate(self.days):
            self.timetable.append([day["DayOfWeek"]])
            for hour in day["Atoms"]:
                b = True
                #print(hour["Change"]["ChangeType"])
                h = {"Hour": None,
                    "Subject": None,
                    "Teacher": None,
                    "Room": None,
                    "Change": hour["Change"]
                    }
                for _h in self.hours:
                    if _h["Id"] == hour["HourId"]:
                        h["Hour"] = _h
                for _s in self.subjects:
                    if _s["Id"] == hour["SubjectId"]:
                        #if _s["Name"] == "Aplikovaná fyzika": b = False
                        h["Subject"] = _s
                for _t in self.teachers:
                    if _t["Id"] == hour["TeacherId"]:
                        h["Teacher"] = _t
                for _r in self.rooms:
                    if _r["Id"] == hour["RoomId"]:
                        h["Room"] = _r
                
                if b:
                    self.timetable[dayI].append(h)
    def prettyTimetable(self):
        table = PrettyTable()
        fieldnames = [[self.timetable[j][i]["Hour"]["Caption"] for i in range(len(self.timetable[j])) if i != 0] for j in range(len(self.timetable))]
        fieldnames = [f for f in map(deleteDuplicates,fieldnames)]
        longest = 0
        for i, fieldname in enumerate(fieldnames):
            if len(fieldname) > len(fieldnames[longest]):
                longest = i
        f = ["Day"]
        f.extend(fieldnames[longest])
        print(f)
        table.fieldnames = f#["Day","1.","2.","3.","4.","5.","6.","7.","8.","9."]
        for i, day in enumerate(self.timetable):
            row = [f"{day[0]}\n\n---"]
            row.extend([f'{day[j]["Subject"]["Name"]}\n{day[j]["Teacher"]["Name"]}\n---' if day[j]["Subject"] is not None else "Nic\n\n---" for j in range(len(day)) if j != 0])
            for a in range(len(table.fieldnames)-len(row)):
                row.append("Nic\n\n---")
            if len(row)>len(table.fieldnames):
                row = row[:len(table.fieldnames)]
            
            table.add_row(row)
        print("===================")
        return str(table)
    def dearTable(self):
        fieldnames = [[self.timetable[j][i]["Hour"]["Caption"] for i in range(len(self.timetable[j])) if i != 0] for j in range(len(self.timetable))]
        fieldnames = [f for f in map(deleteDuplicates,fieldnames)]
        longest = 0
        for i, fieldname in enumerate(fieldnames):
            if len(fieldname) > len(fieldnames[longest]):
                longest = i
        f = ["Day"]
        f.extend(fieldnames[longest])
        add_table("Timetable", f)
        for i, day in enumerate(self.timetable):
            row = [f"{day[0]}"]
            row.extend([f'{day[j]["Subject"]["Name"]}\n{day[j]["Teacher"]["Name"]}' if day[j]["Subject"] is not None else "Nic" for j in range(len(day)) if j != 0])
            for a in range(len(f)-len(row)):
                row.append("Nic")
            if len(row)>len(f):
                row = row[:len(f)]
            add_row("Timetable", row)
    def htmlTable(self):
        fieldnames = [[self.timetable[j][i]["Hour"]["Caption"] for i in range(len(self.timetable[j])) if i != 0] for j in range(len(self.timetable))]
        fieldnames = [f for f in map(deleteDuplicates,fieldnames)]
        longest = 0
        for i, fieldname in enumerate(fieldnames):
            if len(fieldname) > len(fieldnames[longest]):
                longest = i
        f = ["Day"]
        f.extend(fieldnames[longest])
        tableHtml = ['<h1>Timetable<h1><table><tr>']
        tableHtml.extend([f"<th>{i}</th>" for i in f])
        tableHtml.append("</tr>")

        for i, day in enumerate(self.timetable):
            row = [[] for j in range(len(day))]
            row[0] = day[0]
            for hI, h in enumerate(day[1:]):
                row[int(h["Hour"]["Caption"])].extend([h["Subject"]["Name"] if h["Subject"] is not None else "", h["Teacher"]["Name"] if h["Teacher"] is not None else "", h["Room"]["Abbrev"] if h["Room"] is not None else ""])
            #print(row)

            tableHtml.append("<tr>")
            for r in row:

                tableHtml.append("<td>")
                try:
                    tableHtml.append('<table class="hour withoutOuterBorder">')
                    for r_ in r:
                        if r_ == "":
                            continue
                        tableHtml.append("<tr><td>")
                        tableHtml.append(r_)
                        tableHtml.append("</td></tr>")
                    tableHtml.append("</table>")
                    # if "".join(tableHtml[-((len(r)*3)+2):]) == f"<table>{'<tr><td></td></tr>'*len(r)}</table>":
                    #     print("ahoj")
                    #     for _ in range(len(r)*3+2):
                    #         print(tableHtml.pop())
                    #         #tableHtml.append("")
                    if "".join(tableHtml[-2:]) == "<table class=hour withoutOuterBorder></table>":
                        #print("ahoj")
                        for _ in range(2):
                            print(tableHtml.pop())
                            #tableHtml.append("")
                except Exception as e:
                    tableHtml.pop()
                    tableHtml.append(r)
                    #print(e)

                tableHtml.append("</td>")
                
            tableHtml.append("</tr>")

        tableHtml.append("</table>")

        html = "".join(map(str,tableHtml))
        return html

#response = requests.post("https://bakalari.gymso.cz/api/login",data={"client_id":"ANDR","grant_type":"password","username":username,"password":password},headers={"Content-Type": "application/x-www-form-urlencoded"})

client = Client(schoolURL, username, password)

client.get_timetable("2020-09-08")
#print(client.timetable.prettyTimetable())
#print(client.get_resource("api/3/user").text)
# client.timetable.dearTable()


# add_additional_font("D:\\Python\\bakalari-thing\\Roboto-Medium.ttf",custom_glyph_ranges=[[0x0100, 0x017f], [0x0180, 0x024F]])
# start_dearpygui()

marks = json.loads(client.get_resource("api/3/marks").text)
client.get_marks()

def makeHtml():
    html = """
    <html lang="cz">
    <meta charset="UTF-8">
    <head>
    <link rel="stylesheet" href="style.css">
    </head>
    <style>
    """
    with open("style.css","r") as f:
        html += f.read()

    html += """</style>
    <script>
    window.addEventListener('pywebviewready', function(){})
    function loadNewTimetable(){
        document.getElementById("click").innerText = "Ahoooj"
        pywebview.api.loadNewTimetable(document.getElementById("timetableDate").value)
        //document.getElementById("click").innerText = "Ahooojda"
    }
    function showResponse(response) {
        var container = document.getElementById('click')

        container.innerText = response.message
        container.style.display = 'block'
    }
    </script>
    <body>
    <div id=click></div>
    <input type="date" id="timetableDate"><button onclick="loadNewTimetable()">Load</button>"""

    html += client.timetable.htmlTable()
    html += "<br><br>"
    html += client.htmlMarks()
    html += "</body></html>"
    return html

class Api:
    def loadNewTimetable(self,date):
        print(date)
        client.get_timetable(date)
        window.load_html(makeHtml())
        #return date

with open("test.html","w") as f:
    f.write(makeHtml())

if True:
    api = Api()
    window = webview.create_window("Rozvrh", html=makeHtml(), js_api=api)
    #webview.create_window("Test", html="<h1>Ahoj!<h1>")
    #print(makeHtml())
    webview.start(debug=True)