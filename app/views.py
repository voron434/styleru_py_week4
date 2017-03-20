from flask import render_template, flash, redirect, request, session
from app import app
import requests
import json
import time

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


def error_healing(error_code):
    if error_code == 1:
        return 'Произошла неизвестная ошибка'
    if error_code == 2:
        return 'Сорян, админ все повыключал'
    if error_code == 5:
        return 'Авторизация не удалась'
    if error_code == 6:
        time.sleep(2)
        return None
    if error_code == 9:
        return 'Слишком много однотипных действий'
    if error_code == 14:
        return 'Прости, вылезла капча. Попробуй перезайти'
    if error_code == 15:
        return 'Этот юзер спрятался от меня'
    if error_code == 17:
        return 'Так исторически сложилось, что тебе придется войти'
    if error_code == 18:
        return 'Эта страничка удалена, у нее нет друзей'
    if error_code == 113:
        return 'Прости, но ты ввел что-то не так, как я ожидаю'
    if error_code == 1000:
        return 'Нет, сначала положи что-нибудь в форму!'


def form_url(redirect_uri):
    params = {'client_id': CLIENT_ID,
              'display': 'page',
              'redirect_uri': redirect_uri,
              'scope': 'friends',
              'response_type': 'code',
              'v': '5.62',
              }
    request = requests.Request('GET', 'https://oauth.vk.com/authorize',
                               params=params)
    request.prepare()
    return request.prepare().url


def get_user_info(token, short_name):
    params = {'user_ids': short_name,
              'access_token': token,
              }
    url = 'https://api.vk.com/method/users.get'
    request = json.loads(requests.get(url, params).text)
    return request


def get_online_friends_ids(short_name, token):
    if not short_name:
        return {'error': {'error_code': 1000}}

    user_info = get_user_info(token, short_name)
    if 'error' in user_info:
        return user_info
    url = 'https://api.vk.com/method/friends.getOnline'
    params = {'user_id': user_info['response'][0]['uid'],
              'access_token': token,
              'order': 'hints',
              'count': 5000,  # vk won't return more
              'v': '5.62',
              'online_mobile': 1,
              }
    vk_friends_online = json.loads(requests.get(url, params).text)
    return vk_friends_online


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    params = {'logged_in': False,
              'auth_url': form_url(request.url_root + 'getpas'),
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
