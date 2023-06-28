import pandas as pd
import os, tempfile
import colorama
import textwrap
import pyfiglet
from tabulate import tabulate

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


def read_excel(type):
    try:
        df=pd.read_excel('working.xlsx')
        accounts = df.to_dict(orient='records')
        if type == 'showaccounts':
            show_accounts(accounts)
        if type == 'checklogin':
            checklogin(accounts)
        if type == 'sync':
            sync(accounts)
        if type == 'showlogs':
            show_logs(accounts)
    except Exception as e:
        print(f"Error: {e}")
        return read_excel(type)

def show_accounts(accounts):
    response = []
    response.append(["Index", "From", "To"])
    index = 0
    print(f"Total accounts: {len(accounts)}")
    for account in accounts:
        index = index + 1
        response.append([index, account["from_user"], account["to_user"]])
    print(colorama.Fore.LIGHTYELLOW_EX)
    print(tabulate(response))
    print(colorama.Fore.RESET)

def checklogin(accounts):
    response = []
    response.append(["Index", "From", "To", "Status", 'Message'])
    index = 0
    print(f"Total accounts: {len(accounts)}")
    for account in accounts:
        try:
            index = index + 1
            print(f"Checking {account['from_user']} -> {account['to_user']} ...")
            result = readcmd(f"imapsync --host1 {account['from_host']} --user1 {account['from_user']} --password1 {account['from_password']}\
                --host2 {account['to_host']} --user2 {account['to_user']} --password2 {account['to_password']} --justlogin")
            error_message = []
            for line in result.split('\n'): 
                if "Exiting with return value 0" in line:
                    response.append([index, account["from_user"], account["to_user"], "success", ""])
                    break
                elif ": Host1 failure:" in line:
                    error_message.append(line)
                elif ": Host2 failure:" in line:
                    error_message.append(line)
            if len(error_message) > 0:
                response.append([index, account["from_user"], account["to_user"], "error", '\n'.join(textwrap.wrap('\n'.join(error_message)))])
        except Exception as e:
            response.append([index, account["from_user"], account["to_user"], "error", e])
    print(colorama.Fore.LIGHTYELLOW_EX)
    print(tabulate(response))
    print(colorama.Fore.RESET)

def sync(accounts):
    response = []
    response.append(["Index", "From", "To", "Status", 'Message'])
    index = 0
    try:
        fromIndex = int(input("Sync from index: "))
        toIndex = int(input("Sync to index: "))
        if fromIndex < index + 1 and fromIndex > len(accounts):
            print(f'Index from {index + 1} to {len(accounts)}')
            return False
        if toIndex < index + 1 and toIndex > len(accounts):
            print(f'Index from {index + 1} to {len(accounts)}')
            return False
    except:
        print('Input not correct')
        return False
    print(f"Total accounts: {len(accounts)}")
    for account in accounts:
        try:
            index = index + 1
            if fromIndex > index or toIndex < index:
                continue;
            print(f"Syncing {account['from_user']} -> {account['to_user']} ...")
            print(f"imapsync --host1 {account['from_host']} --user1 {account['from_user']} --password1 '{account['from_password']}'\
                --host2 {account['to_host']} --user2 {account['to_user']} --password2 '{account['to_password']}'")
            os.system(f"imapsync --host1 {account['from_host']} --user1 {account['from_user']} --password1 '{account['from_password']}'\
                --host2 {account['to_host']} --user2 {account['to_user']} --password2 '{account['to_password']}'")
            # error_message = []
            # for line in result.split('\n'): 
            #     if ": Host1 failure:" in line:
            #         error_message.append(line)
            #     elif ": Host2 failure:" in line:
            #         error_message.append(line)
            # if len(error_message) > 0:
            #     response.append([index, account["from_user"], account["to_user"], "error", '\n'.join(textwrap.wrap('\n'.join(error_message)))])
            # else:
            #     response.append([index, account["from_user"], account["to_user"], "success", ""])
        except Exception as e:
            response.append([index, account["from_user"], account["to_user"], "error", e])
    print(colorama.Fore.LIGHTYELLOW_EX)
    print(tabulate(response))
    print(colorama.Fore.RESET)

def show_logs(accounts):
    try:
        index = 0
        logIndex = int(input("Input index to show logs: "))
        if logIndex < index + 1 and logIndex > len(accounts):
            print(f'Index from {index + 1} to {len(accounts)}')
            return False
    except:
        print('Input not correct')
        return False

    for account in accounts:
        try:
            index = index + 1
            if logIndex != index:
                continue
            while(True):
                print(f"Show log file {account['from_user']} -> {account['to_user']} ...")
                file_list = os.listdir("LOG_imapsync")
                fileJson = {}
                response = []
                response.append(["Index", "Date", "File Name"])
                fileIndex = 0
                for file in file_list:
                    fileSplit = file.split('_')
                    fileJson["date"] = fileSplit[2] + '/' + fileSplit[1] + '/' + fileSplit[0]\
                        + ' ' + fileSplit[3] + ':'+ fileSplit[4] + ':'+ fileSplit[5]
                    fileJson["fromto"] = fileSplit[7] + ' ' + fileSplit[8]
                    if fileJson["fromto"] == account["from_user"] + ' ' + account["to_user"] + '.txt':
                        fileIndex = fileIndex + 1
                        response.append([fileIndex, fileJson["date"], file])
                print(colorama.Fore.LIGHTYELLOW_EX)
                print(tabulate(response))
                print(colorama.Fore.RESET)

                logFileIndex = int(input("Input index logs file (Press a to break): "))
                for logFile in response:
                    if logFile[0] == logFileIndex:
                        print('Tail 1000 line of file ' + logFile[2])
                        os.system('clear')
                        os.system('tail -1000 LOG_imapsync/' + logFile[2])
                        input("Press any key to exit! ")
        except Exception as e:
            print(e)

def main():
    print(pyfiglet.figlet_format("BULK IMAPSYNC"))
    print("""
    0. Exit
    1. Show accounts
    2. Check login
    3. Sync accounts
    4. Show log file
    """)
    menu_selected = input("Select tools: ")
    if menu_selected == '0':
        print("Bye!")
        return False
    elif menu_selected == '1':
        while(read_excel('showaccounts')):
            pass
    elif menu_selected == '2':
        while(read_excel('checklogin')):
            pass
    elif menu_selected == '3':
        while(read_excel('sync')):
            pass
    elif menu_selected == '4':
        while(read_excel('showlogs')):
            pass
    return True

while(main()):
   pass
