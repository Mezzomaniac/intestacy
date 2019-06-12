from flask import Flask
#from flask.ext.session import Session
#from flask_sqlalchemy import SQLAlchemy
#from flask_sijax import Sijax
from intestacywebapp.config import Config

app = Flask(__name__)
app.config.from_object(Config)

#db = SQLAlchemy(app)
#app.config['SESSION_SQLALCHEMY'] = db
#Session(app)
#db.create_all()

#Sijax(app)

from intestacywebapp import routes#, models