from flask import Flask
from intestacywebapp.config import Config
from intestacywebapp.utils import money_fmt
from intestacywebapp.data import ACT_URL

app = Flask(__name__)
app.config.from_object(Config)

app.context_processor(lambda: {'act_url': ACT_URL})
app.template_filter('dollar')(money_fmt)

from intestacywebapp import routes
