from flask import abort, redirect, render_template, request, url_for
try:
    import git
except ImportError:
    pass

from intestacywebapp import app
from intestacywebapp.forms import EstateForm, BeneficiariesForm, RecalculateForm
from intestacywebapp import data, processing, session_interface, utils
from intestacywebapp import _tests

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/test', methods=['GET', 'POST'])
def test():
    if not app.config['TESTING']:
        abort(403)
    
    estate = _tests.estate
    import datetime
    estate.deathdate = datetime.date(2000, 1, 1)
    estate.distribute()
    
    return render_template('distribution.html', title='Test',
    estate = estate, form=RecalculateForm())

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
    jsconstants = {"specified_items": specified_items, "value": str(value), "fam_ct_am_act_02": int(fam_ct_am_act_02)}
    return render_template('form.html',
        title="Calculate Intestacy - Beneficiaries' Details",
        form=form,
        jsconstants=jsconstants)

@app.route('/calculate/distribution', methods=['GET', 'POST'])
def distribution():
    # TODO: Make whether distribution date info and recalculation field appear be dependant on whether interest applies
    # That might require switching form.html to be includable instead of using extend
    # Or including scripts.html from distribution.html, not just form.html
    
    # TODO: Warn if increasing estate value could require inclusion of more beneficiaries
    
    form = RecalculateForm()
    form.distribution_date.render_kw['min'] = session_interface.load_from_session('deathdate').isoformat()
    if form.validate_on_submit():
        session_interface.update_session({field: data for field, data in form.data.items() if data})
    estate = processing.calculate_distribution(**session_interface.load_session())
    return render_template('distribution.html',
        title='Distribution',
        estate=estate,
        form=form)
    # TODO: Enable saving a set of beneficiaries to be recalculated with a different net value

@app.post('/update_server')
def webhook():
    if request.method != 'POST':
        return 'Wrong event type', 400
    if (signature_header := request.headers.get('x-hub-signature-256', None)) is None:
        return 'x-hub-signature-256 header is missing!', 401
    if not utils.verify_signature(app.config['SECRET_KEY'], signature_header, request.data):
        return 'Request signatures did not match!', 403
    # TODO: Expand checks: see https://medium.com/@aadibajpai/deploying-to-pythonanywhere-via-github-6f967956e664
    repo = git.Repo('/home/themezj/intestacy/.git')
    repo.remotes.origin.pull()
    return 'Updated PythonAnywhere successfully'
