from flask import Flask, request
from bots import Bots

app = Flask(__name__)
BOTS_MANAGER = None

@app.get('/')
def start_bots (): 
    
    # Start new bot instances
    BOTS_MANAGER.start_bots()
    
    return {
        "status": "ok",
        "message": "Bots started"
    }
    
@app.post('/comment/')
def comment ():
    
    # Get json data
    data = request.get_json()
    streamer = data.get ("streamer", "")
    mod = data.get ("mod", "")
    comment = data.get ("comment", "")
    
    # Validate data
    if "" in [mod, comment, streamer]:
        return {
            "status": "error",
            "message": "Invalid data"
        }
        
    # Add comment to queue
    BOTS_MANAGER.send_comments (streamer, mod, comment)

    return {
        "status": "ok",
        "message": "Sending comments"
    }

if __name__ == "__main__":
   
    # DEBUG WITHOUT API >>> 
    # BOTS_MANAGER = Bots ()
    
    # # Start new bots instances 
    # BOTS_MANAGER.start_bots()
    
    # # # DEBUG: test send comment
    # from time import sleep
    # sleep (80)
    
    # # Test comment
    # stramer = "Kiingyeye".lower()
    # id_mod = 3
    # mod_comment = ":3"
    # BOTS_MANAGER.send_comments (stramer, id_mod, mod_comment)
    # <<< DEBUG WITHOUT API 
    
    # Initialize bots manager
    BOTS_MANAGER = Bots ()
    
    # Start flask app
    app.run(debug=True)