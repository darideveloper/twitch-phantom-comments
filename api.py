import os
import random
import requests
from dotenv import load_dotenv

load_dotenv()
API_HOST = os.getenv("API_HOST")
TOKEN_WEBSHARE = os.getenv("TOKEN_WEBSHARE")
TOKEN_COMMENTS = os.getenv("TOKEN_COMMENTS")
TOKEN_STREAMS = os.getenv("TOKEN_STREAMS")

LOGS_PREFIX = "(api)"

class Api ():
    
    def __init__ (self):
        self.proxies = []
        self.comments = {}
        
        self.__load_proxies__ ()
        self.__load_comments__ ()
        
    def __load_proxies__ (self):
        """ Query proxies from the webshare api, and save them
        """
        
        print (f"{LOGS_PREFIX} Loading proxies...")
        
        # Get proxies
        res = requests.get (
            "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100", 
            headers = { 
                "Authorization": f"Token {TOKEN_WEBSHARE}"
            }
        )
        if res.status_code != 200:
            print (f"Error getting proxies: {res.status_code} - {res.text}")
            quit ()

        try:
            json_data = res.json ()
            self.proxies = json_data['results']
        except Exception as error:
            print (f"{LOGS_PREFIX} Error getting proxies: {error}")
            quit ()
            
    def __load_comments__ (self): 
        """ Query comments from the API, and save them 
        """
        
        print (f"{LOGS_PREFIX} Loading comments...")
        
        # Get data from api
        res = requests.get (
            f"{API_HOST}/comments/comments/",
            headers={"token": TOKEN_COMMENTS}
        )
        res.raise_for_status ()
        res_json = res.json ()
        
        # Filter only active comments
        comments = list(filter (lambda comment: 
            comment["is_active"], 
        res_json["data"]))
        
        # Format comments
        comments = list(map (lambda comment: {
            "mod_comment": comment["category"], 
            "comments": comment["comments"].split ("\r\n"),
        }, comments))
        
        self.comments = comments        
            
    def get_users (self) -> list:
        """ users and passwords from the API

        Returns:
            dict: user data (id, username and password)
            
            Example:
            [    
                {
                    "id": 1,
                    "user": "sample 1 user",
                    "cookies": {"hello": "word"},
                },
                {
                    "id": 2,
                    "user": "sample 2 user",
                    "cookies": {"hello": "word"},
                }
            ]

        """
        
        print (f"{LOGS_PREFIX} Getting users...")
        
        # Get data from api
        res = requests.get (
            f"{API_HOST}/comments/bots/", 
            headers={"token": TOKEN_COMMENTS}
        )
        res.raise_for_status ()
        json_data = res.json ()
        
        # Validate response
        if json_data["status"] != "ok":
            print (f"{LOGS_PREFIX} Error getting users: {json_data['message']}")
            quit ()
        
        users = json_data["data"]
        
        # Filter only active users
        users = list(filter (lambda user: user["is_active"], users))
        
        # Formatd ata
        users = list(map (lambda user: {
            "id": user["id"],
            "user": user["user"],
            "cookies": user["cookies"],
        }, users))
        
        return users

    def get_proxy (self) -> dict:
        """ get a random proxy 

        Returns:
            dict: proxy data (host and port)
            
            Example:
            {
                "host": "0.0.0.0",
                "port": 80,
            }
        """
        
        print (f"{LOGS_PREFIX} Getting a random proxy...")
        
        # Get data from api
        proxy = random.choice (self.proxies)
        return {
            "host": proxy["proxy_address"],
            "port": proxy["port"],
        }

    def get_streams(self) -> list:
        """ Get current live streams in comunidad mc, using the API

        Returns:
            list: streamer names.

            Example:  ["DariDeveloper", "darideveloper2"]
        """

        print(f"{LOGS_PREFIX} Getting streams...")
        
        # Get data from api
        res = requests.get (
            f"{API_HOST}/streams/current-streams",
            headers={"token": TOKEN_STREAMS}
        )
        json_data = res.json()
        streams = json_data["data"]
        
        return streams
    
    def disable_user (self, user_id:int, user_name:str): 
        """ Disable user in the API

        Args:
            user_id (int): user id
            user_name (str): user name
        """
        
        print (f"\t{LOGS_PREFIX} Disabling user {user_name}...")
        
        res = requests.delete (
            f"{API_HOST}/comments/bots/",
            headers={"token": TOKEN_COMMENTS},
            json={"id": user_id},
        )
        
        json_data = res.json ()
        if json_data["status"] != "ok":
            print (f"{LOGS_PREFIX} Error disabling user: {json_data['message']}")

    def get_random_comment (self, mod_comment:str): 
        """ Get a random comment from options in database

        Args:
            mod_comment (str): comment sent by mod
        """
        
        comments = list(filter (lambda comment: 
            comment["mod_comment"] == mod_comment, 
        self.comments))[0]
                
        if not comments:
            return ""
        
        random_comment = random.choice (comments["comments"])
        
        return random_comment
    
    