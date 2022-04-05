import datetime
from decimal import Decimal
from flask import json, session
from intestacywebapp.data import SPECIFIED_ITEMS

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
        
def jsonify(data):
    return json.dumps(data, cls=JSONEncoder)

def unjsonify(data):
    try:
        return datetime.datetime.strptime(json.loads(data), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return json.loads(data, parse_float=Decimal)

# TODO: Create class inheriting from flask SessionInterface

def reset_session():
    for key in session.copy():
        if key != 'csrf_token':
            del session[key]
            session.updated = True

def update_session(data):
    '''Update session from form data.'''
    
    excluded = ('csrf_token', 'submit')
    update = {}
    for key, value in data.items():
        if key in excluded:
            continue
        try:
            update[key] = jsonify({k: v for k, v in value.items() if k not in excluded})
        except AttributeError:
            update[key] = jsonify(value)
    session.update(update)

def set_specified_items(deathdate=None):
    if deathdate is None:
        deathdate = load_from_session('deathdate')
    for date, amounts in reversed(sorted(SPECIFIED_ITEMS.items())):
        if deathdate >= date:
            update_session({'specified_items': amounts})
            return amounts

def load_from_session(key, *keys):
    try:
        value = unjsonify(session[key])
    except KeyError:
        return
    for key in keys:
        value = value[key]
    return value

def load_session():
    return {k: unjsonify(v) for k, v in session.items() if k != 'csrf_token'}
