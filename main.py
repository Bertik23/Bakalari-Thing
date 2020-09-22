import requests
import getpass
import exceptions
import pprint
import json
from flask import Flask, render_template, Response, session, abort
from flask import jsonify
from flask import request
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
    except requests.exceptions.ConnectionError:
        return jsonify({"response":"error","type":"NoConnection","message":"The server has no internet connection."})

@app.route("/timetable")
def timetable():
    try:
        now = datetime.now()
        clients[session["client"]].get_timetable(now.isoformat()[:10])
        return render_template('timetable.html', isHeader=True)
    except (AttributeError, KeyError):
        #statusCode = Response(status=401)
        #return statusCode
        abort(401)

@app.route("/marks")
def marks():
    try:
        clients[session["client"]].get_marks()
        return render_template('marks.html', isHeader=True)
    except (AttributeError, KeyError):
        #statusCode = Response(status=401)
        #return statusCode
        abort(401)

@app.route("/test")
def test():
    return render_template('test.html')


@app.route("/about")
def about():
    return render_template('about.html', isHeader=True)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404

app.register_error_handler(404, page_not_found)

@app.errorhandler(401)
def unauthorized(e):
    # note that we set the 404 status explicitly
    #return render_template('errors/401.html'), 401
    return Response(render_template("errors/401.html"), 401, {'WWW-Authenticate':'NotBasic realm="Login Required"'})

app.register_error_handler(401, unauthorized)


@app.route("/loadNewTimetable")
def loadNewTimetable():
    date = request.args.get('date')
    clients[session["client"]].get_timetable(date)
    return jsonify({"result": clients[session["client"]].timetable.htmlTable()})

@app.route("/getMarks")
def getMarks():
    htmlMarks = clients[session["client"]].htmlMarks()
    return jsonify({"result": htmlMarks})

@app.route("/getRecievedMessages")
def getRecievedMessages():
    clients[session["client"]].get_recievedMessages()
    return jsonify({"result": clients[session["client"]].recievedMessages})

if __name__ == "__main__":
    app.run()