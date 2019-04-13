import datetime
from decimal import Decimal
#from functools import lru_cache
from flask import session, json

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

def reset_session():
    for key in session.copy():
        if key != 'csrf_token':
            del session[key]
    #update_session({'issue': 0, 'parent': False, 'siblings': 0})

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
    excluded = ('csrf_token', 'submit')
    update = {k: jsonify(v) for k, v in data.iteritems() if k not in excluded}
    session.update(update)

def unjsonify(data):
    try:
        return datetime.datetime.strptime(json.loads(data), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return json.loads(data, parse_float=Decimal)

def load_from_session(key):
    try:
        return unjsonify(session[key])
    except KeyError:
        return

specified_items = {datetime.date(1977, 3, 1):
                       {'item 2': 50000,
                        'item 3(a) and (b)': 75000,
                        'item 3(b)(i)': 6000,
                        'item 6': 6000}#,
                   #datetime.date(date Administration Act passes):
                       #{'item 2': 435000,
                        #'item 3(a) and (b)': 650000,
                        #'item 3(b)(i)': 52000,
                        #'item 6': 52000}
                   }
# TODO: After Administration Amendment Act passes, automatically check for new orders under s 14A Administration Act

def set_specified_items():
    deathdate = load_from_session('deathdate')
    for date, amounts in sorted(specified_items.iteritems()):
        if deathdate >= date:
            update_session(amounts)
            return

def calculate():
    load = load_from_session
    value = load('value')
    item2 = load('item 2')
    item3aandb = load('item 3(a) and (b)')
    item3bi = load('item 3(b)(i)')
    item6 = load('item 6')
    spouse = load('spouse')
    defactos = load('defactos')
    defacto_rels = load('defacto_rels') or []
    partner = load('partner')
    issue = load('issue') or 0
    surviving_issue = load('surviving_issue')
    nonsurviving_issue = load('nonsurviving_issue')
    grandchildren_families = load('grandchildren_families')
    parent = load('parent') or False
    father = load('father')
    mother = load('mother')
    siblings = load('siblings') or 0
    surviving_siblings = load('surviving_siblings')
    nonsurviving_siblings = load('nonsurviving_siblings')
    nibling_families = load('nibling_families')
    auntuncles = load('auntuncles')
    surviving_auntuncles = load('surviving_auntuncles')
    nonsurviving_auntuncles = load('nonsurviving_auntuncles')
    cousin_families = load('cousin_families')
    
    beneficiaries = {}
    
    if partner and issue:
        # Item 2
        if spouse:
            spouse = not any(length >= 5 for length in defacto_rels)
        partner_share = min(value, item2)
        balance = max(value - item2, 0)
        division = 2 if issue == 1 else 3
        partner_share += balance / division
        balance -= balance / division
        partner_share = partner_share / (spouse + bool(defactos))
        if spouse:
            beneficiaries['Spouse'] = partner_share
        if defactos == 1:
            beneficiaries['De facto partner'] = partner_share
        else:
            for length in defacto_rels:
                beneficiaries['De facto partner ({} years)'.format(length)] = partner_share / defactos
        if surviving_issue == 1:
            beneficiaries['Surviving child'] = balance / issue
        else:
            for child in range(1, surviving_issue + 1):
                beneficiaries['Surviving child {}'.format(child)] = balance / issue
        for child, grandchildren in enumerate(grandchildren_families, 1):
            child_num = '' if nonsurviving_issue == 1 else ' {}'.format(child)
            for grandchild in range(1, grandchildren + 1):
                gchild_num = '' if grandchildren == 1 else ' {}'.format(grandchild)
                beneficiaries["Non-surviving child{}'s child{}".format(child_num, gchild_num)] = balance / issue / grandchildren
    elif partner and (parent or siblings):
        # Item 3
        if spouse:
            spouse = not any(length >= 5 for length in defacto_rels)
        partner_share = min(value, item3aandb)
        balance = max(value - item3aandb, 0)
        partner_share += balance / 2
        balance /= 2
        partner_share = partner_share / (spouse + bool(defactos))
        if spouse:
            beneficiaries['Spouse'] = partner_share
        if defactos == 1:
            beneficiaries['De facto partner'] = partner_share
        else:
            for length in defacto_rels:
                beneficiaries['De facto partner ({} years)'.format(length)] = partner_share / defactos
        if parent:
            parent_share = min(balance, item3bi)
            balance = max(balance - item3bi, 0)
            parent_share += balance / 2
            balance /= 2
            parent_share = parent_share / (father + mother)
            if father:
                beneficiaries['Father'] = parent_share
            if mother:
                beneficiaries['Mother'] = parent_share
        if surviving_siblings == 1:
            beneficiaries['Surviving sibling'] = balance / siblings
        else:
            for sibling in range(1, surviving_siblings + 1):
                beneficiaries['Surviving sibling {}'.format(sibling)] = balance / siblings
        for sibling, niblings in enumerate(nibling_families, 1):
            sib_num = '' if nonsurviving_siblings == 1 else ' {}'.format(sibling)
            for nibling in range(1, niblings + 1):
                nib_num = '' if niblings == 1 else ' {}'.format(nibling)
                beneficiaries["Non-surviving sibling{}'s child{}".format(sib_num, nib_num)] = balance / siblings / niblings
    elif partner:
        # Item 4
        if spouse:
            spouse = not any(length >= 5 for length in defacto_rels)
        partner_share = value / (spouse + bool(defactos))
        if spouse:
            beneficiaries['Spouse'] = partner_share
        if defactos == 1:
            beneficiaries['De facto partner'] = partner_share
        else:
            for length in defacto_rels:
                beneficiaries['De facto partner ({} years)'.format(length)] = partner_share / defactos
    elif issue:
        # Item 5
        if surviving_issue == 1:
            beneficiaries['Surviving child'] = value / issue
        else:
            for child in range(1, surviving_issue + 1):
                beneficiaries['Surviving child {}'.format(child)] = value / issue
        for child, grandchildren in enumerate(grandchildren_families, 1):
            child_num = '' if nonsurviving_issue == 1 else ' {}'.format(child)
            for grandchild in range(1, grandchildren + 1):
                gchild_num = '' if grandchildren == 1 else ' {}'.format(grandchild)
                beneficiaries["Non-surviving child{}'s child{}".format(child_num, gchild_num)] = value / issue / grandchildren
    elif parent and siblings:
        # Item 6
        parent_share = min(value, item6)
        balance = max(value - item6, 0)
        parent_share += balance / 2
        balance /= 2
        parent_share = parent_share / (father + mother)
        if father:
            beneficiaries['Father'] = parent_share
        if mother:
            beneficiaries['Mother'] = parent_share
        if surviving_siblings == 1:
            beneficiaries['Surviving sibling'] = balance / siblings
        else:
            for sibling in range(1, surviving_siblings + 1):
                beneficiaries['Surviving sibling {}'.format(sibling)] = balance / siblings
        for sibling, niblings in enumerate(nibling_families, 1):
            sib_num = '' if nonsurviving_siblings == 1 else ' {}'.format(sibling)
            for nibling in range(1, niblings + 1):
                nib_num = '' if niblings == 1 else ' {}'.format(nibling)
                beneficiaries["Non-surviving sibling{}'s child{}".format(sib_num, nib_num)] = balance / siblings / niblings
    elif parent:
        # Item 7
        share = value / (father + mother)
        if father:
            beneficiaries['Father'] = share
        if mother:
            beneficiaries['Mother'] = share
    elif siblings:
        # Item 8
        if surviving_siblings == 1:
            beneficiaries['Surviving sibling'] = value / siblings
        else:
            for sibling in range(1, surviving_siblings + 1):
                beneficiaries['Surviving sibling {}'.format(sibling)] = value / siblings
        for sibling, niblings in enumerate(nibling_families, 1):
            sib_num = '' if nonsurviving_siblings == 1 else ' {}'.format(sibling)
            for nibling in range(1, niblings + 1):
                nib_num = '' if niblings == 1 else ' {}'.format(nibling)
                beneficiaries["Non-surviving sibling{}'s child{}".format(sib_num, nib_num)] = value / siblings / niblings
    elif grandparents:
        # Item 9
        if grandparents == 1:
            beneficiaries['Grandparent'] = value
        else:
            for grandparent in range(1, grandparents + 1):
                beneficiaries['Grandparent {}'.format(grandparent)] = value / grandparents
    elif auntuncles:
        # Item 10
        if surviving_auntuncles == 1:
            beneficiaries['Surviving sibling'] = value / auntuncles
        else:
            for auntuncle in range(1, surviving_auntuncles + 1):
                beneficiaries['Surviving aunt/uncle {}'.format(auntuncle)] = value / auntuncles
        for auntuncle, cousins in enumerate(cousin_families, 1):
            au_num = '' if nonsurviving_auntuncles == 1 else ' {}'.format(auntuncle)
            for cousin in range(1, cousins + 1):
                cous_num = '' if cousins == 1 else ' {}'.format(cousin)
                beneficiaries["Non-surviving aunt/uncle{}'s child{}".format(au_num, cous_num)] = value / auntuncles / cousins
    else:
        # Item 11
        beneficiaries['Crown'] = value
    
    return beneficiaries

def money_fmt(number):
    quantized = number.quantize(Decimal('.01'))
    return '${:,.2f}'.format(quantized)

if __name__ == '__main__':
    dec = Decimal('1.5')
    date = datetime.date.today()
    print(jsonify([dec, date]))
    print(repr(unjsonify(jsonify(dec))))
    print(repr(unjsonify(jsonify(date))))

