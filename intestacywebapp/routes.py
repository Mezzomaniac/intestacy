import datetime

from flask import redirect, render_template, request, session, url_for#, flash, g
#import flask_sijax

from intestacywebapp import app
from intestacywebapp.forms import EstateForm, BeneficiariesForm
from intestacywebapp import functions
from intestacywebapp.models import *  # for testing only

ACT_URL = "https://www.legislation.wa.gov.au/legislation/statutes.nsf/RedirectURL?OpenAgent&query=mrdoc_37039.htm#_Toc493060114"

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', version=app.config['VERSION'])

@app.route('/act')
def act():
    return redirect(ACT_URL)

#@flask_sijax.route(app, "/test")
@app.route('/test', methods=['GET', 'POST'])
def test():
    return redirect(url_for('index'))
    
    from decimal import Decimal as D
    estate = Estate(datetime.date.today(), D('1234567.89'))
    estate.spouse = Relative('Spouse', 'Wifey')
    estate.defactos = [DeFacto(name='Angela', length=5), DeFacto(name='Pamela', length=2), DeFacto(name='Sandra', length=0), DeFacto(name='Rita', length=2)]
    estate.parents = [Relative('Parent', 'Mum'), Relative('Parent', 'Dad')]
    estate.siblings = [DescendibleRelative('Surviving Sibling 1', 'Little Bro'), DescendibleRelative('Surviving Sibling 2', 'Little Sis')]
    estate.siblings.append(DescendibleRelative('Non-surviving Sibling 1', 'Big Bro', False, [Relative('Grandchild', 'Dog'), Relative('Grandchild', 'Cat'), Relative('Grandchild', 'Fish')]))
    estate.siblings.append(DescendibleRelative('Non-surviving Sibling 2', 'Big Sis', False, [Relative('Grandchild', 'Monkey'), Relative('Grandchild', 'Dolphin'), Relative('Grandchild', 'Lion')]))
    estate.distribute()
    return render_template('distribution.html', title='Test', 
    estate=estate, dollar=functions.money_fmt)
    
    #def say_hi(obj_response, hello_from, hello_to):
        #obj_response.alert(f'Hi from {hello_from} to {hello_to}!')
        #obj_response.css('a', 'color', 'green')
        
    #if g.sijax.is_sijax_request:
        #g.sijax.register_callback('say_hi', say_hi)
        #return g.sijax.process_request()
    
    #def enable_q2(obj_response, q1):
        #print(q1)
        #if q1 == 'true':
             #obj_response.attr('#q2', 'disabled', False)
    
    #if g.sijax.is_sijax_request:
        #print(request.method)
        #print(obj_response)
        #g.sijax.register_callback('enable_q2', enable_q2)
        #return g.sijax.process_request()
    #print(request.method)
    #print(request.form)
    #return render_template('test.html', title='test', to='Memmy')
    
    form = BeneficiariesForm()
    specified_items = {
        'item_2': 50000,
        'item_3a_and_b': 75000, 
        'item_3bi': 6000, 
        'item_6': 6000}
    return render_template('form.html', title="Test", form=form, scripts=True, 
        specified_items=specified_items, value=80000)

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    form = TestForm()
    if form.validate_on_submit():
        return redirect(url_for('test1'))
    return render_template('test.html', title='test2', form=form)

@app.route('/calculate', methods=['GET', 'POST'])
@app.route('/calculate/estate', methods=['GET', 'POST'])
def calculate():
    functions.reset_session()
    form = EstateForm()
    if form.validate_on_submit():
        functions.update_session(form.data)
        functions.set_specified_items(form.deathdate.data)
        # TODO: compare deathdate to date of 2002 amendments
        return redirect(url_for('beneficiaries'))
    return render_template('form.html', title='Calculate Intestacy - Estate Details', form=form)

@app.route('/calculate/beneficiaries', methods=['GET', 'POST'])
def beneficiaries():
    form = BeneficiariesForm()
    if form.validate_on_submit():
        # TODO: For better UX, add client-side validation using html built-in validation and js validation
        functions.update_session(form.data)
        return redirect(url_for('distribution'))
    deathdate = functions.load_from_session('deathdate')
    fam_ct_am_act_02 = deathdate >= functions.FAM_CT_AM_ACT_02
    specified_items = functions.load_from_session('specified_items')
    value = functions.load_from_session('value')
    return render_template('form.html', 
        title="Calculate Intestacy - Beneficiaries' Details", 
        form=form, 
        scripts=True,
        specified_items=specified_items, 
        value=value,
        fam_ct_am_act_02=fam_ct_am_act_02)

@app.route('/calculate/distribution')
def distribution():
    estate = functions.calculate_distribution(**functions.load_session())
    # TODO: Also say whether a grant of LoA is required to get $ from a bank (AA s139)
    return render_template('distribution.html', title='Distribution', 
    estate=estate, dollar=functions.money_fmt)
    # TODO: Enable saving a set of beneficiaries to be recalculated with a different net value