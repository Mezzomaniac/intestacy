import os
from flask import Flask
#from flask.ext.session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['VERSION'] = '2'
app.config['SESSION_PERMANENT'] = False
#app.config['PERMANENT_SESSION_LIFETIME'] = 60
#Session(app)

from webapp import routes
