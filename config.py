import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
    DEBUG = True
    
class TestingConfig:
   SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"
   DEBUG=True
   CACHE_TYPE='SimpleCache'
   SQLALCHEMY_TRACK_MODIFICATIONS=False

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI")