import os
import random
from time import sleep
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv
from api import Api
from scraping.web_scraping import WebScraping

load_dotenv ()
BOTS_STREAM = int(os.getenv ("BOTS_STREAM"))
CHROME_FOLDER = os.getenv ("CHROME_FOLDER")

LOGS_PREFIX = "(bots)"

class Bot (): 
    
    scrapers = {}
    
    def __init__ (self): 
                
        # Connect with api
        self.api = Api ()
        self.streams = self.api.get_streams ()
        
        # Get users 
        self.users = self.api.get_users ()
        
        # Css selectors
        self.selectors = {
            'login_btn': '[data-a-target="login-button"]',
        }
        
        if not self.streams:
            print (f"{LOGS_PREFIX} No streams available")
            return None
        
        # Start each bot in thread
        for stream in self.streams:
            
            print (f"\n{LOGS_PREFIX} Starting {BOTS_STREAM} bots in stream {stream['streamer']}\n")
            
            for _ in range (BOTS_STREAM): 
                thread_obj = Thread (target=self.__start_bot__, args=(stream,))
                thread_obj.start ()
        
    def __start_bot__ (self, stream:dict):
        """ Start chrome in chat page with user cookies and proxy,
            and keep open until stream ends.

        Args:
            stream (dict): Currenmt stream data
        """
        
        # Random wait time 
        sleep (random.randint (1, 30)/10)
        
        # Validate if there are users
        if not self.users:
            print (f"{LOGS_PREFIX} No users available")
            return None
        
        # Get random user and proxy
        user = random.choice (self.users)
        self.users.remove (user)
        proxy = self.api.get_proxy ()
        
        print (f"{LOGS_PREFIX} Starting bot with user {user['user']}")
        
        # Start chrome
        scraper = WebScraping (
            proxy_server=proxy['host'],
            proxy_port=proxy['port'],
            start_killing=False,
        )
        
        # Test proxies loading a page
        scraper.set_page ("https://ipinfo.io/json")
        body = scraper.get_text ("body")
        if not '"ip":' in body:
            print (f"{LOGS_PREFIX} Error loading proxy {proxy['host']}:{proxy['port']}")
            return None
        
        # Login with cookies
        scraper.set_page ("https://www.twitch.tv/login")
        scraper.set_cookies (user['cookies'])
        
        # Validate login seaching login button
        scraper.set_page ("https://www.twitch.tv")
        login_button = scraper.get_elems (self.selectors['login_btn'])
        if login_button:
            
            # Disable user and debug error    
            print (f"{LOGS_PREFIX} Error login with user {user['user']}")
            self.api.disable_user (user['id'])
            return None
        
        # Open stream chat
        chat_link = f"https://www.twitch.tv/popout/{stream['streamer']}/chat?popout="
        scraper.set_page (chat_link)
        
        # Save scraper
        Bot.scrapers[user['user']] = scraper
        
        print (f"\t{LOGS_PREFIX} Bot waiting with user {user['user']}")
        
        # Keep open until stream ends
        now = datetime.now()
        end_time = datetime.strptime (stream["end_time"], "%H:%M:%S")
        end_time = end_time.replace (year=now.year, month=now.month, day=now.day)
        running_time = end_time - now
        running_seconds = running_time.total_seconds ()
        
        # Wait until stream ends
        sleep (running_seconds)
        scraper.end_browser ()
        
if __name__ == "__main__":
    Bot ()