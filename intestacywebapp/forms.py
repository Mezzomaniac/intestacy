import datetime

from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, RadioField, SelectField, StringField, SubmitField
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.validators import InputRequired, NumberRange, ValidationError

from intestacywebapp.utils import ordinal_fmt


class MoneyField(DecimalField):
    def __init__(self, label='', validators=[], **kwargs):
        kwargs.setdefault('render_kw', {}).setdefault('step', '0.01')
        super().__init__(label, validators, **kwargs)

#class RelativeForm(FlaskForm):
    #class Meta:
        #csrf = False
    
    #survived = RadioField('Was the Deceased survived by {}?', 
        #validators=[InputRequired()], 
        #choices=[
            #(0, 'No'), 
            #(1, 'Yes')],
        #default=0,
        #coerce=bool)
    #name = StringField('(Optional) What is their name?')

    '''def __init__(self, relative, **kwargs):
        super().__init__(**kwargs)
        self.survived.label.text = self.survived.label.text.format(relative)'''

class DeFactoInfoForm(FlaskForm):
    class Meta:
        csrf = False
    
    length = RadioField('How long did the de facto relationship last?', 
        #validators=[InputRequired()], 
        choices=[
            (0, 'Less than 2 years'), 
            (2, '2 or more but less than 5 years'),
            (5, '5 or more years')],
        default=0,
        coerce=int)
    name = StringField(
        "(Optional) What is the de facto partner's name?", 
        render_kw={'placeholder': 'De Facto Partner'})
        # TODO: Number the placeholder text 'De Facto Partner 1' etc

class RelativeNumberField(SelectField):
    def __init__(self, relative='', num=None, origin='Deceased', validators=None, max=20, **kwargs):
        ordinal = ordinal_fmt(num)
        if ordinal:
            ordinal += ' '
        # TODO: Use {{ loop.index }} for num
        label = f"How many {relative} did the {ordinal}{origin} have at the date of the Deceased's death?"
        if validators is None:
            validators = [InputRequired('Please type a number'), NumberRange(min=0)]
        choices = [(n, str(n)) for n in range(max + 1)]
        kwargs.setdefault('render_kw', {}).setdefault('required', True)
        class_ = kwargs['render_kw'].get('class', '').split()
        if 'relative-number-field' not in class_:
            class_.append('relative-number-field')
        kwargs['render_kw']['class'] = ' '.join(class_)
        super().__init__(label, validators=validators, default=0, choices=choices, coerce=int, **kwargs)

def nonsurviving_relative_form_builder(origin, child):
    
    class NonsurvivingRelativeForm(FlaskForm):
        class Meta:
            csrf = False
        
        name = StringField(
            f"(Optional) What is the non-surviving {origin}'s name?",
            render_kw={'placeholder': origin.title()}) 
        issue_num = RelativeNumberField(
            'living children', origin=f'non-surviving {origin}', 
            validators=[NumberRange(min=0)], 
            render_kw={'required': False})
        issue = FieldList(
            StringField(
                f"(Optional) What is the surviving {child}'s name?", 
                render_kw={'placeholder': child.title()}), 
            min_entries=20)
    
    return NonsurvivingRelativeForm

#class DeFactoForm(FlaskForm):
    #class Meta:
        #csrf = False
    
    #number = FormField(RelativeNumberForm, 'De factos')
    #defacto_rels = RelativeNumberField('de facto partners with whom the Deceased lived\
#<span class="if-spouse" hidden>\
#, during which time the Deceased did not live as the husband or wife of their spouse,\
#</span>')
    #defactos = FieldList(FormField(DeFactoInfoForm, 'De facto partner'), 
        #'De facto partners', 
        #min_entries=10, 
        #render_kw={'hidden': True})

class TestForm(FlaskForm):
    a = StringField('string')
    submit = SubmitField('Submit')

    def __init__(self, relative, **kwargs):
        super().__init__(**kwargs)

class EstateForm(FlaskForm):
    deathdate = DateField(
        'What is the date of death?', 
        [InputRequired('Please enter a valid date')], 
        format='%Y-%m-%d', render_kw={'placeholder': 'yyyy-mm-dd', 'min': '1997-12-15'})
    
    #chattels = MoneyField(
        #"What is the value of household chattels included in the Deceased's property?", 
        #[InputRequired(), NumberRange(
            #min=0, 
            #message='Value cannot be negative.')])
            
    value = MoneyField(
        'What is the net value of (the intestate portion of) the estate?', 
        [InputRequired('Please type a number'), NumberRange(
            min=1, 
            message='Estate value must be at least $1.00')],
        render_kw={'min': '1'})
            
    submit = SubmitField('Next')
    
    def validate_deathdate(form, field):
        if field.data < datetime.date(1997, 12, 15):
            raise ValidationError('''Sorry, we don't currently deal with death dates before <time datetime="1997-12-15">15 December 1997</time>, when death duties were abolished in WA.
If this missing feature is important to you, please let us know by <a href="mailto:jeremylondon@outlook.com.au?subject=Intestacy%20Calculator">sending us feedback.</a>.''')


