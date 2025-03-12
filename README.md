# How to run
1. Install Python if it's not yet: https://www.python.org/downloads/
2. Git clone this Repo or download the file to your device. The device requires to be enrolled with your work account.
3. Open terminal and cd to the project folder.
4. Use python virtual environment to install requirements and run.
    - `python -m venv .venv`
    - `.\.venv\Scripts\Activate.ps1`
    - `pip install -r .\requirements.txt`
    - Run: `python .\main.py`

5. Debug in VSCode.
    - Press `Ctrl + Shift + P` to select Python Interpreter.
    - Choose the venv you created previously.
    - Select `main.py` file.
    - Press `F5` to run.

# How it works
The script uses selenium to get token from the browser. By calling MyWorkspace APIs, it can monitor and perform actions on your workspaces.