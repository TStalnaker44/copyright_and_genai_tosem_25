
import os, subprocess, webbrowser, time
from threading import Thread

def main():
    thread = Thread(target = run_server)
    thread.start()
    time.sleep(5)
    open_browser()

def run_server():
    current = os.getcwd()
    path = os.path.join(current, "scripts", "reconciliator", "manage.py")
    subprocess.run(f'py "{path}" runserver')

def open_browser():
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    main()