class BeneficiariesForm(FlaskForm):
    #spouse = FormField(RelativeForm, 'Spouse')
    spouse_num = RadioField('Was the Deceased survived by a spouse?', 
        validators=[InputRequired()], 
        choices=[
            (0, 'No'), 
            (1, 'Yes')],
        default=0,
        coerce=int,
        render_kw={'class': 'spouse'})
    spouse = StringField(
        "(Optional) What is the spouse's name?", 
        render_kw={
            'class': 'spouse if-spouse', 
            'hidden': 'hidden', 
            'placeholder': 'Spouse'})
    defactos_num = RelativeNumberField('de facto partners with whom the Deceased lived\
<span class="if-spouse" hidden>\
, during which time the Deceased did not live as the husband or wife of their spouse,\
</span>',
        max=4, 
        render_kw={'class': 'if-fam-ct-am-act-02 defactos'})
    defactos = FieldList(
        FormField(
            DeFactoInfoForm, 
            'De facto partner'), 
        'De facto partners', 
        min_entries=4, 
        render_kw={'class': 'defactos'})
    
    surviving_issue_num = RelativeNumberField(
        'living children', 
        render_kw={'class': 'issue if-no-partner if-item2'})
    surviving_issue = FieldList(
        StringField(
            "(Optional) What is the surviving child's name?",
            render_kw={'placeholder': 'Child'}), 
        'Surviving children', 
        render_kw={'class': 'issue, if-no-partner if-item2'}, 
        min_entries=20)
    nonsurviving_issue_num = RelativeNumberField(
        'deceased children who left children', 
        render_kw={'class': 'issue if-no-partner if-item2'})
    nonsurviving_issue = FieldList(
        FormField(
            nonsurviving_relative_form_builder('child', 'grandchild')),
        'Non-surviving children', 
        render_kw={'class': 'issue, if-no-partner if-item2'}, 
        min_entries=20)
    
    parents_num = RelativeNumberField(
        'living parents', 
        max=2, 
        render_kw={'class': 'parents'})
    parents = FieldList(
        StringField(
            "(Optional) What is the surviving parent's name?",
            render_kw={'placeholder': 'Parent'}), 
        'Parents', 
        render_kw={'class': 'parents'}, 
        min_entries=2)
    # TODO: Refer to 'mother' & 'father' if < 21/9/02. 

    surviving_siblings_num = RelativeNumberField(
        'living siblings (including half-siblings)', 
        render_kw={'class': 'siblings'})
    surviving_siblings = FieldList(
        StringField(
            "(Optional) What is the surviving sibling's name?",
            render_kw={'placeholder': 'Sibling'}), 
        'Surviving siblings', 
        render_kw={'class': 'siblings'}, 
        min_entries=20)
    nonsurviving_siblings_num = RelativeNumberField(
        'deceased siblings (including half-siblings) who left children', 
        render_kw={'class': 'siblings'})
    nonsurviving_siblings = FieldList(
        FormField(
            nonsurviving_relative_form_builder('sibling', 'niece or nephew')),
        'Non-surviving siblings', 
        render_kw={'class': 'siblings'}, 
        min_entries=20)

    grandparents_num = RelativeNumberField(
        'living grandparents', 
        max=4, 
        render_kw={'class': 'grandparents'})
    grandparents = FieldList(
        StringField(
            "(Optional) What is the surviving grandparent's name?",
            render_kw={'placeholder': 'Grandparent'}), 
        'Grandparents', 
        render_kw={'class': 'grandparents'}, 
        min_entries=4)

    surviving_auntuncles_num = RelativeNumberField(
        'living aunts and uncles (including half-blood relations)', 
        max=40, 
        render_kw={'class': 'auntuncles'})
    surviving_auntuncles = FieldList(
        StringField(
            "(Optional) What is the surviving aunt/uncle's name?", 
            render_kw={'placeholder': 'Aunt/Uncle'}), 
        'Surviving aunts & uncles', 
        render_kw={'class': 'auntuncles'}, 
        min_entries=40)
    nonsurviving_auntuncles_num = RelativeNumberField(
        'deceased aunts and uncles (including half-blood relations) who left children', 
        max=40, 
        render_kw={'class': 'auntuncles'})
    nonsurviving_auntuncles = FieldList(
        FormField(
            nonsurviving_relative_form_builder('aunt/uncle', 'cousin')),
        'Non-surviving aunts & uncles', 
        render_kw={'class': 'auntuncles'}, 
        min_entries=40)

    submit = SubmitField('Calculate distribution')

    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)
        #self.spouse.survived.label.text = self.spouse.survived.label.text.format('a spouse')

class RecalculateForm(FlaskForm):
    value = MoneyField(
        'Re-calculate with a different value:', 
        [InputRequired('Please type a number'), NumberRange(
            min=1, 
            message='Estate value must be at least $1.00')],
        render_kw={'min': '1'})
            
    submit = SubmitField('Go')


'''def questions2a_form_builder(defacto_rels):
    class Questions3Form(FlaskForm):
        pass

    for i in range(defacto_rels):
        setattr(Questions3Form, 'defacto_{}'.format(i), DecimalField('De facto relationship {}'.format(i+1)))

    setattr(Questions3Form, 'submit', SubmitField('Next'))
    return Questions3Form()
    
    #indexes = range(defacto_rels)
    
    class Questions2AForm(FlaskForm):
        defactos = FieldList(FormField(DeFactoForm, 'De facto partner'), 'De facto partners', min_entries=defacto_rels)
        submit = SubmitField('Next')
    
    return Questions2AForm()
    
    def __init__(self, defacto_rels, **kwargs):
        self.defactos = FieldList(DecimalField('Length'), 'How many years did each de facto relationship last?', min_entries=defacto_rels)
        super(Questions3Form, self).__init__(**kwargs)'''
