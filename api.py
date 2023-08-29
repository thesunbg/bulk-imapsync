from flask import Flask
from flask import request, jsonify
from datetime import datetime
import os, tempfile
import signal

app = Flask(__name__)

responseCodes = [
    'EX_OK',
    'EX_USAGE',
    'EX_NOINPUT',
    'EX_UNAVAILABLE',
    'EX_SOFTWARE',
    'EXIT_CATCH_ALL',
    'EXIT_BY_SIGNAL',
    'EXIT_BY_FILE',
    'EXIT_PID_FILE_ERROR',
    'EXIT_CONNECTION_FAILURE',
    'EXIT_TLS_FAILURE',
    'EXIT_AUTHENTICATION_FAILURE',
    'EXIT_SUBFOLDER1_NO_EXISTS',
    'EXIT_WITH_ERRORS',
    'EXIT_WITH_ERRORS_MAX',
    'EXIT_OVERQUOTA',
    'EXIT_ERR_APPEND',
    'EXIT_ERR_FETCH',
    'EXIT_ERR_CREATE',
    'EXIT_ERR_SELECT',
    'EXIT_TRANSFER_EXCEEDED',
    'EXIT_ERR_APPEND_VIRUS',
    'EXIT_TESTS_FAILED',
    'EXIT_CONNECTION_FAILURE_HOST1',
    'EXIT_CONNECTION_FAILURE_HOST2',
    'EXIT_AUTHENTICATION_FAILURE_USER1',
    'EXIT_AUTHENTICATION_FAILURE_USER2',
]

# Imap Sync 
@app.route('/sync', methods = ['POST'])
def sync():
    from_host = request.json.get('from_host')
    if(from_host == None):
        return jsonify(status = 'error', message= 'from_host required'), 500
    from_user = request.json.get('from_user')
    if(from_user == None):
        return jsonify(status = 'error', message= 'from_user required'), 500
    from_password = request.json.get('from_password')
    if(from_password == None):
        return jsonify(status = 'error', message= 'from_password required'), 500

    to_host = request.json.get('to_host')
    if(to_host == None):
        return jsonify(status = 'error', message= 'to_host required'), 500
    to_user = request.json.get('to_user')
    if(to_user == None):
        return jsonify(status = 'error', message= 'to_user required'), 500
    to_password = request.json.get('to_password')
    if(to_password == None):
        return jsonify(status = 'error', message= 'to_password required'), 500
    now = datetime.now()
    logfile = 'sync_' + now.strftime("%-m%d%Y%H%M%S") + '_' + from_host + '_' + from_user + '_' + to_host + '_' + to_user + '.txt'
    command = "imapsync "
    options = request.json.get('options')
    if(options != None):
        command += " " + options
    command += f" --host1 {from_host} --user1 {from_user} --password1 '{from_password}'\
                --host2 {to_host} --user2 {to_user} --password2 '{to_password}' --log --logfile {logfile} &"
    os.system(command)
    return jsonify(status = "success", command = command), 200

# Imap Sync 
@app.route('/checklogin', methods = ['POST'])
def checklogin():
    from_host = request.json.get('from_host')
    if(from_host == None):
        return jsonify(status = 'error', message= 'from_host required'), 500
    from_user = request.json.get('from_user')
    if(from_user == None):
        return jsonify(status = 'error', message= 'from_user required'), 500
    from_password = request.json.get('from_password')
    if(from_password == None):
        return jsonify(status = 'error', message= 'from_password required'), 500

    to_host = request.json.get('to_host')
    if(to_host == None):
        return jsonify(status = 'error', message= 'to_host required'), 500
    to_user = request.json.get('to_user')
    if(to_user == None):
        return jsonify(status = 'error', message= 'to_user required'), 500
    to_password = request.json.get('to_password')
    if(to_password == None):
        return jsonify(status = 'error', message= 'to_password required'), 500
    now = datetime.now()
    logfile = 'checklogin_' + now.strftime("%-m%d%Y%H%M%S") + '_' + from_host + '_' + from_user + '_' + to_host + '_' + to_user + '.txt'
    command = "imapsync "
    command += f" --host1 {from_host} --user1 {from_user} --password1 '{from_password}'\
                --host2 {to_host} --user2 {to_user} --password2 '{to_password}' --log --logfile {logfile} --justlogin &"
    os.system(command)
    return jsonify(status = "success", command = command), 200

