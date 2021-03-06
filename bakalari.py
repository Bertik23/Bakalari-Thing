import json
import requests
import exceptions
import datetime
import pprint

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
        tableHtml = ["<table>"]
        for subject in self.marks["Subjects"]:
            tableHtml.extend(["<tr><td><table class=withoutOuterBorder><tr><td>",subject["Subject"]["Name"],"</td></tr><tr><td>Průměr:",subject["AverageText"] ,"</td></tr></table></td>"])
            for mark in subject["Marks"]:
                tableHtml.extend(["<td>",mark["MarkText"],"</td>"])
            tableHtml.extend(["</tr>"])
        tableHtml.append("</table>")

        return "".join(tableHtml)

    def get_recievedMessages(self):
        self.recievedMessages = []
        messages = json.loads(self.get_resource("api/3/komens/messages/received", method="post").text)["Messages"]
        for m in messages:
            self.recievedMessages.append(Message(m))

    def recievedMessagesHTML(self):
        s = "<table>"
        for m in self.recievedMessages:
            s += f'<tr title="Send {m.time}"><td>{m.relevant}</td><td>{m.text}</td><tr>'
        return s

    def get_substitutions(self):
        substitutions = json.loads(self.get_resource("api/3/substitutions").text)

        self.substitutions = []

        for substitution in substitutions["Changes"]:
            self.substitutions.append([datetime.date.fromisoformat(substitution["Day"][:10]).weekday()+1, substitution["Hours"], substitution["Description"]])

    def substitutionsHtml(self):
        subsHtml = "<table>"

        for i in self.substitutions:
            subsHtml += "<tr><td>"
            subsHtml += "</td><td>".join(map(str,i))
            subsHtml += "</td></tr>"

        subsHtml += "</table>"

        return subsHtml

    def get_timetable(self,date):
        t = json.loads(self.get_resource("api/3/timetable/actual",params={"date":date}).text)
        self.timetable = Timetable(t)
        self.timetable.pairThings()
    def login(self, username, password):
        response = requests.post(f"{self.schoolURL}api/login",data={"client_id":"ANDR","grant_type":"password","username":username,"password":password},headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            access_token = response.json()["access_token"]
            refresh_token = response.json()["refresh_token"]
        except KeyError:
            raise exceptions.WrongLogin("Špatné jméno nebo heslo")
        return access_token, refresh_token

    def get_resource(self,url,method="get",**kwargs):
        return requests.request(method, self.schoolURL+url,**kwargs, headers={"Authorization" : f"Bearer {self.access_token}"})

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
            try:
                row = [[] for j in range(int(fieldnames[i][-1])+1)]
                row[0] = "Po" if day[0] == 1 else "Út" if day[0] == 2 else "St" if day[0] == 3 else "Čt" if day[0] == 4 else "Pá" if day[0] == 5 else "Nic"
                for hI, h in enumerate(day[1:]):
                    #print(int(h["Hour"]["Caption"]), row)
                    row[int(h["Hour"]["Caption"])].extend([h["Subject"]["Name"] if h["Subject"] is not None else "", h["Teacher"]["Name"] if h["Teacher"] is not None else "", h["Room"]["Abbrev"] if h["Room"] is not None else ""])
                print(row)

                tableHtml.append(f'<tr class="day{day[0]}">')
                for r in row:
                    if type(r) == str:
                        tableHtml.append(f"<td>{r}</td>")
                        continue

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
                        tableHtml.pop()
                        tableHtml.append('<td class="day">')
                        tableHtml.append(r)
                        #print(e)

                    tableHtml.append("</td>")
                    
                tableHtml.append("</tr>")
            except:
                pass

        tableHtml.append("</table>")

        html = "".join(map(str,tableHtml))
        return html

class Message:
    def __init__(self, message):
        self.relevant = message["RelevantName"]
        self.text = message["Text"]
        self.time = message["SentDate"]
    def __str__(self):
        return f"{self.time} > {self.relevant}: {self.text}"
    def __repr__(self):
        return f"Message from {self.relevant}"
