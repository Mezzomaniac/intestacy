from flask import Flask
#from flask.ext.session import Session
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
#Session(app)

from . import routes