from flask import Flask
from bot import Bot

app = Flask(__name__)
BOTS_MANAGER = None

@app.route('/')
def start_bots (): 
    
    # Start new bots instances 
    BOTS_MANAGER.start_bots()
    
    return {
        "status": "ok",
        "message": "Bots started"
    }
    
if __name__ == "__main__":
    BOTS_MANAGER = Bot ()
    app.run(debug=True)