from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, DateField, DecimalField, IntegerField, FieldList
from wtforms.validators import InputRequired, DataRequired, NumberRange
from .functions import ordinal_fmt

class SurvivingRelativeField(BooleanField):
    def __init__(self, relative, **kwargs):
        label = f"Was the Deceased surivived by {relative}?"
        super().__init__(label, **kwargs)

class RelativeNumberField(IntegerField):
    def __init__(self, relative, num=None, origin='Deceased', validators=None, **kwargs):
        ordinal = ordinal_fmt(num)
        if ordinal:
            ordinal += ' '
        label = f"How many {relative} did the {ordinal}{origin} have at the date of the Deceased's death?"
        super().__init__(label, validators, **kwargs)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

class TestForm(FlaskForm):
    a = StringField('string')
    #b = DateField('b (ddmmyy)', format='%d%m%y')
    c = DecimalField('decimal')
    #group = [a, b, c]
    #fields = [StringField('d')]
    #e = StringField('e')
    submit = SubmitField('Submit')

class Test2Form(FlaskForm):
    a = StringField('string')
    #b = DateField('b (ddmmyy)', format='%d%m%y')
    c = DecimalField('decimal')
    #group = [a, b, c]
    #fields = [StringField('d')]
    #e = StringField('e')
    submit = SubmitField('Submit')

class Questions1Form(FlaskForm):
    deathdate = DateField('What is the date of death (dd/mm/yyyy)?', [DataRequired()], format='%d/%m/%Y')
    value = DecimalField('What is the net value of the estate?', [InputRequired(), NumberRange(min=1)])
    spouse = SurvivingRelativeField('a spouse')
    submit = SubmitField('Next')

class Questions2Form(FlaskForm):
    defactos = RelativeNumberField('de facto partners with whom the Deceased lived as de facto partner for at least 2 years{}', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Next')
    
    def __init__(self, spouse, **kwargs):
        super().__init__(**kwargs)
        self.defactos.label.text = self.defactos.label.text.format(
            ', during which time the Deceased did not live as the husband or wife of their spouse,' if spouse else '')

def questions2a_form_builder(defactos):
    '''class Questions3Form(FlaskForm):
        pass

    for i in range(defactos):
        setattr(Questions3Form, 'defacto_{}'.format(i), DecimalField('De facto relationship {}'.format(i+1)))

    setattr(Questions3Form, 'submit', SubmitField('Next'))
    return Questions3Form()'''
    
    #indexes = range(defactos)
    
    class Questions2AForm(FlaskForm):
        defacto_rels = FieldList(DecimalField('Length in years', [InputRequired(), NumberRange(min=2.0)]), 'How long did each de facto relationship last?', min_entries=defactos)
        submit = SubmitField('Next')
    
    return Questions2AForm()
    
    '''def __init__(self, defactos, **kwargs):
        self.defacto_rels = FieldList(DecimalField('Length'), 'How many years did each de facto relationship last?', min_entries=defactos)
        super(Questions3Form, self).__init__(**kwargs)
        #self.defacto_rels = FieldList(DecimalField('Length'), 'How many years did each de facto relationship last?', min_entries=defactos)'''

class Questions3Form(FlaskForm):
    surviving_issue = RelativeNumberField('living children', validators=[InputRequired(), NumberRange(min=0)])
    nonsurviving_issue = RelativeNumberField('deceased children who left children', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Next')

def family_form_builder(families, origin, entries):
    
    class FamilyForm(FlaskForm):
        pass
    
    label = f'How many living children did each non-surviving {origin} of the Deceased leave?'
    origin = f'non-surviving {origin}'
    validators = [InputRequired(), NumberRange(min=1)]
    fieldlist = FieldList(
        RelativeNumberField('living children', origin=origin, validators=validators), 
        label, min_entries=entries)
    setattr(FamilyForm, f'{families}_families', fieldlist)
    FamilyForm.submit = SubmitField('Next')
    
    return FamilyForm()

'''def questions3a_form_builder(nonsurviving_issue):
    class Questions3AForm(FlaskForm):
        grandchildren_families = FieldList(RelativeNumberField('living children', origin='non-surviving child', validators=[InputRequired(), NumberRange(min=1)]), 'How many living children did each non-surviving child of the Deceased leave?', min_entries=nonsurviving_issue)
        submit = SubmitField('Next')
    
    return Questions3AForm()'''
    
class Questions4Form(FlaskForm):
    father = SurvivingRelativeField('their father')
    mother = SurvivingRelativeField('their mother')
    submit = SubmitField('Next')

class Questions5Form(FlaskForm):
    surviving_siblings = RelativeNumberField('living siblings', validators=[InputRequired(), NumberRange(min=0)])
    nonsurviving_siblings = RelativeNumberField('deceased siblings who left children', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Next')

'''def questions5a_form_builder(nonsurviving_siblings):
    class Questions5AForm(FlaskForm):
        nibling_families = FieldList(RelativeNumberField('living children', origin='non-surviving sibling', validators=[InputRequired(), NumberRange(min=1)]), 'How many living children did each non-surviving sibling of the Deceased leave?', min_entries=nonsurviving_siblings)
        submit = SubmitField('Next')
    
    return Questions5AForm()'''

class Questions6Form(FlaskForm):
    grandparents = RelativeNumberField('living grandparents', validators=[InputRequired(), NumberRange(min=0, max=4)])
    submit = SubmitField('Next')

class Questions7Form(FlaskForm):
    surviving_auntuncles = RelativeNumberField('living aunts and uncles', validators=[InputRequired(), NumberRange(min=0)])
    nonsurviving_auntuncles = RelativeNumberField('deceased aunts and uncles who left children', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Next')
