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
    
    proxies = []
    """ Structure:
    [
        {
            "proxy_address": "127.0.0.1",
            "port": 80, 
        },
        ...
    ]
    """
    
    comments = []      
    """ Structure:
    [
        {
            "mod_comment": "sample", 
            "comments": ["sample1", "sample2"]
            "id": 1,
        },
        ...
    ]
    """
    
    def __init__ (self):
        
        if not Api.proxies:
            self.__load_proxies__ ()
            
        if not Api.comments:
            self.__load_comments__ ()
    
        print ()
        
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
            proxies = json_data['results']
        except Exception as error:
            print (f"{LOGS_PREFIX} Error getting proxies: {error}")
            quit ()
        
        # Format proxyes data
        Api.proxies = list(map (lambda proxy: {
            "proxy_address": proxy["proxy_address"],
            "port": proxy["port"], 
        }, proxies))
        
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
            "id": comment["id"],
        }, comments))
        
        Api.comments = comments        
             
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
        proxy = random.choice (Api.proxies)
        return {
            "host": proxy["proxy_address"],
            "port": proxy["port"],
        }

    def get_streams(self) -> list:
        """ Get current live streams in comunidad mc, using the API

        Returns:
            list: streamer names.

            Example:  
            [
                {
                    "id": 1,
                    "date": "2023-09-09",
                    "start_time": "09:07:30",
                    "end_time": "20:00:00",
                    "is_active": true,
                    "streamer": "daridev",
                    "access_token": "SAMPLE_TOKEN"
                },
                ...
            ]
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

    def get_random_comment (self, mod_comment:str) -> dict:
        """ Get a random comment from options in database

        Args:
            mod_comment (str): comment sent by mod
            
        Returns:
            {
                "id_comment_mod": 1,
                "comment": "hello world",
            }
        """
        
        comments = list(filter (lambda comment: 
            comment["mod_comment"] == mod_comment,
        Api.comments))
                
        if not comments:
            return {}
        
        comments = comments[0]
        
        # Chose a comment from the list
        random_comment = random.choice (comments["comments"])
        
        return {
            "id_comment_mod": comments["id"],
            "comment": random_comment,
        }
    
    def save_comment_history (self, id_stream:int, id_bot:int, id_comment_mod:int, 
                              comment_bot:str, id_mod:int ):
        """ Save comment sent by bot in the API

        Args:
            id_stream (int): id stream
            id_bot (int): id bot
            id_comment_mod (int): id of comments relation
            comment_bot (str): comment sent by bot
            id_mod (int): id of the mod that sent initial the comment
        """
        
        res = requests.post (
            f"{API_HOST}/comments/comments-history/",
             headers={"token": TOKEN_COMMENTS},
            json={
                "stream": id_stream,
                "bot": id_bot,
                "comment_mod": id_comment_mod,
                "comment_bot": comment_bot,
                "mod": id_mod,
            },
        )
        
        json_data = res.json ()
        if json_data["status"] != "ok":
            print (f"{LOGS_PREFIX} Error saving comment history: {json_data['message']}")
        
# if __name__ == "__main__":
#     api = Api ()
#     api.save_comment_history (
#         id_stream=13,
#         id_bot=20,
#         id_comment_mod=10,
#         comment_bot=":3",
#         id_mod=3
#     )
    