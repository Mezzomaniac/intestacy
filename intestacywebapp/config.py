import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex())
    VERSION = '1.3.0'

    #TESTING = True
    if TESTING:
        SEND_FILE_MAX_AGE_DEFAULT = 0  # For development only

    SESSION_PERMANENT = False
