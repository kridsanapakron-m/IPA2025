import json
from dotenv import load_dotenv
import requests
import os

load_dotenv()
requests.packages.urllib3.disable_warnings()

# RESTCONF HTTP headers
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Basic Auth
basicauth = ("admin", "cisco")


def generate_loopback_config(studentID):
    last3 = studentID[-3:]
    x = int(last3[0])
    y = int(last3[1:])
    ip_address = f"172.{x}.{y}.1"
    interface_name = f"Loopback{studentID}"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": interface_name,
            "description": f"Loopback for {studentID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip_address,
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }
    return interface_name, yangConfig


def create(studentID, router_ip):
    base_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    interface_name, yangConfig = generate_loopback_config(studentID)
    url = f"{base_url}/interface={interface_name}"

    resp_check = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if resp_check.status_code == 200:
        return f"Cannot create: Interface loopback {studentID}"

    resp = requests.put(url, data=json.dumps(yangConfig), auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return f"Interface loopback {studentID} is created successfully"
    else:
        return f"Cannot create: Interface loopback {studentID}"


def delete(studentID, router_ip):
    base_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    interface_name = f"Loopback{studentID}"
    url = f"{base_url}/interface={interface_name}"

    resp_check = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if resp_check.status_code != 200:
        return f"Cannot delete: Interface loopback {studentID}"

    resp = requests.delete(url, auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return f"Interface loopback {studentID} is deleted successfully"
    else:
        return f"Cannot delete: Interface loopback {studentID}"


def enable(studentID, router_ip):
    base_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    interface_name = f"Loopback{studentID}"
    url = f"{base_url}/interface={interface_name}"

    resp_check = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if resp_check.status_code != 200:
        return f"Cannot enable: Interface loopback {studentID}"

    data = {"ietf-interfaces:interface": {"enabled": True}}
    resp = requests.patch(url, data=json.dumps(data), auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return f"Interface loopback {studentID} is enabled successfully"
    else:
        return f"Cannot enable: Interface loopback {studentID}"


def disable(studentID, router_ip):
    base_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    interface_name = f"Loopback{studentID}"
    url = f"{base_url}/interface={interface_name}"

    resp_check = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if resp_check.status_code != 200:
        return f"Cannot shutdown: Interface loopback {studentID}"

    data = {"ietf-interfaces:interface": {"enabled": False}}
    resp = requests.patch(url, data=json.dumps(data), auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return f"Interface loopback {studentID} is shutdowned successfully"
    else:
        return f"Cannot shutdown: Interface loopback {studentID}"


def status(studentID, router_ip):
    base_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    interface_name = f"Loopback{studentID}"
    url = f"{base_url}/interface={interface_name}"

    resp = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        enabled = data["ietf-interfaces:interface"]["enabled"]
        state = "enabled" if enabled else "disabled"
        return f"Interface loopback {studentID} is {state}"
    else:
        return f"No Interface loopback {studentID}"
