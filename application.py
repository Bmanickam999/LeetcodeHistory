from configparser import ConfigParser
from flask import Flask
from flask import render_template
from flask import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import json

from dataProxy import DataProxy
from leetcode import Contest

app = Flask(__name__)
auth = HTTPBasicAuth()
config = ConfigParser()
config.read('config.ini')
dataProxy = DataProxy(config)

users = {
    config['WebApp']['AdminUsername']: generate_password_hash(config['WebApp']['AdminPassword']),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/addContest')
@auth.login_required
def addContest():
    contestType = request.args.get('type', default = 'standard', type = str)
    contestId = request.args.get('id', type = int)

    if (contestType == None or contestId == None):
        return "Errors in GET arguments. Required: 'type' and 'id'"

    res = False

    if contestType == 'standard':
        res = dataProxy.pushContest(Contest.STANDARD, contestId)
    elif contestType == 'biweekly':
        res = dataProxy.pushContest(Contest.BIWEEKLY, contestId)

    return "Function executed: " + str(res)

@app.route('/getUser')
@auth.login_required
def getUser():
    username = request.args.get('username', type = str)

    if (username == None):
        "Errors in GET arguments. Required: 'username'"

    userRanks = dataProxy.getUser(username)
    result = {}
    result['ranks'] = []
    for rank in  userRanks:
        result['ranks'].append(json.loads(rank.decode()))

    return json.dumps(result)

@app.route('/')
@auth.login_required
def root():
    return app.send_static_file('index.html')

@app.route('/test')
@auth.login_required
def test():
    username = request.args.get('username', type = str)

    if (username == None):
        return "Errors in GET arguments. Required: 'username'"

    userRanks = dataProxy.getUser(username)
    result = {}
    result['ranks'] = []
    for rank in  userRanks:
        result['ranks'].append(json.loads(rank.decode()))
    jsonData = json.dumps(result)

    return render_template('test.html', result = jsonData)
