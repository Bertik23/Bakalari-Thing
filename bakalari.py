import json
import requests
import exceptions

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
        self.marks = json.loads(self.get_resource("api/3/marks").text)

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
    def htmlTable(self):
        fieldnames = [[self.timetable[j][i]["Hour"]["Caption"] for i in range(len(self.timetable[j])) if i != 0] for j in range(len(self.timetable))]
        fieldnames = [f for f in map(deleteDuplicates,fieldnames)]
        longest = 0
        for i, fieldname in enumerate(fieldnames):
            if len(fieldname) > len(fieldnames[longest]):
                longest = i
        #print(fieldnames)
        f = ["Day"]
        f.extend(fieldnames[longest])
        tableHtml = ['<table><tr>']
        tableHtml.extend([f"<th>{i}</th>" for i in f])
        tableHtml.append("</tr>")

        for i, day in enumerate(self.timetable):
            row = [[] for j in range(int(fieldnames[i][-1])+1)]
            row[0] = day[0]
            for hI, h in enumerate(day[1:]):
                #print(int(h["Hour"]["Caption"]), row)
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
                            tableHtml.pop()
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
