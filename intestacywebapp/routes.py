import datetime

from flask import redirect, render_template, url_for#, flash, g, request, session

from intestacywebapp import app
from intestacywebapp.forms import EstateForm, BeneficiariesForm, RecalculateForm
from intestacywebapp import functions
from intestacywebapp import tests

ACT_URL = "https://www.legislation.wa.gov.au/legislation/statutes.nsf/RedirectURL?OpenAgent&query=mrdoc_37039.htm#_Toc493060114"

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', version=app.config['VERSION'])

@app.route('/act')
def act():
    return redirect(ACT_URL)

@app.route('/test', methods=['GET', 'POST'])
def test():
    return redirect(url_for('index'))
    
    return render_template('distribution.html', title='Test', 
    estate=tests.estate, dollar=functions.money_fmt)
    
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

@app.route('/calculate/distribution', methods=['GET', 'POST'])
def distribution():
    form = RecalculateForm()
    if form.validate_on_submit():
        functions.update_session(form.data)
    estate = functions.calculate_distribution(**functions.load_session())
    # TODO: Also say whether a grant of LoA is required to get $ from a bank (AA s139)
    return render_template('distribution.html', title='Distribution', 
    estate=estate, dollar=functions.money_fmt, form=form)
    # TODO: Enable saving a set of beneficiaries to be recalculated with a different net value