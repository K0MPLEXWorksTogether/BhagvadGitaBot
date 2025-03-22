"""
This file contains all the utilities to interact with the deployed BhagvadGitaAPI.
"""

import requests
import json

URL = "https://bhagvad-gita-api.vercel.app/"

def getVerseData(chapter: int, verse: int) -> dict:
    try:
        parameters = {
        "chapter": chapter,
        "verse": verse
        }

        response = requests.get(f"{URL}/verse", params=parameters)
        return json.loads(response.text)
    except Exception as GetVerseError:
        print("Failed To Retrieve Data: ", GetVerseError)