from flask import Flask, request
from bot import Bot

app = Flask(__name__)
BOTS_MANAGER = None

@app.get('/')
def start_bots (): 
    
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
    BOTS_MANAGER.send_comments (comment, mod)

    return {
        "status": "ok",
        "message": "Sending comments"
    }

if __name__ == "__main__":
    
    BOTS_MANAGER = Bot ()
    
    # Start new bots instances 
    BOTS_MANAGER.start_bots()
    
    # DEBUG: test send comment
    from time import sleep
    sleep (30)
    
    # # Test invalid comment
    # stramer = "pipevillanu3va"
    # mod = "daridev99"
    # mod_comment = "holiii"
    # BOTS_MANAGER.send_comments (stramer, mod, mod_comment)
    
    # Test valid comment
    stramer = "aristoristo"
    id_mod = 3
    mod_comment = ":3"
    BOTS_MANAGER.send_comments (stramer, id_mod, mod_comment)
    
    # DEBUG: REACTIVATE
    # app.run(debug=True)