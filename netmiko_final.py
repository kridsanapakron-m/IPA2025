from netmiko import ConnectHandler
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()

device_ip = os.getenv("router_ip")
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        result = ssh.send_command("show ip interface brief", use_textfsm=True)

        up = 0
        down = 0
        admin_down = 0
        interface_status_list = []

        for intf in result:
            if intf["interface"].startswith("GigabitEthernet"):
                interface_name = intf["interface"]
                interface_state = intf["status"].lower()

                if "admin" in interface_state:
                    state_text = "administratively down"
                    admin_down += 1
                elif interface_state == "down":
                    state_text = "down"
                    down += 1
                elif interface_state == "up":
                    state_text = "up"
                    up += 1
                else:
                    state_text = interface_state

                interface_status_list.append(f"{interface_name} {state_text}")

        ans = f"{', '.join(interface_status_list)} -> {up} up, {down} down, {admin_down} administratively down"
        return ans