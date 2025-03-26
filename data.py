import requests
import json
import tempfile
import os

URL = "https://bhagvad-gita-api.vercel.app/"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def getVerseData(chapter: int, verse: int) -> dict:
    try:
        parameters = {
        "chapter": chapter,
        "verse": verse
        }

        response = requests.get(f"{URL}/verse", params=parameters)
        return json.loads(response.text)
    except Exception as getVerseError:
        print("Failed To Retrieve Data: ", getVerseError)

def getAudioData(chapter: int, verse: int) -> str:
    try:
        parameters = {
        "chapter": chapter,
        "verse": verse
        }

        response = requests.get(f"{URL}/audio", params=parameters)

        if response.status_code == 200:
            
            TempDir = os.path.join(PROJECT_ROOT, "temp_audio_files")

            if not os.path.exists(TempDir):
                os.makedirs(TempDir)

            filePath = os.path.join(TempDir, f"{chapter}-{verse}.mp3")

            with open(filePath, "wb") as file:
                file.write(response.content)

            print(f"Audio saved to {filePath}")
            return TempDir  
        else:
            print("Failed To Retrieve Audio.")
            return ""
    except Exception as getAudioError:
        print("Failed To Retrieve Audio: ", getAudioError)

def deleteAudioFile(chapter: int, verse: int) -> None:
    try: 
        TempDir = os.path.join(PROJECT_ROOT, "temp_audio_files")
        filePath = os.path.join(TempDir, f"{chapter}-{verse}.mp3")

        if os.path.exists(filePath):
            os.remove(filePath)
            print(f"Audio file {filePath} deleted.")
        else:
            print(f"No audio file found for Chapter {chapter}, Verse {verse}.")
    except FileNotFoundError:
        print(f"No audio file found for Chapter {chapter}, Verse {verse}.")