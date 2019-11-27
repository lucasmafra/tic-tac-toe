import json

def to_bytes(string):
  return bytes(string, 'utf-8')

def from_bytes(b):
  return b.decode('utf-8')

def serialize(data):
  return to_bytes(json.dumps(data))

def deserialize(data):
  return json.loads(from_bytes(data))
