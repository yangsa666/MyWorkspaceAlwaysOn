from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from datetime import datetime, timezone
import pytz
import json
import time
import schedule
from tabulate import tabulate
from api import Myworkspace

# initialize the browser to get token from session storage
def get_token():
    try:
        options = EdgeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.ChromiumEdge(options=options)
        browser.get("https://myworkspace.microsoft.com/")
        time.sleep(15)
        sessionStorage = browser.execute_script("return window.sessionStorage")
        print(sessionStorage)
        myworkspaceAppId = '2ec0e21d-27e1-41a8-a154-6c791ce63b1a'
        tokenKey = json.loads(sessionStorage[f'msal.token.keys.{myworkspaceAppId}'])['accessToken'][1]
        tokenObj = sessionStorage[tokenKey]
        access_token = json.loads(tokenObj)['secret']
        print('Got access_token successfully.')
        browser.quit()
        return access_token
    except Exception as e:
        print(f"Failed to get access_token, error: {e}")
        return None

def conver_jit_status(status_code):
    if status_code == 5:
        return "Activated"
    elif status_code == 2:
        return "Activating"
    elif status_code == 4:
        return "Deactivating"
    else:
        return "Not Activated"
def convert_utc_to_shanghai(utc_datetime_str):
    # Parse the UTC datetime string to a datetime object with timezone
    utc_datetime = datetime.fromisoformat(utc_datetime_str)
    # Define the Asia/Shanghai timezone
    shanghai_timezone = pytz.timezone('Asia/Shanghai')
    # Convert the UTC datetime to Asia/Shanghai datetime
    shanghai_datetime = utc_datetime.astimezone(shanghai_timezone)
    # Format the Asia/Shanghai datetime as a string
    shanghai_datetime_str = shanghai_datetime.strftime('%Y-%m-%d %H:%M:%S.%f%z')
    return shanghai_datetime_str

def alwaysOn():
    print(datetime.now(pytz.timezone('Asia/Shanghai')), " Starting AlwaysOn...")
    token = get_token()
    mw = Myworkspace(token)
    workspaces = mw.get_workspaces()

    workspace_table = list(map(lambda workspace: {'ID': workspace['ID'], 'Name': workspace['Name'], 'State': 'Running' if workspace['State'] == 4 else 'Stopped', 'ShutdownTime': convert_utc_to_shanghai(workspace['ShutdownTimeInUtc'])}, workspaces))
    table = tabulate((workspace_table), headers='keys', tablefmt = "grid")
    print(table)

    nat_jit = mw.get_nat_jit()
    jit_table = list(map(lambda jit: {'WorkspaceID': jit['WorkspaceID'], 'Status': conver_jit_status(jit['Status'])}, nat_jit))
    table = tabulate((jit_table), headers='keys', tablefmt = "grid")
    print(table)

    for workspace in workspaces:
        if workspace['State'] != 4:
            print(f"Workspace {workspace['Name']} is stopped, starting workspace...")
            mw.start_workspace(workspace['ID'])

        if not any(jit['WorkspaceID'] == workspace['ID'] for jit in jit_table):
            print(f"External Connectivity JIT not activated for workspace {workspace['Name']}, activating External Connectivity JIT...")
            mw.extend_jit(workspace['ID'], 168)
            print(f"External Connectivity JIT activated for workspace {workspace['Name']}")

        left_running_mins = (datetime.fromisoformat(workspace['ShutdownTimeInUtc']) - datetime.now(timezone.utc)).total_seconds() / 60
        if workspace['State'] == 4 and left_running_mins < 60 and left_running_mins > 0:
            print(f"Workspace {workspace['Name']} is running, but running time has {left_running_mins} mins left, extending running time...")
            result = mw.extend_running_time(workspace['ID'], 8)
            print(f"Running time extended for workspace {workspace['Name']} for additional {result} hours")

    print("alwaysOn executed successfully this time")

alwaysOn()

schedule.every(10).minutes.do(alwaysOn)

while True:
    schedule.run_pending()
    time.sleep(1)