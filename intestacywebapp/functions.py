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
<<<<<<< master
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
=======
            update_session(amounts)
            return

def calculate():
    load = load_from_session
    value = Decimal(load('value'))
    item2 = Decimal(load('item 2'))
    item3aandb = Decimal(load('item 3(a) and (b)'))
    item3bi = Decimal(load('item 3(b)(i)'))
    item6 = Decimal(load('item 6'))
    spouse = load('spouse')
    defactos = load('defactos')
    defacto_rels = load('defacto_rels') or []
    partner = load('partner')
    issue = load('issue') or 0
    surviving_issue = load('surviving_issue')
    nonsurviving_issue = load('nonsurviving_issue')
    grandchildren_families = load('grandchildren_families') or []
    parent = load('parent') or 0
    father = load('father')
    mother = load('mother')
    siblings = load('siblings') or 0
    surviving_siblings = load('surviving_siblings')
    nonsurviving_siblings = load('nonsurviving_siblings')
    nibling_families = load('nibling_families') or []
    grandparents = load('grandparents') or 0
    auntuncles = load('auntuncles') or 0
    surviving_auntuncles = load('surviving_auntuncles')
    nonsurviving_auntuncles = load('nonsurviving_auntuncles')
    cousin_families = load('cousin_families') or []

    beneficiaries = {}

    if partner and issue:
        # Item 2
        if spouse:
            spouse = not any(length >= 5 for length in defacto_rels)
        partner_share = min(value, item2)
        balance = max(value - item2, Decimal(0))
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
                beneficiaries[f'De facto partner ({length} years)'] = partner_share / defactos
        if surviving_issue == 1:
            beneficiaries['Surviving child'] = balance / issue
        else:
            for child in range(1, surviving_issue + 1):
                beneficiaries[f'Surviving child {child}'] = balance / issue
        for child, grandchildren in enumerate(grandchildren_families, 1):
            child_num = '' if nonsurviving_issue == 1 else f' {child}'
            for grandchild in range(1, grandchildren + 1):
                gchild_num = '' if grandchildren == 1 else f' {grandchild}'
                beneficiaries[f"Non-surviving child{child_num}'s child{gchild_num}"] = balance / issue / grandchildren
    elif partner and (parent or siblings):
        # Item 3
        if spouse:
            spouse = not any(length >= 5 for length in defacto_rels)
        partner_share = min(value, item3aandb)
        balance = max(value - item3aandb, Decimal(0))
        partner_share += balance / 2
        balance /= 2
        partner_share = partner_share / (spouse + bool(defactos))
        if spouse:
            beneficiaries['Spouse'] = partner_share
        if defactos == 1:
            beneficiaries['De facto partner'] = partner_share
        else:
            for length in defacto_rels:
                beneficiaries[f'De facto partner ({length} years)'] = partner_share / defactos
        if parent:
            parent_share = min(balance, item3bi)
            balance = max(balance - item3bi, Decimal(0))
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
                beneficiaries[f'Surviving sibling {sibling}'] = balance / siblings
        for sibling, niblings in enumerate(nibling_families, 1):
            sib_num = '' if nonsurviving_siblings == 1 else f' {sibling}'
            for nibling in range(1, niblings + 1):
                nib_num = '' if niblings == 1 else f' {nibling}'
                beneficiaries[f"Non-surviving sibling{sib_num}'s child{nib_num}"] = balance / siblings / niblings
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
                beneficiaries[f'De facto partner ({length} years)'] = partner_share / defactos
    elif issue:
        # Item 5
        if surviving_issue == 1:
            beneficiaries['Surviving child'] = value / issue
        else:
            for child in range(1, surviving_issue + 1):
                beneficiaries[f'Surviving child {child}'] = value / issue
        for child, grandchildren in enumerate(grandchildren_families, 1):
            child_num = '' if nonsurviving_issue == 1 else f' {child}'
            for grandchild in range(1, grandchildren + 1):
                gchild_num = '' if grandchildren == 1 else f' {grandchild}'
                beneficiaries[f"Non-surviving child{child_num}'s child{gchild_num}"] = value / issue / grandchildren
    elif parent and siblings:
        # Item 6
        parent_share = min(value, item6)
        balance = max(value - item6, Decimal(0))
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
                beneficiaries[f'Surviving sibling {sibling}'] = balance / siblings
        for sibling, niblings in enumerate(nibling_families, 1):
            sib_num = '' if nonsurviving_siblings == 1 else f' {sibling}'
            for nibling in range(1, niblings + 1):
                nib_num = '' if niblings == 1 else f' {nibling}'
                beneficiaries[f"Non-surviving sibling{sib_num}'s child{nib_num}"] = balance / siblings / niblings
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
                beneficiaries[f'Surviving sibling {sibling}'] = value / siblings
        for sibling, niblings in enumerate(nibling_families, 1):
            sib_num = '' if nonsurviving_siblings == 1 else f' {sibling}'
            for nibling in range(1, niblings + 1):
                nib_num = '' if niblings == 1 else f' {nibling}'
                beneficiaries[f"Non-surviving sibling{sib_num}'s child{nib_num}"] = value / siblings / niblings
    elif grandparents:
        # Item 9
        if grandparents == 1:
            beneficiaries['Grandparent'] = value
        else:
            for grandparent in range(1, grandparents + 1):
                beneficiaries[f'Grandparent {grandparent}'] = value / grandparents
    elif auntuncles:
        # Item 10
        if surviving_auntuncles == 1:
            beneficiaries['Surviving sibling'] = value / auntuncles
        else:
            for auntuncle in range(1, surviving_auntuncles + 1):
                beneficiaries[f'Surviving aunt/uncle {auntuncle}'] = value / auntuncles
        for auntuncle, cousins in enumerate(cousin_families, 1):
            au_num = '' if nonsurviving_auntuncles == 1 else f' {auntuncle}'
            for cousin in range(1, cousins + 1):
                cous_num = '' if cousins == 1 else f' {cousin}'
                beneficiaries[f"Non-surviving aunt/uncle{au_num}'s child{cous_num}"] = value / auntuncles / cousins
    else:
        # Item 11
        beneficiaries['Crown'] = value

    print(beneficiaries)
    return beneficiaries

def money_fmt(number):
    quantized = number.quantize(Decimal('.01'))
    return f'${quantized:,.2f}'

if __name__ == '__main__':
    dec = Decimal('1.5')
    date = datetime.date.today()
    print(jsonify([dec, date]))
    print(repr(unjsonify(jsonify(dec))))
    print(repr(unjsonify(jsonify(date))))
>>>>>>> origin/master
