import subprocess
import time
import random

def notify(title, text):
    script = f'display notification "{text}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

def beep():
    subprocess.run(["osascript", "-e", "beep"])

messages = [
    ("System Integrity Check", "Scanning startup disk..."),
    ("Security Agent", "Unusual process behavior detected"),
    ("CoreServices", "Reindexing system memory"),
    ("Kernel", "User attention required"),
    ("Finder", "Nothing is wrong. Probably."),
]

time.sleep(2)

notify("Boot Monitor", "Initializing background diagnostics...")
beep()
time.sleep(2)

for title, msg in messages:
    notify(title, msg)
    if random.random() > 0.5:
        beep()
    time.sleep(random.uniform(1.5, 3.5))

notify("System Status", "All systems operational.")
beep()