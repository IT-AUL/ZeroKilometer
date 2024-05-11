from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup


class Translate:
    tat2rus_url = "https://translate.tatar/translate?lang=1&text="
    rus2tat_url = "https://translate.tatar/translate?lang=0&text="

    def tat_to_rus(self, text: str) -> str:
        response_translated = requests.get(self.tat2rus_url + unquote(text))
        if b"translation" in response_translated.content:
            parsed_html = BeautifulSoup(response_translated.content, features="html.parser")
            return parsed_html.find("translation").text
        else:
            return response_translated.text

    def rus_to_tat(self, text: str) -> str:
        response_translated = requests.get(self.rus2tat_url + unquote(text))
        if b"translation" in response_translated.content:
            parsed_html = BeautifulSoup(response_translated.content, features="html.parser")
            return parsed_html.find("translation").text
        else:
            return response_translated.text
