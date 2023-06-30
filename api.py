from flask import Flask
from flask import request, jsonify
import os, tempfile
import signal

app = Flask(__name__)

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
    command = "imapsync "
    options = request.json.get('options')
    if(options != None):
        command += " " + options
    command += f" --host1 {from_host} --user1 {from_user} --password1 '{from_password}'\
                --host2 {to_host} --user2 {to_user} --password2 '{to_password}' --log &"
    os.system(command)
    return jsonify(status = "success", command = command), 200

@app.route('/logs', methods = ['POST'])
def logs():
    from_user = request.json.get('from_user')
    if(from_user == None):
        return jsonify(status = 'error', message= 'from_user required'), 500
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
            fileJson["date"] = fileSplit[2] + '/' + fileSplit[1] + '/' + fileSplit[0]\
                + ' ' + fileSplit[3] + ':'+ fileSplit[4] + ':'+ fileSplit[5]
            fileJson["fromto"] = fileSplit[7] + ' ' + fileSplit[8]
            if fileJson["fromto"] == from_user + ' ' + to_user + '.txt':
                fileIndex = fileIndex + 1
                response.append([fileIndex, fileJson["date"], file])
        return jsonify(status = "success", file_list = response), 200
    except:
        return jsonify(status = "success", file_list = []), 200

# View Log file 
@app.route('/viewlog', methods = ['GET'])
def viewlog():
    try:
        f = open("/var/tmp/uid_0/LOG_imapsync/" + request.args.get('file_name'))
        return jsonify(status = "success", data = f.read()), 200
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
    except:
        return jsonify(status = "success"), 200

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