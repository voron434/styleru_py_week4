from flask import render_template, flash, redirect, request, session
from app import app
from vk_helpers import error_healing,form_url,get_user_info,get_online_friends_ids
import requests
import json
import os

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    params = {'logged_in': False,
              'auth_url': form_url(CLIENT_ID, request.url_root + 'getpas'),
              'logout_url': '/logout'
              }
    short_name = request.args.get('text', '')
    if 'access_token' not in session:
        return render_template('index.html', **params)

    params['logged_in'] = True
    token = session['access_token']
    online_friends_ids = get_online_friends_ids(short_name, token)
    if 'error' in online_friends_ids:
        params['error'] = error_healing(online_friends_ids['error']['error_code'])
        return render_template('index.html', **params)
    online_friends_ids = online_friends_ids['response']

    friends_info_pc = []
    for friend_id in online_friends_ids['online']:
        friend_info = get_user_info(token, friend_id)
        if 'error' in friend_info:
            error_healing(friend_info['error']['error_code'])
            friend_info = get_user_info(token, friend_id)
        friends_info_pc.append(friend_info)
    friends_info_mobile = []
    for friend_id in online_friends_ids['online_mobile']:
        friend_info = get_user_info(token, friend_id)
        if 'error' in friend_info:
            error_healing(friend_info['error']['error_code'])
            friend_info = get_user_info(token, friend_id)
        friends_info_mobile.append(friend_info)
    params['online_friends_mobile'] = friends_info_mobile
    params['online_friends_pc'] = friends_info_pc
    params.pop('online_friends', None)
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
    session.pop('access_token',None)
    return redirect('index')
