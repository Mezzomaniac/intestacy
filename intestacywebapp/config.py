import os

class Config:
    SECRET_KEY = os.urandom(16)
    VERSION = '2.1.0'
    SESSION_PERMANENT = False
    #PERMANENT_SESSION_LIFETIME = 60