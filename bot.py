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
    
    bots = {}
    """Strcuture
    {
        "stramer": {
            "bot1": Bot,
            "bot2": Bot,
            "bot3": Bot,
        },
        ...
    }
    
    """
    
    api = Api ()
    
    def __init__ (self): 
        
        # Css selectors
        self.selectors = {
            'login_btn': '[data-a-target="login-button"]',
            'comment_textarea': '[data-a-target="chat-input"]',
            'comment_send_btn': 'button[data-a-target="chat-send-button"]',
            'comment_accept_buttons': [
                'button[data-test-selector="chat-rules-ok-button"]',
                'button[data-test-selector="chat-rules-show-intro-button"]',
            ],
            'comment_warning_before': '[.chat-input-tray__clickable]',
            'comment_warning_after': '[data-test-selector="full-error"], [data-test-selector="inline-error"]',
            'player': '.persistent-player'
        }
        
        # Current scraper instance
        self.scraper = None
        
        # Api data
        self.streams = []
        self.users = []
        
        # Bot data
        self.bot_name = ""
        self.id_stream = 0
        self.id_bot = 0
        
        # Comments data
        self.id_comment_mod = 0
        self.comment_bot = ""
        self.id_mod = 0
        
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
        proxy = Bot.api.get_proxy ()
        
        # Save comment data
        self.id_bot = user['id']
        self.bot_name = user['user']
        
        print (f"{LOGS_PREFIX} Starting bot with user {self.bot_name}")
        
        # Start chrome
        self.scraper = WebScraping (
            proxy_server=proxy['host'],
            proxy_port=proxy['port'],
            start_killing=False,
        )
        
        # Test proxies loading a page
        self.scraper.set_page ("https://ipinfo.io/json")
        body = self.scraper.get_text ("body")
        if not '"ip":' in body:
            print (f"{LOGS_PREFIX} Error loading proxy {proxy['host']}:{proxy['port']}")
            return None
        
        # Login with cookies
        self.scraper.set_page ("https://www.twitch.tv/login")
        self.scraper.set_cookies (user['cookies'])
        
        # Validate login seaching login button
        self.scraper.set_page ("https://www.twitch.tv")
        login_button = self.scraper.get_elems (self.selectors['login_btn'])
        if login_button:
            
            # Disable user and debug error    
            print (f"{LOGS_PREFIX} Error login with user {self.bot_name}")
            Bot.api.disable_user (user['id'])
            return None
        
        # Open stream 
        stramer = stream['streamer'].lower()
        chat_link = f"https://www.twitch.tv/{stramer}/"
        self.scraper.set_page (chat_link)
        
        # Hide video
        player = self.scraper.get_elems (self.selectors["player"])
        if player:
            script = f"document.querySelector ('{self.selectors['player']}').style.display = 'none'"
            self.scraper.driver.execute_script (script)
        
        # Create streamer dict if not exists
        if not Bot.bots.get (stramer, {}):
            Bot.bots[stramer] = {}
        
        # Save scraper
        Bot.bots[stramer][self.bot_name] = self
        
        print (f"\t{LOGS_PREFIX} Bot waiting with user {self.bot_name}")
        
        # Keep open until stream ends
        now = datetime.now()
        end_time = datetime.strptime (stream["end_time"], "%H:%M:%S")
        end_time = end_time.replace (year=now.year, month=now.month, day=now.day)
        running_time = end_time - now
        running_seconds = running_time.total_seconds ()
        
        # Save stream id
        self.id_stream = stream["id"]
        
        # Wait until stream ends
        sleep (running_seconds)
        self.scraper.end_browser ()
    
    def __send_comment__ (self): 
        """ Send comment with scraper
        
        Args: 
            comment (str): comment to send
        """
        
        # Random wait time
        sleep (random.randint (1, 5))
        
        # Validate if constrols are visible
        comment_textarea_visible = self.scraper.get_elems (self.selectors["comment_textarea"])
        comment_send_btn_visible = self.scraper.get_elems (self.selectors["comment_send_btn"])
        if not comment_textarea_visible or not comment_send_btn_visible:
            print (f"{LOGS_PREFIX} Error: inputs not visible")
            return False
            
        # Validate error messages
        warning_text = self.scraper.get_text (self.selectors["comment_warning_before"])
        if warning_text:
            print (f"{LOGS_PREFIX} Error: Inputs not available: {warning_text}")
            return False
        
        # Write message
        self.scraper.send_data (self.selectors["comment_textarea"], self.comment_bot)
        sleep (5)
        
        # Click in accept buttons
        for selector in self.selectors["comment_accept_buttons"]:
            
            accept_elem = self.scraper.get_elems (selector)
            if accept_elem:
                self.scraper.click (selector)
                
                # Write message (again)
                self.scraper.send_data (self.selectors["comment_textarea"], self.comment_bot)
                
        # Submit donation
        self.scraper.refresh_selenium ()
        self.scraper.click (self.selectors["comment_send_btn"])
                
        warning_text = self.scraper.get_text (self.selectors["comment_warning_after"])
        if warning_text:
            self.print (f"{LOGS_PREFIX} Error: Donation not send: {warning_text}")
            return False
            
        print (f"{LOGS_PREFIX} Comment sent with bot {self.bot_name}: {self.comment_bot}")
        
        # Send comment to api
        self.api.save_comment_history (
            id_stream = self.id_stream,
            id_bot = self.id_bot,
            id_comment_mod = self.id_comment_mod,
            comment_bot = self.comment_bot,
            id_mod = self.id_mod,
        )
    
    def start_bots (self): 
        """ Auto start all required bots """
        
        # Update api data
        self.streams = Bot.api.get_streams ()
        self.users = Bot.api.get_users ()
        
        # Validate if there are streams   
        if not self.streams:
            print (f"{LOGS_PREFIX} No streams available")
            return None
  
        # Start each bot in thread
        for stream in self.streams:
            
            print (f"\n{LOGS_PREFIX} Starting {BOTS_STREAM} bots in stream {stream['streamer']}\n")
            
            for _ in range (BOTS_STREAM): 
                thread_obj = Thread (target=self.__start_bot__, args=(stream,))
                thread_obj.start ()
    
    @classmethod
    def send_comments (self, streamer:str, id_mod:int, mod_comment:str): 
        """ Send commnt to all bots

        Args:
            streamer (str): streamer name
            id_mod (int): mod id
            mod_comment (str): comment sent by mod
        """
        
        # Clean comment
        mod_comment = mod_comment.strip ()
        
        # Get bots of the current stream
        bots = Bot.bots.get (streamer, {})
        
        # Send message with each bot in stream
        for bot_name, bot in bots.items():
            
            comment_bot_data = Bot.api.get_random_comment (mod_comment)
            
            if not comment_bot_data:
                print (f"{LOGS_PREFIX} No random comment available for '{mod_comment}'")
                return None
            
            id_comment_mod = comment_bot_data["id_comment_mod"]
            comment_bot = comment_bot_data["comment"]
            
            print (f"{LOGS_PREFIX} Sending comment with bot {bot_name}: {comment_bot}...")
            
            # Update bot data
            bot.id_comment_mod = id_comment_mod
            bot.comment_bot = comment_bot
            bot.id_mod = id_mod
            
            thread_obj = Thread (target=bot.__send_comment__)
            thread_obj.start ()