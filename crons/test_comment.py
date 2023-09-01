import requests

# Request to flask home
res = requests.post('http://localhost:5000/comment/', json={
    "mod": "daridev99",
    "comment": ":3"
})
