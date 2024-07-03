import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxOTk1ODA5MSwianRpIjoiMTI3N2JmMjgtOTA5MC00MjU4LTk5MGYtOGVmNTcyN2NlMmQ0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ODM1MDA1MjU4LCJuYmYiOjE3MTk5NTgwOTEsImNzcmYiOiJmYWJhMTcxYy1lMTIxLTRhZTgtYjI3Yy1lMmMwZjEwODhjNzYiLCJleHAiOjE3MTk5NTg5OTF9.PVeLn9uhC9j6Z5iptugVuTnPntCzqexP9nmxdScedhE",
}
x = requests.get('https://7244-188-225-101-83.ngrok-free.app/quest_list', headers=headers)
print(x.json())
