import os

class Config:
    SECRET_KEY = os.urandom(16)
    VERSION = '2.2.1'
    
    #TESTING = True
    #SEND_FILE_MAX_AGE_DEFAULT = 0  # For development only
    
    SESSION_PERMANENT = False
    #PERMANENT_SESSION_LIFETIME = 60
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_ECHO = True
    #SESSION_TYPE = 'sqlalchemy'
    #SESSION_TYPE = 'filesystem'
    
    #SIJAX_STATIC_PATH = os.path.join('.', 
        #os.path.dirname(__file__), 
        #'static/js/sijax/')
    #SIJAX_JSON_URI = '/static/js/sijax/json2.js'