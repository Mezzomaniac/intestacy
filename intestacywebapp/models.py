import datetime
from decimal import Decimal
from fractions import Fraction

from flask import json

from intestacywebapp import data

"""from . import db
from .functions import ordinal_fmt

class MonetaryAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric)

class Relative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    relation = db.Column(db.String, nullable=False)
    deceased = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String)
    length = db.Column(db.Numeric)
    share = db.Column(db.Numeric)
    notes = db.Column(db.String)
    
    def __repr__(self):
        return f'<{self.relation}>'
    
    def __str__(self):
        return self.name or f'{ordinal_fmt(self.id)} {self.relation}'"""

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Fraction):
            return {'__fraction__': (obj.numerator, obj.denominator)}
        elif isinstance(obj, datetime.date):
            return str(obj)
        elif isinstance(obj, (Relative, Estate)):
            return vars(obj)
        return json.JSONEncoder.default(self, obj)

class Relative:
    def __init__(self, relationship:str, name:str='', survived=True):
        self.relationship = relationship
        self.name = name
        self.survived = survived
        self.fixed = Decimal('0.00')
        self.interest = Decimal('0.00')
        self.fraction = Fraction(0)
        self.share = Decimal('0.00')
        self.notes = []
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.relationship}, {self.name}, survived={self.survived})'
    
    @property
    def percentage(self):
        decimal = Decimal(self.fraction.numerator) / Decimal(self.fraction.denominator) * 100
        quantized = decimal.quantize(Decimal('.01'))
        return f'{quantized:,.2f}%'

    def to_json(self):
        return json.dumps(self, cls=MyEncoder)

class DescendibleRelative(Relative):
    def __init__(self, relationship:str, name:str='', survived=True, issue:list=[]):
        super().__init__(relationship, name, survived)
        self.issue = issue
    
    def __repr__(self):
        return super().__repr__()[:-1] + f', issue={self.issue})'

class DeFacto(Relative):
    def __init__(self, relationship:str='De Facto Partner', name:str='', survived=True, length:int=0):
        super().__init__(relationship, name, survived)
        self.length = length
        lengths_dict = {0: ' \n(< 2 years)', 2: ' \n(< 5 years)', 5: ' \n(≥ 5 years)'}
        self.relationship += lengths_dict[length]

    def __repr__(self):
        return super().__repr__()[:-1] + f', length={self.length})'

class Estate:
    
    def __init__(self, deathdate:datetime.date, value:Decimal):
        self.deathdate = deathdate
        self.value = Decimal(value)
        self.set_specified_items()
        
        self.spouse = None
        self.defactos = []
        self.issue = []
        self.parents = []
        self.siblings = []
        self.grandparents = []
        self.auntuncles = []
        self.crown = None
    
    @property
    def eligible_spouse(self):
        return getattr(self.spouse, 'survived', False) and not any(defacto.length >= 5 for defacto in self.defactos)
    
    @property
    def eligible_defactos(self):
        return sum(defacto.length >= 2 for defacto in self.defactos)
    
    @property
    def eligible_partner(self):
        return self.eligible_spouse or bool(self.eligible_defactos)
    
    @property
    def eligible_issue(self):
        return sum(child.survived or bool(child.issue) for child in self.issue)
    
    @property
    def eligible_siblings(self):
        return sum(sibling.survived or bool(sibling.issue) for sibling in self.siblings)

    @property
    def eligible_auntuncles(self):
        return sum(auntuncle.survived or bool(auntuncle.issue) for auntuncle in self.auntuncles)
    
    def __iter__(self):
        if self.spouse:
            yield self.spouse
        for attr in ('defactos', 'issue', 'parents', 'siblings', 'grandparents', 'auntuncles'):
            for relative in getattr(self, attr):
                yield relative
        if self.crown:
            yield self.crown

    def set_specified_items(self):
        for date, amounts in sorted(data.SPECIFIED_ITEMS.items()):
            if self.deathdate >= date:
                self.specified_items = {item.upper(): Decimal(amount) for  item, amount in amounts.items()}
                for item, amount in self.specified_items.items():
                    setattr(self, item, amount)
                return
        raise ValueError(f'Date of death must not be earlier than {min(data.SPECIFIED_ITEMS):%-d %B %Y}')

    def to_json(self):
        return json.dumps(self, cls=MyEncoder)
    
    def distribute(self):
        if self.eligible_partner and self.eligible_issue:
            self.item2()
        elif self.eligible_partner and (self.parents or self.eligible_siblings):
            self.item3()
        elif self.eligible_partner:
            self.item4()
        elif self.eligible_issue:
            self.item5()
        elif self.parents and self.eligible_siblings:
            self.item6()
        elif self.parents:
            self.item7()
        elif self.eligible_siblings:
            self.item8()
        elif self.grandparents:
            self.item9()
        elif self.eligible_auntuncles:
            self.item10()
        else:
            self.item11()
    
    def item2(self):
        fixed = Decimal('0.00')
        interest = Decimal('0.00')
        partner_fraction = Fraction(1)
        issue_fraction = Fraction(0)
        
        partner_share = min(self.value, self.ITEM_2)
        balance = self.value - partner_share
        
        if balance:
            fixed = self.ITEM_2
            interest = fixed * (datetime.date.today() - self.deathdate).days / 365 * Decimal('0.05')
            interest = min(balance, interest)
            partner_share += interest
            balance -= interest
        if balance:
            division = 2 if self.eligible_issue == 1 else 3
            partner_fraction /= division
            issue_fraction = 1 -partner_fraction
            partner_share += balance / division
            balance -= balance / division

        self.distribute_to_partners(partner_share, partner_fraction, fixed, interest)
        self.distribute_to_descendible_relatives('issue', balance, issue_fraction)
        
    def item3(self):
        partner_fixed = Decimal('0.00')
        interest = Decimal('0.00')
        partner_fraction = Fraction(1)
        
        partner_share = min(self.value, self.ITEM_3A_AND_B)
        balance = self.value - partner_share
        
        if balance:
            partner_fixed = self.ITEM_3A_AND_B
            interest = partner_fixed * (datetime.date.today() - self.deathdate).days / 365 * Decimal('0.05')
            interest = min(balance, interest)
            partner_share += interest
            balance -= interest
        if balance:
            partner_fraction = Fraction(1, 2)
            partner_share += balance / 2
            balance /= 2

        self.distribute_to_partners(partner_share, partner_fraction, partner_fixed, interest)
        
        if not balance:
            return
        
        if self.parents:
            parent_fixed = Decimal('0.00')
            parent_fraction = Fraction(1, 2)
            siblings_fraction = Fraction(0)
            parent_share = min(balance, self.ITEM_3BI)
            balance -= parent_share
            if balance and self.eligible_siblings:
                parent_fixed = self.ITEM_3BI
                parent_fraction = Fraction(1, 4)
                siblings_fraction = Fraction(1, 4)
                parent_share += balance / 2
                balance /= 2
                
            parents = len(self.parents)
            for parent in self.parents:
                parent.share = parent_share / parents
                parent.fraction = parent_fraction / parents
                parent.fixed = parent_fixed / parents
        
        else:
            siblings_fraction = Fraction(1, 2)
        if self.eligible_siblings:
            self.distribute_to_descendible_relatives('siblings', balance, siblings_fraction)

    def item4(self):
        self.distribute_to_partners(self.value)
    
    def item5(self):
        self.distribute_to_descendible_relatives('issue', self.value)
    
    def item6(self):
        fixed = Decimal('0.00')
        parent_fraction = Fraction(1)
        siblings_fraction = Fraction(0)
        
        parent_share = min(self.value, self.ITEM_6)
        balance = self.value - parent_share
        
        if balance:
            fixed = self.ITEM_6
            parent_fraction = Fraction(1, 2)
            siblings_fraction = Fraction(1, 2)
            parent_share += balance / 2
            balance /= 2

        parents = len(self.parents)
        for parent in self.parents:
            parent.share = parent_share / parents
            parent.fraction = parent_fraction / parents
            parent.fixed = fixed / parents
        self.distribute_to_descendible_relatives('siblings', balance, siblings_fraction)

    def item7(self):
        parents = len(self.parents)
        for parent in self.parents:
            parent.share = self.value / parents
            parent.fraction = Fraction(1) / parents
    
    def item8(self):
        self.distribute_to_descendible_relatives('siblings', self.value)
    
    def item9(self):
        grandparents = len(self.grandparents)
        for grandparent in self.grandparents:
            grandparent.share = self.value / grandparents
            grandparent.fraction = Fraction(1) / grandparents
    
    def item10(self):
        self.distribute_to_descendible_relatives('auntuncles', self.value)
    
    def item11(self):
        self.crown = Relative('The Crown')
        self.crown.share = self.value
        self.crown.fraction = Fraction(1)
    
    def distribute_to_partners(self, share, fraction=Fraction(1), fixed=Decimal('0.00'), interest=Decimal('0.00')):
        portions = (self.eligible_spouse + bool(self.eligible_defactos))
        notes = ['Plus chattels.']
        if fraction < 1 or portions > 1 or self.eligible_defactos > 1:
            notes.append('May choose to receive home being lived in at date of death instead of monetary equivalent.')
        share /= portions
        fraction /= portions
        fixed /= portions
        interest /= portions
        if self.eligible_spouse:
            self.spouse.share = share
            self.spouse.fraction = fraction
            self.spouse.fixed = fixed
            self.spouse.interest = interest
            self.spouse.notes = notes
        for defacto in self.defactos:
            if defacto.length >= 2:
                defacto.share = share / self.eligible_defactos
                defacto.fraction = fraction / self.eligible_defactos
                defacto.fixed = fixed / self.eligible_defactos
                defacto.interest = interest / self.eligible_defactos
                defacto.notes = notes
        
    def distribute_to_descendible_relatives(self, relatives, share, fraction=Fraction(1)):
        portions = getattr(self, f'eligible_{relatives}')
        fraction /= portions
        share /= portions
        
        for relative in getattr(self, relatives):
            if relative.survived:
                relative.fraction = fraction
                relative.share = share
            else:
                issue = len(relative.issue)
                for child in relative.issue:
                    child.fraction = fraction / issue
                    child.share = share / issue
