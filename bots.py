import os
import random
from time import sleep
from dotenv import load_dotenv
from api import Api
from bot import Bot
from threading import Thread

load_dotenv ()
BOTS_STREAM = int(os.getenv ("BOTS_STREAM"))
BOTS_IN_GROUP = int(os.getenv ("BOTS_IN_GROUP"))

LOGS_PREFIX = "(Bots Manager)"

class Bots ():
    
    def __init__ (self):
        """ Manage bots in streams """
        
        self.api = Api ()
        self.bots = {}
        """Strcuture
        {
            "stramer": [Bot1, Bot2, Bot3],
            ...
        }
        """
    
    def start_bots (self): 
        """ Auto start all required bots """
        
        # Update api data
        streams = self.api.get_streams ()
    
        # Validate if there are streams   
        if not streams:
            print (f"{LOGS_PREFIX} No streams available")
            return None
  
        # Start each bot in thread
        for stream in streams:
            
            # get current users from api
            users = self.api.get_users ()
            
            # End if there are no more users available
            if not users: 
                print (f"{LOGS_PREFIX} No users available")
                return None            
            
            # Log bots in stream
            print (f"{LOGS_PREFIX} Starting {BOTS_STREAM} bots in stream {stream['streamer']}\n")
            
            # Create bot groups
            bot_groups = BOTS_STREAM // BOTS_IN_GROUP
            for _ in range (bot_groups):
            
                group_bots = []
            
                for _ in range (BOTS_IN_GROUP): 
                    
                    if not users: 
                        print (f"{LOGS_PREFIX} No more users available")
                        continue
           
                    # Get random user and proxy
                    user = random.choice (users)
                    users.remove (user)
                    proxy = Bot.api.get_proxy ()
                    
                    # Inace bot
                    bot = Bot ()
                    
                    # Start bot
                    thread_obj = Thread (target=bot.start_bot, args=(stream, user, proxy))
                    thread_obj.start ()
                        
                    
                    # Save bot in group
                    group_bots.append (bot)
                    
                # Wait for bots be ready
                while True:
                    bot_no_ready = list (filter (lambda bot: not bot.ready, group_bots))
                    if bot_no_ready:
                        sleep (5)
                        continue
                    else:
                        break

                # Filter bot with and without error
                bots_ready = list (filter (lambda bot: not bot.error, group_bots))
                bots_error = list (filter (lambda bot: bot.error, group_bots))
                
                # Kill error bots
                for bot in bots_error:
                    bot.kill ()

                # Save bot ready instances
                streamer = stream["streamer"].lower()
                if streamer not in self.bots:
                    self.bots[streamer] = []
                    
                self.bots[streamer] += bots_ready
    
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
        bots = self.bots.get (streamer, [])
        
        if not bots:
            print (f"{LOGS_PREFIX} No bots available in stream {streamer}")
            return None
        
        # Send message with each bot in stream
        for bot in bots:
            
            comment_bot_data = self.api.get_random_comment (mod_comment)
            
            if not comment_bot_data:
                print (f"{LOGS_PREFIX} No random comment available for '{mod_comment}'")
                return None
            
            id_comment_mod = comment_bot_data["id_comment_mod"]
            comment_bot = comment_bot_data["comment"]
            
            # Update bot data
            bot.id_comment_mod = id_comment_mod
            bot.comment_bot = comment_bot
            bot.id_mod = id_mod
            
            thread_obj = Thread (target=bot.send_comment, args=(self.api,))
            thread_obj.start ()