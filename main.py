import time
from datetime import datetime, timezone
import sched
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
import json
import pytz
from tabulate import tabulate
from api import Myworkspace

# initialize the browser to get token from session storage
def get_token():
    options = EdgeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.ChromiumEdge(options=options)
    browser.get("https://myworkspace.microsoft.com/")
    time.sleep(15)
    storageKey = "be3c2eaf-1dce-4a89-bfc8-22d58fbc8a9f.72f988bf-86f1-41af-91ab-2d7cd011db47-login.windows.net-accesstoken-2ec0e21d-27e1-41a8-a154-6c791ce63b1a-72f988bf-86f1-41af-91ab-2d7cd011db47-api://2ec0e21d-27e1-41a8-a154-6c791ce63b1a/user_impersonation--"
    sessionStorage = browser.execute_script("return window.sessionStorage")
    tokenObj = sessionStorage[storageKey]
    access_token = json.loads(tokenObj)['secret']
    print('Got access_token successfully.')
    browser.quit()
    return access_token

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
scheduler = sched.scheduler(time.time, time.sleep)
# Schedule the alwaysOn function to run every 10 minutes
scheduler.enter(600, 1, alwaysOn)
scheduler.run()