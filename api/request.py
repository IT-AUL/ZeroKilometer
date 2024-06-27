import requests

# Define the URL of your Flask application endpoint
url = 'http://localhost:5000/auth'  # Replace with your actual endpoint URL

# Data to be sent as JSON
data = {
    'id': '100', "username": "egg"}
headers = {
    "Content-Type": "application/json",
}
# Send POST request with JSON data
response = requests.post(url, headers=headers, json=data)

# Print response
print(response.status_code)
print(response.json())
print(requests.get("http://localhost:5000/api/quest").json())
