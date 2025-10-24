#######################################################################################
# Yourname: Kridsanapakron Marat
# Your student ID: 66070006
# Your GitHub Repo: https://github.com/kridsanapakron-m/IPA2024-Final.git

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import json
import time
import glob
import requests
import restconf_final
import netconf_final
from netmiko_final import read_motd
from ansible_final import edit_motd
from fine_iparoom import get_room_id
import os
from dotenv import load_dotenv
load_dotenv()
from requests_toolbelt.multipart.encoder import MultipartEncoder
command_type = 0
router_ip = None
def check_type_command(message):
    global command_type
    if message == "restconf":
        command_type = 1
        return "Ok: Restconf"
    elif message == "netconf":
        command_type = 2
        return "Ok: Netconf"
    else:        
        command_type = 0
        return "Error: No method specified"
#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.getenv("webex_token")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = get_room_id("IPA2025")
student_id = os.getenv("student_id")
while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    json_data = r.json()
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")
    messages = json_data["items"]
    message = messages[0]["text"]
    if not message.startswith(f"/{student_id} "):
        continue
    print("My message: " + message)
    parts = message.split()
    if len(parts) < 2:
        continue
    tokens = parts[1:]
    responseMessage = ""

    if len(tokens) == 1:
        # case "/66070006 restconf" or "/66070006 create"
        text = tokens[0]
        if text in ["restconf", "netconf"]:
            responseMessage = check_type_command(text)
        elif text.count(".") == 3:  # check IP
            responseMessage = "Error: No command found."
        elif command_type == 0 and text in ["create", "delete", "enable", "disable", "status"]:
            responseMessage = "Error: No method specified"
        else:
            responseMessage = "Error: No IP specified"

    elif len(tokens) >= 2:
        # case"/66070006 10.0.15.61 create"
        router_ip = tokens[0]
        command = tokens[1]

        if command == "motd" and router_ip is not None:
            #/66070123 10.0.15.61 motd Authorized users only! Managed by 66070123
            if len(tokens) >= 8 and tokens[2] == "Authorized" and tokens[3] == "users" and tokens[4] == "only!" and tokens[5] == "Managed" and tokens[6] == "by" and tokens[7] == student_id:
                responseMessage = edit_motd(router_ip, student_id)
            else:
                responseMessage = read_motd(router_ip)
        elif command_type == 0:
            responseMessage = "Error: No method specified"
        elif not router_ip:
            responseMessage = "Error: No IP specified"
        else:
            if command_type == 1:
                module = restconf_final
            elif command_type == 2:
                module = netconf_final

            if command == "create":
                responseMessage = module.create(student_id, router_ip)
            elif command == "delete":
                responseMessage = module.delete(student_id, router_ip)
            elif command == "enable":
                responseMessage = module.enable(student_id, router_ip)
            elif command == "disable":
                responseMessage = module.disable(student_id, router_ip)
            elif command == "status":
                responseMessage = module.status(student_id, router_ip)
            else:
                responseMessage = "Error: Unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        # if command == "showrun" and responseMessage == 'ok':
        #         files = glob.glob("./show_run_66070006*")
        #         latest_file = max(files, key=os.path.getmtime)
        #         fileobject = open(latest_file, "rb")
        #         filetype = "text/plain"
        #         postData = MultipartEncoder(
        #             fields={
        #                 "roomId": roomIdToGetMessages,
        #                 "text": "show running config",
        #                 "files": (os.path.basename(latest_file), fileobject, filetype)
        #                 })
        #         HTTPHeaders = {
        #             "Authorization": f"Bearer {ACCESS_TOKEN}",
        #             "Content-Type": postData.content_type,}
        # else:
    postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
    postData = json.dumps(postData)
    HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/yang-data+json"
        }   

    r = requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)
    if not r.status_code == 200:
        raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
