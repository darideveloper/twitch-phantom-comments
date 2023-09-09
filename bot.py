import os
import random
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from api import Api
from scraping.web_scraping import WebScraping

load_dotenv ()
BOTS_STREAM = int(os.getenv ("BOTS_STREAM"))
CHROME_FOLDER = os.getenv ("CHROME_FOLDER")

LOGS_PREFIX = "(bots)"

class Bot (WebScraping): 
    
    api = Api ()
    
    # Api data
    streams = []
    users = []
    
    # Css selectors
    selectors = {
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
    
    def __init__ (self): 
        """ Initialize bots in chat and submit comments """        
        
        # Current scraper instance
        self.scraper = None
        
        # Bot data
        self.bot_name = ""
        self.id_stream = 0
        self.id_bot = 0
        self.streamer = ""
        
        # Comments data
        self.id_comment_mod = 0
        self.comment_bot = ""
        self.id_mod = 0
        
    def start_bot (self, stream:dict, user:dict, proxy:dict):
        """ Start chrome in chat page with user cookies and proxy,
            and keep open until stream ends.

        Args:
            stream (dict): current stream data
            user (dict): random user data
            proxy (dict): random proxy data
        """
        
        # Random wait time 
        sleep (random.randint (1, 30)/10)
        
        # Save comment data
        self.id_bot = user['id']
        self.bot_name = user['user']
        
        # Logs bot
        stramer = stream['streamer'].lower()
        print (f"{LOGS_PREFIX} Starting bot with user {self.bot_name} in stream {stramer}")
        
        # Call to parent constructor
        super().__init__ (
            proxy_server=proxy['host'],
            proxy_port=proxy['port'],
            start_killing=False,
        )
        
        # Test proxies loading a page
        self.set_page ("https://ipinfo.io/json")
        body = self.get_text ("body")
        if not '"ip":' in body:
            print (f"{LOGS_PREFIX} Error loading proxy {proxy['host']}:{proxy['port']}")
            return None
        
        # Login with cookies
        self.set_page ("https://www.twitch.tv/login")
        self.set_cookies (user['cookies'])
        
        # Validate login seaching login button
        self.set_page ("https://www.twitch.tv")
        login_button = self.get_elems (Bot.selectors['login_btn'])
        if login_button:
            
            # Disable user and debug error    
            print (f"{LOGS_PREFIX} Error login with user {self.bot_name}")
            Bot.api.disable_user (user['id'])
            return None
        
        # Open stream 
        self.streamer = stramer
        chat_link = f"https://www.twitch.tv/{stramer}/"
        self.set_page (chat_link)
        
        # Hide video
        player = self.get_elems (Bot.selectors["player"])
        if player:
            script = f"document.querySelector ('{Bot.selectors['player']}').style.display = 'none'"
            self.driver.execute_script (script)
        
        print (f"\t{LOGS_PREFIX} Bot waiting with user {self.bot_name} in stream {stramer}")
        
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
        self.self.end_browser ()
    
    def send_comment (self, api:Api): 
        """ Send comment with scraper
        
        Args:
            api (Api): api instance
        """
        
        print (f"{LOGS_PREFIX} Sending comment with bot {self.bot_name} in stream {self.streamer}: {self.comment_bot}...")
        
        # Random wait time
        sleep (random.randint (1, 5))
        
        # Validate if constrols are visible
        comment_textarea_visible = self.get_elems (Bot.selectors["comment_textarea"])
        comment_send_btn_visible = self.get_elems (Bot.selectors["comment_send_btn"])
        if not comment_textarea_visible or not comment_send_btn_visible:
            print (f"{LOGS_PREFIX} Error: inputs not visible")
            return False
            
        # Validate error messages
        warning_text = self.get_text (Bot.selectors["comment_warning_before"])
        if warning_text:
            print (f"{LOGS_PREFIX} Error: Inputs not available: {warning_text}")
            return False
        
        # Write message
        self.send_data (Bot.selectors["comment_textarea"], self.comment_bot)
        sleep (5)
        
        # Click in accept buttons
        for selector in Bot.selectors["comment_accept_buttons"]:
            
            accept_elem = self.get_elems (selector)
            if accept_elem:
                self.click (selector)
                
                # Write message (again)
                self.send_data (Bot.selectors["comment_textarea"], self.comment_bot)
                
        # Submit donation
        self.refresh_selenium ()
        # self.click (Bot.selectors["comment_send_btn"])
                
        warning_text = self.get_text (Bot.selectors["comment_warning_after"])
        if warning_text:
            print (f"{LOGS_PREFIX} Error: Donation not send: {warning_text}")
            return False
            
        print (f"{LOGS_PREFIX} Comment sent with bot {self.bot_name}: {self.comment_bot}")
        
        # Send comment to api
        api.save_comment_history (
            id_stream = self.id_stream,
            id_bot = self.id_bot,
            id_comment_mod = self.id_comment_mod,
            comment_bot = self.comment_bot,
            id_mod = self.id_mod,
        )
            
    def __str__ (self):
        
        return f"Bot ({self.bot_name}) in stream {self.id_stream}"