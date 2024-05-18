import json
import urllib.parse

API_TOKEN = 'YOUR_BOT_TOKEN'
WEBAPP_URL = 'https://your-webapp-url.com/?name={name}'

array_of_numbers = [1, 2, 3, 4, 5]

encoded_array = urllib.parse.quote(json.dumps(array_of_numbers))

url = WEBAPP_URL.format(name=encoded_array)

print(url)
