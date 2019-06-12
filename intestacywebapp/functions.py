import datetime
from decimal import Decimal

from flask import session, json

from intestacywebapp.models import Relative, DescendibleRelative, DeFacto, Estate


def ordinal_fmt(n):
    if n is None:
        return ''
    elif n % 10 == 1 and n % 100 != 11:
        suffix = 'st'
    elif (n % 10 == 2 and n % 100 != 12) or n % 100 == 72:
        suffix = 'nd'
    elif n % 10 == 3 and n % 100 != 13:
        suffix = 'rd'
    else:
        suffix = 'th'
    return str(n) + suffix

def money_fmt(number):
    quantized = number.quantize(Decimal('.01'))
    return f'${quantized:,.2f}'

def reset_session():
    for key in session.copy():
        if key != 'csrf_token':
            del session[key]
            session.updated = True

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
        
def jsonify(data):
    return json.dumps(data, cls=MyEncoder)

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

def unjsonify(data):
    try:
        return datetime.datetime.strptime(json.loads(data), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return json.loads(data, parse_float=Decimal)

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

specified_items = {
    datetime.date(1977, 3, 1): 
        {'item_2': 50000, 
        'item_3a_and_b': 75000, 
        'item_3bi': 6000, 
        'item_6': 6000}#, 
    #datetime.date(date Administration Act passes): 
        #{'item_2': 435000, 
        #'item_3a_and_b': 650000, 
        #'item_3bi': 52000, 
        #'item_6': 52000}
    }
# TODO: Only start from 15/12/97, when death duties were abolished
# 21/09/02: parents need not be a mother and father
# TODO: After Administration Amendment Act passes, automatically check for new orders under s 14A Administration Act

FAM_CT_AM_ACT_02 = datetime.date(2002, 12, 1)

def set_specified_items(deathdate=None):
    if deathdate is None:
        deathdate = load_from_session('deathdate')
    #deathdate = datetime.datetime.strptime(deathdate, '%Y-%m-%d').date()
    for date, amounts in sorted(specified_items.items()):
        if deathdate >= date:
            update_session({'specified_items': amounts})
            return amounts

def calculate_distribution(
    deathdate, value, specified_items=None, 
    spouse_num=0, spouse='', defactos_num=0, defactos=[], 
    surviving_issue_num=0, surviving_issue=[], nonsurviving_issue_num=0, nonsurviving_issue=[], 
    parents_num=0, parents=[],
    surviving_siblings_num=0, surviving_siblings=[], nonsurviving_siblings_num=0, nonsurviving_siblings=[], 
    grandparents_num=0, grandparents=[],
    surviving_auntuncles_num=0, surviving_auntuncles=[], nonsurviving_auntuncles_num=0, nonsurviving_auntuncles=[]
    ):
    estate = Estate(deathdate, value)
    
    if spouse_num:
        estate.spouse = Relative('Spouse', spouse)
    estate.defactos = [DeFacto(**defacto) for defacto in defactos[:defactos_num]]

    estate.issue = [DescendibleRelative(f'Surviving Child {n}', child) 
        for n, child in enumerate(surviving_issue[:surviving_issue_num], 1)]
    estate.issue.extend(
        DescendibleRelative(f'Non-surviving Child {n}', child['name'], False, 
            [Relative('Grandchild', grandchild) for grandchild in child['issue'][:child['issue_num']]]) 
        for n, child in enumerate(nonsurviving_issue[:nonsurviving_issue_num], 1))

    estate.parents = [Relative('Parent', parent) for parent in parents[:parents_num]]
    
    estate.siblings = [DescendibleRelative(f'Surviving Sibling {n}', sibling) 
        for n, sibling in enumerate(surviving_siblings[:surviving_siblings_num], 1)]
    estate.siblings.extend(
        DescendibleRelative(f'Non-surviving Sibling {n}', sibling['name'], False, 
            [Relative('Niece/Nephew', nibling) for nibling in sibling['issue'][:sibling['issue_num']]]) 
        for n, sibling in enumerate(nonsurviving_siblings[:nonsurviving_siblings_num], 1))

    estate.grandparents = [Relative('Grandparent', grandparent) for grandparent in grandparents[:grandparents_num]]

    estate.auntuncles = [DescendibleRelative(f'Surviving Aunt/Uncle {n}', auntuncle) 
        for n, auntuncle in enumerate(surviving_auntuncles[:surviving_auntuncles_num], 1)]
    estate.auntuncles.extend(
        DescendibleRelative(f'Non-surviving Aunt/Uncle {n}', auntuncle['name'], False, 
            [Relative('Cousin', cousin) for cousin in auntuncle['issue'][:auntuncle['issue_num']]]) 
        for n, auntuncle in enumerate(nonsurviving_auntuncles[:nonsurviving_auntuncles_num], 1))

    estate.distribute()
    return estate