# Define message types (join, move, state)
# Encode and decode JSON packets
# Ensure consistent client–server communication

import json

def encode(data):
    return (json.dumps(data) + "\n").encode()

def decode(data):
    return json.loads(data)
