import requests
import time
import json


def error_healing(error_code):
    if error_code == 1:
        return 'Произошла неизвестная ошибка'
    elif error_code == 2:
        return 'Сорян, админ все повыключал'
    elif error_code == 5:
        return 'Авторизация не удалась'
    elif error_code == 6:
        time.sleep(2)
        return None
    elif error_code == 9:
        return 'Слишком много однотипных действий'
    elif error_code == 14:
        return 'Прости, вылезла капча. Попробуй перезайти'
    elif error_code == 15:
        return 'Этот юзер спрятался от меня'
    elif error_code == 17:
        return 'Так исторически сложилось, что тебе придется войти'
    elif error_code == 18:
        return 'Эта страничка удалена, у нее нет друзей'
    elif error_code == 113:
        return 'Прости, но ты ввел что-то не так, как я ожидаю'
    elif error_code == 1000:
        return 'Нет, сначала положи что-нибудь в форму!'
    else:
        return 'Тебе повезло! Ты нашел новую ошибку!'



def form_url(CLIENT_ID, redirect_uri):
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