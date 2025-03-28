import requests
import json 
import os

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
load_dotenv()

URL = "https://bhagvad-gita-db.vercel.app/"
AUTH_OBJECT = HTTPBasicAuth(os.getenv("USERNAME"), os.getenv("PASSWORD"))

def query(username: str) -> str:
    try:
        params = {
            "username": username
        }

        response = requests.get(f"{URL}/query", params=params, auth=AUTH_OBJECT)
        if response.status_code == 200:
            return response.json()["usertype"]
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return ""
    except requests.exceptions.RequestException as RequestException:
        print("Request Failed: ", RequestException)
        return False
    except Exception as QueryError:
        print("Failed To Query Database: ", QueryError)
        return ""

def create(username: str, usertype: str, chatID: str, time: str) -> bool:
    try:
        args = {
            "username": username,
            "usertype": usertype,
            "chatID": chatID,
            "time": time,
        }

        response = requests.post(f"{URL}/create", json=args, auth=AUTH_OBJECT)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as RequestException:
        print("Request Failed: ", RequestException)
        return False
    except Exception as CreateError:
        print("Failed To Create User: ", CreateError)
        return False

def delete(username: str, usertype: str) -> bool:
    try:
        args = {
            "username": username,
            "usertype": usertype
        }

        response = requests.delete(f"{URL}/delete", json=args, auth=AUTH_OBJECT)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as RequestException:
        print("Request Failed: ", RequestException)
        return False
    except Exception as CreateError:
        print("Failed To Create User: ", CreateError)
        return False


delete(
    username="Abhiram",
    usertype="sequential"
)
