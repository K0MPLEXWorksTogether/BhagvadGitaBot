import aiohttp
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

URL = "https://bhagvad-gita-db.vercel.app/"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

async def query(session, username: str) -> str:
    try:
        params = {"username": username}
        auth = aiohttp.BasicAuth(USERNAME, PASSWORD)

        async with session.get(f"{URL}/query", params=params, auth=auth) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("usertype", "")
            else:
                print(f"Failed: {response.status} - {await response.text()}")
                return ""
        
    except aiohttp.ClientError as RequestError:
        print("Request Failed: ", RequestError)
        return ""
    except Exception as Error:
        print("Failed To Query: ", Error)
        return ""

async def create(session, username: str, usertype: str, chatID: str, time: str) -> bool:
    try:
        args = {
            "username": username,
            "usertype": usertype,
            "chatID": chatID,
            "time": time
        }
        auth = aiohttp.BasicAuth(USERNAME, PASSWORD)

        async with session.post(f"{URL}/create", json=args, auth=auth) as response:
            if response.status == 200:
                return True
            else:
                print(f"Failed: {response.status} - {await response.text()}")
                return False
    except aiohttp.ClientError as e:
        print("Request Failed:", e)
        return False
    except Exception as e:
        print("Failed To Create User:", e)
        return False

async def delete(session, username: str, usertype: str) -> bool:
    try:
        args = {
            "username": username,
            "usertype": usertype
        }
        auth = aiohttp.BasicAuth(USERNAME, PASSWORD)

        async with session.delete(f"{URL}/delete", json=args, auth=auth) as response:
            if response.status == 200:
                return True
            else:
                print(f"Failed: {response.status} - {await response.text()}")
                return False
    except aiohttp.ClientError as e:
        print("Request Failed:", e)
        return False
    except Exception as e:
        print("Failed To Delete User:", e)
        return False

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        success = await delete(session=session, username="queryTestSeq", usertype="random")
        if success:
            print("Returned Result:", success)
        else:
            print("Failed To Retrieve Data.")

if __name__ == "__main__":
    asyncio.run(main())