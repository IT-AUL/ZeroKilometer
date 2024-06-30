import requests

data = {
"user_data": "grgrg"
}
headers = {
    "Content-Type": "application/json",
}
print(requests.post('https://c39b-178-205-48-57.ngrok-free.app/auth', json=data, headers=headers).json())
