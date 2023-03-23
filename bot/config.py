import os

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("FENIXWBBOT_API_TOKEN")

MONGO_HOST = "clusterfenix.unccemf.mongodb.net/?retryWrites=true&w=majority"
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
