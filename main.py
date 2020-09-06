import requests
import getpass
import exceptions
import pprint
import json
from prettytable import PrettyTable
from dearpygui.dearpygui import *
from flask import Flask, render_template, Response, session
from flask import jsonify
from flask import request
import webview
from datetime import datetime
import random
import bakalari

schoolURL = "https://bakalari.gymso.cz/"


#response = requests.post("https://bakalari.gymso.cz/api/login",data={"client_id":"ANDR","grant_type":"password","username":username,"password":password},headers={"Content-Type": "application/x-www-form-urlencoded"})

app = Flask("Bakalari Thing")
app.secret_key = b"_randomThingo"

clients = {}

# Display your index page
@app.route("/")
def index():
    return render_template('index.html', isHeader = False)

@app.route("/login")
def login():
    try:
        sessionClientId = random.randint(10000000,99999999)
        while sessionClientId in clients.keys():
            sessionClientId = random.randint(10000000,99999999)
        session["client"] = sessionClientId
        clients[sessionClientId] = bakalari.Client(schoolURL, request.args.get("username"), request.args.get("password"))
        return jsonify({"response":"success"})
    except exceptions.WrongLogin:
        return jsonify({"response":"error","type":"WrongLogin"})
    #return render_template('test.html')

@app.route("/timetable")
def timetable():
    try:
        now = datetime.now()
        clients[session["client"]].get_timetable(now.isoformat()[:10])
        return render_template('timetable.html', isHeader=True)
    except (AttributeError, KeyError):
        statusCode = Response(status=401)
        return statusCode



@app.route("/loadNewTimetable")
def loadNewTimetable():
    date = request.args.get('date')
    clients[session["client"]].get_timetable(date)
    return jsonify({"result": clients[session["client"]].timetable.htmlTable()})

if __name__ == "__main__":
    app.run()#host='0.0.0.0', port=80)