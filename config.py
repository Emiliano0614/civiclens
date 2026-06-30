#this file is like a middleman between .env and the crate app
#it reads the file and converts them to actull environment variables
import os
from dotenv import load_dotenv
#loads the .env
load_dotenv()
class Config:
    #turn teh .env into variables
    SECRET_KEY = os.environ.get("SECRET_KEY")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
