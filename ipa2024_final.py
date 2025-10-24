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
from restconf_final import create, enable, disable, delete, status
from netmiko_final import gigabit_status
from ansible_final import showrun
from fine_iparoom import get_room_id
import os
from dotenv import load_dotenv
load_dotenv()
from requests_toolbelt.multipart.encoder import MultipartEncoder
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

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith(f"/{student_id} "):

        # extract the command
        command = message.split(" ", 1)[1].strip()
        #print(command)
        my_student_id = message.split(" ", 1)[0][1:]
        #print(my_student_id)

# 5. Complete the logic for each command

        if command == "create":
            responseMessage = create(my_student_id)
        elif command == "delete":
            responseMessage = delete(my_student_id)
        elif command == "enable":
            responseMessage = enable(my_student_id)
        elif command == "disable":
            responseMessage = disable(my_student_id)
        elif command == "status":
            responseMessage = status(my_student_id)
        elif command == "gigabit_status":
            responseMessage = gigabit_status()
        elif command == "showrun":
            responseMessage = showrun()
        else:
            responseMessage = "Error: No command or unknown command"
        
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

        if command == "showrun" and responseMessage == 'ok':
                files = glob.glob("./show_run_66070006*")
                latest_file = max(files, key=os.path.getmtime)
                fileobject = open(latest_file, "rb")
                filetype = "text/plain"
                postData = MultipartEncoder(
                    fields={
                        "roomId": roomIdToGetMessages,
                        "text": "show running config",
                        "files": (os.path.basename(latest_file), fileobject, filetype)
                        })
                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": postData.content_type,}
        else:
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
