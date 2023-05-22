import os

class Config:
    SECRET_KEY = os.urandom(16)
    VERSION = '1.2.2'
    
    #TESTING = True
    #SEND_FILE_MAX_AGE_DEFAULT = 0  # For development only
    
    SESSION_PERMANENT = False
