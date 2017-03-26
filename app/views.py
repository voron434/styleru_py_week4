from flask import render_template, flash, redirect, request, session
from app import app
import requests
import os
from . import vk_helpers


CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
SECRET_KEY = os.environ['SECRET_KEY']

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            raise 404


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = SECRET_KEY
    return session['_csrf_token']


def is_error_there(response, **params):
    flag = False
    if 'error' in response:
        flag = True
        params['error'] = vk_helpers.show_error(response['error']['error_code'])
    return flag


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    params = {'logged_in': False,
              'auth_url': vk_helpers.form_url(CLIENT_ID, request.url_root + 'getpas'),
              'logout_url': '/logout',
              'csrf_token': generate_csrf_token()
              }
    short_name = request.args.get('text', '')
    if 'access_token' not in session:
        token = None
    else:
        params['logged_in'] = True
        token = session['access_token']

    online_friends_ids = vk_helpers.get_all_friends_ids(short_name, token)
    if is_error_there(online_friends_ids, **params):
        return render_template('index.html', **params)
    else:
        online_friends_ids = online_friends_ids['response']['items']
    online_friends = []
    for friend in online_friends_ids:
        if friend['online']:
            online_friends.append(friend)
    params['online_friends'] = online_friends
    return render_template('index.html', **params)


@app.route('/getpas', methods=['GET', 'POST'])
def getpas():

    code = request.args.get('code')
    if code is None:
        return redirect('/index')

    redirect_uri = request.url_root + 'getpas'
    vk_params = {'client_id': CLIENT_ID,
                 'client_secret': CLIENT_SECRET,
                 'redirect_uri': redirect_uri,
                 'code': code,
                 }
    response = requests.get('https://oauth.vk.com/access_token', params=vk_params)
    token = response.json().get('access_token', None)
    session['access_token'] = token
    return redirect('index')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('access_token', None)
    return redirect('index')
