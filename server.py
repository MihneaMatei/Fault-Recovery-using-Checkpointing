from flask import Flask
import subprocess
import os

app = Flask(__name__)

def is_recovery_script_running():
    try:
        output = subprocess.check_output(["pgrep", "-f", "script.py"])
        return output.decode().strip() != ""
    except subprocess.CalledProcessError:
        return False

@app.route("/")
def index():
    if is_recovery_script_running():
        return "Recovery script is running.", 200
    else:
        return "Recovery script is NOT running.", 503

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)