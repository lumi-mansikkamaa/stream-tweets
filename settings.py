TRACK_TERMS = ["trump", "clinton", "hillary clinton", "donald trump"]
CONNECTION_STRING = "sqlite:///tweets.db"
JSON_NAME = "tweets.json"
TABLE_NAME = "tweets"

try:
    from private import *
except  Exception:
    pass