import bakalari
import pprint
import json
import datetime

def getSubstitutions(self):
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