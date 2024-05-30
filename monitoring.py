import requests
import time
import subprocess

def check_server(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("VM1 is active, and the recovery script is running.")
            return True
        else:
            print("VM1 is active, but the recovery script is NOT running.")
            return False
    except requests.RequestException:
        print("VM1 is down.")
        return False

def run_recovery_script():
    print("Running the recovery script...")
    process = subprocess.Popen(['python', 'script.py'], start_new_session=True)
    return process
    

if __name__ == "__main__":
    server_url = 'http://192.168.0.94:8000' 
    check_interval = 10

    while True:
        if not check_server(server_url):
            print("Taking over the recovery operations.")
            process = run_recovery_script()
            while not check_server(server_url):
                print("Running on backup VM")
                time.sleep(check_interval)
            process.terminate()
            print("Resuming on VM1")
        time.sleep(check_interval)