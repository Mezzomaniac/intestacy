from flask import abort, redirect, render_template, url_for#, flash, g, request, session

from intestacywebapp import app
from intestacywebapp.forms import EstateForm, BeneficiariesForm, RecalculateForm
from intestacywebapp import data, processing, session_interface, utils
from intestacywebapp import _tests

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/act')
def act():
    #TODO: How do I get the true URL to show up when users mouse over the link?
    return redirect(data.ACT_URL)

@app.route('/test', methods=['GET', 'POST'])
def test():
    if not app.config['TESTING']:
        abort(403)
    return redirect(url_for('index'))

    return render_template('distribution.html', title='Test',
    estate = _tests.estate, dollar=utils.money_fmt)

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
    if not app.config['TESTING']:
        abort(403)
    form = TestForm()
    if form.validate_on_submit():
        return redirect(url_for('test1'))
    return render_template('test.html', title='test2', form=form)

@app.route('/calculate', methods=['GET', 'POST'])
@app.route('/calculate/estate', methods=['GET', 'POST'])
def calculate():
    session_interface.reset_session()
    form = EstateForm()
    if form.validate_on_submit():
        session_interface.update_session(form.data)
        session_interface.set_specified_items(form.deathdate.data)
        # TODO: compare deathdate to date of 2002 amendments
        return redirect(url_for('beneficiaries'))
    return render_template('form.html', title='Calculate Intestacy - Estate Details', form=form)

@app.route('/calculate/beneficiaries', methods=['GET', 'POST'])
def beneficiaries():
    form = BeneficiariesForm()
    if form.validate_on_submit():
        session_interface.update_session(form.data)
        return redirect(url_for('distribution'))
    deathdate = session_interface.load_from_session('deathdate')
    fam_ct_am_act_02 = deathdate >= data.FAM_CT_AM_ACT_02
    specified_items = session_interface.load_from_session('specified_items')
    value = session_interface.load_from_session('value')
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
        session_interface.update_session(form.data)
    estate = processing.calculate_distribution(**session_interface.load_session())
    # TODO: Also say whether a grant of LoA is required to get $ from a bank (AA s139)
    return render_template('distribution.html', title='Distribution',
    estate=estate, dollar=utils.money_fmt, form=form)
    # TODO: Enable saving a set of beneficiaries to be recalculated with a different net value
