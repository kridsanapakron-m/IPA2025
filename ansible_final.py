import subprocess
import os
import re

def showrun():
    playbook_file = "playbook_showrun.yaml"
    command = ["ansible-playbook", playbook_file]
    result = subprocess.run(command, capture_output=True, text=True)
    result = result.stdout
    if "failed=0" in result and 'unreachable=0' in result:
        return "ok"
    else:
        print(result)
        if "No existing session" in result or "timed out" in result:
            showrun()
        return "Error: Ansible"