from functools import wraps
from flask import request, redirect, url_for, render_template, flash, abort, \
        jsonify, session, g
from flaskr import app, db
from flaskr.models import Entry, User , Result
import datetime

def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_view

@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(session['user_id'])


@app.route('/')
def show_entries():
    entries = Entry.query.order_by(Entry.id.desc()).all()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    entry = Entry(
            title=request.form['title'],
            text=request.form['text']
            )
    db.session.add(entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/users/')
@login_required
def user_list():
    users = User.query.all()
    return render_template('user/list.html', users=users)

@app.route('/users/<int:user_id>/')
@login_required
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)

@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name=request.form['name']
        user.email=request.form['email']
        user.uuid=request.form['uuid']
        user.sex=request.form['sex']
        user.age=request.form['age']
        user.level=request.form['level']
        if request.form['password']:
            user.password=request.form['password']
        #db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user_id))
    return render_template('user/edit.html', user=user)

@app.route('/users/create/', methods=['GET', 'POST'])
@login_required
def user_create():
    if request.method == 'POST':
        user = User(name=request.form['name'],
                    email=request.form['email'],
                    uuid=request.form['uuid'],
                    sex=request.form['sex'],
                    age=request.form['age'],
                    level=request.form['level'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_list'))
    return render_template('user/edit.html')

@app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
def user_delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'OK'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query,
                request.form['email'], request.form['password'])
        if authenticated:
            session['user_id'] = user.id
            flash('You were logged in')
            return redirect(url_for('show_entries'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/reception')
def reception():
    return render_template('reception.html')

@app.route('/select')
def select():
    return render_template('select.html')

@app.route('/result_default')
def result_default():
    date = datetime.date.today().strftime('%Y-%m-%d')
    result = Result.query.order_by(Result.id.desc()).all()
    return render_template('result.html', result=result, date=date)

@app.route('/result/<string:date>/')
def result(date):
    users = User.query.all()
    results = []
    for user in users:
        results.append(db.engine.execute('select uuid, machine_type, count(*) as count, counted_at from result group by machine_type having DATE_FORMAT(counted_at, "%%Y-%%m-%%d") = "' + date + '" and uuid = "' + user.uuid + '"'))
    return render_template('result.html', results=results, date=date)

@app.route('/result/add', methods=['POST'])
def result_add():
    result = Result(
            uuid=request.form['uuid'],
            machine_type=request.form['machine_type'],
            counted_at=request.form['counted_at']
            )
    db.session.add(result)
    db.session.commit()
    return redirect(url_for('result'))
