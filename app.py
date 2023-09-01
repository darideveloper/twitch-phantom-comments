from flask import Flask, request
from bot import Bot

app = Flask(__name__)
BOTS_MANAGER = None

@app.get('/')
def start_bots (): 
    
    # Start new bots instances 
    BOTS_MANAGER.start_bots()
    
    return {
        "status": "ok",
        "message": "Bots started"
    }
    
    
@app.post('/comment/')
def comment ():
    
    # Get json data
    data = request.get_json()
    mod = data.get ("mod", "")
    comment = data.get ("comment", "")
    
    # Validate data
    if "" in [mod, comment]:
        return {
            "status": "error",
            "message": "Invalid data"
        }
        
    # Add comment to queue
    BOTS_MANAGER.add_comment (mod, comment)
    

if __name__ == "__main__":
    BOTS_MANAGER = Bot ()
    app.run(debug=True)