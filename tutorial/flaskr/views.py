# coding:utf-8

from functools import wraps
from flask import request, redirect, url_for, render_template, flash, abort, \
        jsonify, session, g
from flaskr import app, db
from flaskr.models import User, Machine, AccessLog, MachineLog, Result
import datetime

# Private ===
# ログイン必須にする
def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_view

# ユーザ情報を読み込む
@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(session['user_id'])

# === /Private

# === Routes

# TOP
@app.route('/')
def home():
    return render_template('home.html')

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query,
                request.form['email'], request.form['password'])
        if authenticated:
            session['user_id'] = user.id
            flash(u'ログインしました')
            return redirect(url_for('home'))
        else:
            flash(u'メールアドレスまたはパスワードが正しくありません')
    return render_template('login.html')

# ログアウト
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash(u'ログアウトしました')
    return redirect(url_for('login'))

# ユーザ一覧
@app.route('/users/')
@login_required
def user_list():
    users = User.query.all()
    return render_template('user/list.html', users=users)

# ユーザ詳細
@app.route('/users/<int:user_id>/')
@login_required
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)

# ユーザ編集
@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = User.query.get(user_id)

    # ユーザが見つからなければ404
    if user is None:
        abort(404)

    # POSTリクエストであれば、ユーザを保存
    if request.method == 'POST':
        user.name  = request.form['name']
        user.email = request.form['email']
        user.uuid  = request.form['uuid']
        user.sex   = request.form['sex']
        user.age   = request.form['age']
        user.level = request.form['level']

        if request.form['password']:
            user.password=request.form['password']

        db.session.add(user)
        db.session.commit()
        flash(u'保存しました')
        return render_template('user/detail.html', user=user)

    return render_template('user/edit.html', user=user)

# ユーザ新規作成
@app.route('/users/create/', methods=['GET', 'POST'])
@login_required
def user_create():
    if request.method == 'POST':
        user = User(name     = request.form['name'],
                    email    = request.form['email'],
                    uuid     = request.form['uuid'],
                    sex      = request.form['sex'],
                    age      = request.form['age'],
                    level    = request.form['level'],
                    password = request.form['password'])

        db.session.add(user)
        db.session.commit()
        flash(u'保存しました')
        return render_template('user/detail.html', user=user)

    return render_template('user/edit.html')

# ユーザ削除 (API @DELETE)
@app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
@login_required
def user_delete(user_id):
    user = User.query.get(user_id)

    # ユーザが見つからなければ404
    if user is None:
        abort(404)

    db.session.delete(user)
    db.session.commit()
    flash(u'ユーザを削除しました')
    return jsonify({'status': 'OK'})

# リハビリマシン一覧
@app.route('/machines/')
@login_required
def machine_list():
    machines = Machine.query.all()
    return render_template('machine/list.html', machines=machines)

# リハビリマシン新規作成
@app.route('/machines/create/', methods=['GET', 'POST'])
@login_required
def machine_create():
    if request.method == 'POST':
        machine = Machine(name    = request.form['name'],
                          display = request.form['display'])

        db.session.add(machine)
        db.session.commit()
        flash(u'保存しました')
        return redirect(url_for('machine_list'))

    return render_template('machine/edit.html')

# リハビリマシン編集
@app.route('/machines/<int:machine_id>/edit/', methods=['GET', 'POST'])
@login_required
def machine_edit(machine_id):
    machine = Machine.query.get(machine_id)

    # リハビリマシンが見つからなければ404
    if machine is None:
        abort(404)

    # POSTリクエストであれば、リハビリマシンを保存
    if request.method == 'POST':
        machine.name  = request.form['name']
        machine.display  = request.form['display']

        db.session.add(machine)
        db.session.commit()
        flash(u'保存しました')
        return redirect(url_for('machine_list'))

    return render_template('machine/edit.html', machine=machine)

# リハビリマシン削除 (API @DELETE)
@app.route('/machines/<int:machine_id>/delete/', methods=['DELETE'])
@login_required
def machine_delete(machine_id):
    machine = Machine.query.get(machine_id)

    # リハビリマシンが見つからなければ404
    if machine is None:
        abort(404)

    db.session.delete(machine)
    db.session.commit()
    flash(u'リハビリマシンを削除しました')
    return jsonify({'status': 'OK'})

