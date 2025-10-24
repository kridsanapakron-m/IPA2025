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
def edit_motd(router_ip, motd_message):
    playbook_file = "playbook_edit_motd.yaml"

    inventory_inline = "router,"
    command = [
        "ansible-playbook",
        playbook_file,
        "-i", inventory_inline,
        "--extra-vars",
        f"ansible_host={router_ip} ansible_user=admin ansible_password=cisco ansible_network_os=cisco.ios.ios motd_message='{motd_message}'"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    result_text = result.stdout

    if "failed=0" in result_text and "unreachable=0" in result_text:
        return "Ok: success"
    else:
        print(result_text)
        if "no hosts matched" in result_text:
            return "Error: No hosts matched — check playbook host name"
        elif "No existing session" in result_text or "timed out" in result_text:
            return edit_motd(router_ip, motd_message)
        return "Error: Ansible"