@app.route('/logs', methods = ['POST'])
def logs():
    from_host = request.json.get('from_host')
    if(from_host == None):
        return jsonify(status = 'error', message= 'from_host required'), 500
    from_user = request.json.get('from_user')
    if(from_user == None):
        return jsonify(status = 'error', message= 'from_user required'), 500
    to_host = request.json.get('to_host')
    if(to_host == None):
        return jsonify(status = 'error', message= 'to_host required'), 500
    to_user = request.json.get('to_user')
    if(to_user == None):
        return jsonify(status = 'error', message= 'to_user required'), 500
    try:
        file_list = os.listdir("/var/tmp/uid_0/LOG_imapsync/")
        response = []
        fileJson = {}
        fileIndex = 0
        for file in file_list:
            fileSplit = file.split('_')
            fileJson["date"] = fileSplit[1]
            fileJson["fromto"] = fileSplit[2] + '_' + fileSplit[3] + '_' + fileSplit[4] + '_' + fileSplit[5]
            if fileJson["fromto"] == from_host + '_' + from_user + '_' + to_host + '_' + to_user + '.txt':
                fileIndex = fileIndex + 1
                response.append([fileIndex, fileJson["date"], file])
        return jsonify(status = "success", file_list = response), 200
    except:
        return jsonify(status = "success", file_list = []), 200

# Logs file of a domain and response code
@app.route('/logstohostwithresponsecode', methods = ['POST'])
def logswithresponsecode():
    to_host = request.json.get('to_host')
    if(to_host == None):
        return jsonify(status = 'error', message= 'to_host required'), 500
    try:
        file_list = os.listdir("/var/tmp/uid_0/LOG_imapsync/")
        response = []
        fileJson = {}
        fileIndex = 0
        for file in file_list:
            fileSplit = file.split('_')
            if fileSplit[4] == to_host:
                fileIndex = fileIndex + 1
                try:
                    data = open("/var/tmp/uid_0/LOG_imapsync/" + file).read()
                    for code in responseCodes:
                        if(code in data):
                            fileJson['responseCode'] = code
                except:
                    fileJson['responseCode'] = 'READ_ERR'
                response.append([fileIndex, fileJson["date"], file, fileJson['responseCode']])
        return jsonify(status = "success", file_list = response), 200
    except:
        return jsonify(status = "success", file_list = []), 200

# View Log file 
@app.route('/viewlog', methods = ['GET'])
def viewlog():
    try:
        data = open("/var/tmp/uid_0/LOG_imapsync/" + request.args.get('file_name')).read()
        responseCode = ''
        for code in responseCodes:
            if(code in data):
                responseCode = code
        return jsonify(status = "success", data = data, responseCode= responseCode), 200
    except:
        return jsonify(status = "success", data = ''), 200

# Delete Log 
@app.route('/deletelog', methods = ['DELETE'])
def deletelog():
    try:
        os.remove("/var/tmp/uid_0/LOG_imapsync/" + request.args.get('file_name'))
        return jsonify(status = "success"), 200
    except:
        return jsonify(status = "success"), 200

# Total logs file
@app.route('/totallogs', methods = ['GET'])
def totallogs():
    try:
        file_list = os.listdir("/var/tmp/uid_0/LOG_imapsync/")
        return jsonify(status = "success", totalFiles = len(file_list)), 200
    except:
        return jsonify(status = "success", totalFiles = 0), 200

# Delete all logs 
@app.route('/deletealllogs', methods = ['DELETE'])
def deletealllogs():
    try:
        file_list = os.listdir("/var/tmp/uid_0/LOG_imapsync/")
        for file in file_list:
            os.remove("/var/tmp/uid_0/LOG_imapsync/" + file)
        return jsonify(status = "success"), 200
    except:
        return jsonify(status = "success"), 200

#view all imapsync process
@app.route('/imapsyncprocess', methods = ['GET'])
def imapsyncprocess():
    try:
        data = readcmd('ps -ef | grep imapsync')
        if(request.args.get('type') == 'json'):
            lines = data.split('\n')
            del lines[-1]  
            return jsonify(status = "success", data = lines, total = len(lines)), 200             
        return jsonify(status = "success", data = data), 200
    except:
        return jsonify(status = "success"), 200

#Kill imapsync process
@app.route('/killimapsyncprocess', methods = ['POST'])
def killimapsyncprocess():
    process_id = request.json.get('process_id')
    if(process_id == None):
        return jsonify(status = 'error', message= 'process_id required'), 500
    try:
        os.kill(process_id, signal.SIGTERM)
        # os.system('kill -9 ' + process_id + ' && ps -ef | grep imapsync')
        return jsonify(status = "success", message = "killed"), 200
    except Exception as e:
        return jsonify(status = "error", message = e), 200

def readcmd(cmd):
    ftmp = tempfile.NamedTemporaryFile(suffix='.out', prefix='tmp', delete=False)
    fpath = ftmp.name
    if os.name=="nt":
        fpath = fpath.replace("/","\\") # forwin
    ftmp.close()
    os.system(cmd + " > " + fpath)
    data = ""
    with open(fpath, 'r') as file:
        data = file.read()
        file.close()
    os.remove(fpath)
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0")