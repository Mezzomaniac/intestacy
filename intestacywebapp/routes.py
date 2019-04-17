import webbrowser
from flask import render_template, flash, redirect, url_for, request, session

from . import app
from .forms import *#LoginForm, Questions1Form, TestForm, Questions2Form, questions2a_form_builder, Questions3Form, questions3a_form_builder
from .functions import update_session, load_from_session, set_specified_items, reset_session, calculate, money_fmt

ACT_URL = "https://www.legislation.wa.gov.au/legislation/statutes.nsf/RedirectURL?OpenAgent&query=mrdoc_37039.htm#_Toc493060114"

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', version=app.config['VERSION'])

@app.route('/act')
def act():
    return webbrowser.open(ACT_URL)
    return redirect(ACT_URL)  # TODO: open in new window

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for {}, remember me = {}'.format(form.username.data, form.remember.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/test', methods=['GET', 'POST'])
def test():
    beneficiaries = {'Sample data': '$10.00'}
    deathdate = '12 January 1985'
    value = '$10.00'
    return render_template('distribution.html', title='Disttibution', beneficiaries=beneficiaries, value=value, deathdate=deathdate)
    if form.validate_on_submit():
        #print(form.data)
        update_session(form.data)
        #print(session)
        return redirect(url_for('test2'))
    return render_template('test.html', title='test', form=form)

@app.route('/test2', methods=['GET', 'POST'])
def test2():
    form = TestForm()
    #print(request.form)
    #session['c'][2] = 2
    #print(session)
    #arg2=request.args
    #print(arg)
    if form.validate_on_submit():
        print(session)
        print(request.form)
        print(form.data)
        #session['test'].update(form)
        return redirect(url_for('index'))
        #return redirect(url_for('test2'))
    return render_template('test.html', title='test2', form=form)

@app.route('/test3')
def test3(arg='a'):
    session['c'][3] = 3
    print(session['c'])
    arg2=request.args
    #print(arg)
    flash(session['c'])
    return render_template('index.html')

@app.route('/questions', methods=['GET', 'POST'])
@app.route('/questions/1', methods=['GET', 'POST'])
def questions():
    reset_session()
    form = Questions1Form()
    if form.validate_on_submit():
        update_session(form.data)
        set_specified_items()
        return redirect(url_for('questions2'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions2', methods=['GET', 'POST'])
def questions2():
    spouse = load_from_session('spouse')
    form = Questions2Form(spouse)
    if form.validate_on_submit():
        update_session(form.data)
        defactos = load_from_session('defactos')
        partner = spouse or defactos
        update_session({'partner': partner})
        if spouse + defactos > 1:
            return redirect(url_for('questions2a'))
        elif not partner or load_from_session('value') > load_from_session('item 2'):
            return redirect(url_for('questions3'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions2a', methods=['GET', 'POST'])
def questions2a():
    defactos = load_from_session('defactos')
    form = questions2a_form_builder(defactos)
    if form.validate_on_submit():
        update_session(form.data)
        if not load_from_session('partner') or load_from_session('value') > load_from_session('item 2'):
            return redirect(url_for('questions3'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions3', methods=['GET', 'POST'])
def questions3():
    form = Questions3Form()
    if form.validate_on_submit():
        update_session(form.data)
        issue = form.surviving_issue.data + form.nonsurviving_issue.data
        update_session({'issue': issue})
        partner = load_from_session('partner')
        value = load_from_session('value')
        item3aandb = load_from_session('item 3(a) and (b)')
        if form.nonsurviving_issue.data:
            return redirect(url_for('questions3a'))
        elif (partner and not issue and value > item3aandb) or not (partner or issue):
            return redirect(url_for('questions4'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions3a', methods=['GET', 'POST'])
def questions3a():
    nonsurviving_issue = load_from_session('nonsurviving_issue')
    form = family_form_builder('grandchildren', 'child', nonsurviving_issue)
    if form.validate_on_submit():
        update_session(form.data)
        partner = load_from_session('partner')
        issue = load_from_session('issue')
        value = load_from_session('value')
        item3aandb = load_from_session('item 3(a) and (b)')
        if (partner and not issue and value > item3aandb) or not (partner or issue):
            return redirect(url_for('questions4'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions4', methods=['GET', 'POST'])
def questions4():
    form = Questions4Form()
    if form.validate_on_submit():
        update_session(form.data)
        parent = form.father.data or form.mother.data
        update_session({'parent': parent})
        partner = load_from_session('partner')
        value = load_from_session('value')
        item3aandb = load_from_session('item 3(a) and (b)')
        item3bi = load_from_session('item 3(b)(i)')
        if not parent or (partner and value > item3aandb + 2 * item3bi):
            return redirect(url_for('questions5'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions5', methods=['GET', 'POST'])
def questions5():
    form = Questions5Form()
    if form.validate_on_submit():
        update_session(form.data)
        siblings = form.surviving_siblings.data + form.nonsurviving_siblings.data
        update_session({'siblings': siblings})
        if form.nonsurviving_siblings.data:
            return redirect(url_for('questions5a'))
        elif not (load_from_session('partner') or load_from_session('parent') or siblings):
            return redirect(url_for('questions6'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions5a', methods=['GET', 'POST'])
def questions5a():
    nonsurviving_siblings = load_from_session('nonsurviving_siblings')
    form = family_form_builder('nibling', 'sibling', nonsurviving_siblings)
    if form.validate_on_submit():
        update_session(form.data)
        if not (load_from_session('partner') or load_from_session('parent') or load_from_session('siblings')):
            return redirect(url_for('questions6'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions6', methods=['GET', 'POST'])
def questions6():
    form = Questions6Form()
    if form.validate_on_submit():
        update_session(form.data)
        if not form.grandparents.data:
            return redirect(url_for('questions7'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions7', methods=['GET', 'POST'])
def questions7():
    form = Questions7Form()
    if form.validate_on_submit():
        update_session(form.data)
        auntuncles = form.surviving_auntuncles.data + form.nonsurviving_auntuncles.data
        update_session({'auntuncles': auntuncles})
        if form.nonsurviving_auntuncles.data:
            return redirect(url_for('questions7a'))
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/questions7a', methods=['GET', 'POST'])
def questions7a():
    nonsurviving_auntuncles = load_from_session('nonsurviving_auntuncles')
    form = family_form_builder('cousin', 'aunt or uncle', nonsurviving_auntuncles)
    if form.validate_on_submit():
        update_session(form.data)
        return redirect(url_for('distribution'))
    return render_template('questions.html', title='Questions', form=form)

@app.route('/distribution')
def distribution():
    #return redirect(url_for('test'))
    beneficiaries = {beneficiary: money_fmt(share) for beneficiary, share in calculate().items()}
    deathdate = load_from_session('deathdate').strftime('%d %B %Y')
    value = money_fmt(load_from_session('value'))
    return render_template('distribution.html', title='Distribution', beneficiaries=beneficiaries, value=value, deathdate=deathdate)
