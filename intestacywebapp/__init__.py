from flask import Flask
from intestacywebapp.config import Config

app = Flask(__name__)
app.config.from_object(Config)

from intestacywebapp import routes