# 受付中ユーザ一覧
@app.route('/reception')
def reception():
    return render_template('reception.html')

@app.route('/result_default')
@login_required
def result_default():
    date = datetime.date.today().strftime('%Y-%m-%d')
    result = Result.query.order_by(Result.id.desc()).all()
    return render_template('result.html', result=result, date=date)

@app.route('/result/<string:date>/')
@login_required
def result(date):
    users = User.query.all()
    results = []
    for user in users:
        results.append(db.engine.execute('select uuid, machine_type, count(*) as count, counted_at from result group by machine_type having DATE_FORMAT(counted_at, "%%Y-%%m-%%d") = "' + date + '" and uuid = "' + user.uuid + '"'))
    return render_template('result.html', results=results, date=date)

@app.route('/result/add', methods=['POST'])
@login_required
def result_add():
    result = Result(
            uuid=request.form['uuid'],
            counted_at=request.form['counted_at']
            )
    db.session.add(result)
    db.session.commit()
    return redirect(url_for('result_add'))

# === /Routes

# === API Routes

@app.route('/api/result/add', methods=['POST'])
def api_result_add():
    try:
        result = Result(
                machine_id=request.form['machine_id'],
                counted_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        db.session.add(result)
        db.session.commit()
        return jsonify({'status': 'OK', 'result': {'id': result.id, 'machine_id': result.machine_id, 'counted_at' : result.counted_at}})
    except:
        return jsonify({'status': 'Bad Request', 'message': 'Your request is invalid.'})

# get entered user
@app.route('/api/reception/recent', methods=['GET'])
def api_reception_recent():
    # 最新の入室記録を確認
    recent_log = AccessLog.query.filter(AccessLog.exited_at == None).order_by(AccessLog.uuid).first()

    if recent_log is not None and datetime.datetime.now() - recent_log.entered_at < datetime.timedelta(seconds=10):
        user = User.query.filter(User.uuid == recent_log.uuid).first()
        return jsonify({'status': 'OK', 'result': {'id': user.id, 'name': user.name}})
    else:
        return jsonify({'status': 'OK', 'result': None})


# enter or exit
@app.route('/api/reception', methods=['POST'])
def api_reception():
    try:
        # 最新の入室記録を確認
        recent_log = AccessLog.query.filter(AccessLog.uuid == request.form['uuid'], AccessLog.exited_at == None).order_by(AccessLog.uuid).first()

        # 最新の入室記録がなければ入室
        if recent_log is None:
            recent_log = AccessLog(
                uuid       = request.form['uuid'],
                entered_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            message = 'Entered.'

        # 最新の入室記録が30秒以下だと以下だと受け付けない
        elif datetime.datetime.now() - recent_log.entered_at < datetime.timedelta(seconds=30):
            return jsonify({'message': 'Cannot exit too soon.'})

        # 入室記録があれば退出
        else:
            recent_log.exited_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = 'Exited.'

        db.session.add(recent_log)
        db.session.commit()
        result = AccessLog(
                uuid       = request.form['uuid'],
                )
        return jsonify({'message': message})
    except:
        return jsonify({'status': 'Bad Request', 'message': 'Your request is invalid.'})

@app.route('/api/standby', methods=['POST'])
def api_standby():
    try:
        # ユーザのマシン接近記録を取得
        log = MachineLog.query.filter(MachineLog.uuid == request.form['uuid'], MachineLog.machine_id == request.form['machine_id']).first()

        # 最新の接近記録がなければ作成
        if log is None or log.uuid != request.form['uuid']:
            log = MachineLog(
                uuid       = request.form['uuid'],
                machine_id = request.form['machine_id'],
                entered_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )

        # 接近記録があれば延長
        else:
            log.entered_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db.session.add(log)
        db.session.commit()
        return jsonify({'message': 'Standby.'})
    except:
        return jsonify({'status': 'Bad Request', 'message': 'Your request is invalid.'})

# === /API Routes
