import re

import requests

headers = {'User-Agent': None}


def login(email, passwd):
    """
    登录
    :param email:
    :param passwd:
    :return:
    """
    url = 'https://v2.freeyes.xyz/auth/login'
    data = {'email': email, 'passwd': passwd}
    try:
        r = requests.post(url, data=data, headers=headers, timeout=5)
        if r.json()['ret'] == 0:
            return
    except:
        return
    cookies = r.cookies.get_dict()
    return cookies


def buy(cookies):
    """
    购买vip套餐
    :param cookies:
    :return:
    """
    url = 'https://freeyes.xyz/user/buy'
    params = {'shop': 9, 'autorenew': 1, 'disableothers': 1}
    try:
        r = requests.post(url, headers=headers, cookies=cookies, params=params, timeout=5)
        return r.json()['ret'] == 1, r.json()['msg']
    except:
        return False, '购买失败'


def get_balance(cookies):
    """
    获取余额
    :param cookies:
    :return:
    """
    url = 'https://freeyes.xyz/user'
    r = requests.get(url, headers=headers, cookies=cookies)
    return float(re.findall('\s*(.*?) \$', r.text)[0])


def get_sub(cookies):
    """
    获取订阅
    :param cookies:
    :return:
    """
    url = 'https://freeyes.xyz/user'
    r = requests.get(url, headers=headers, cookies=cookies)
    return re.findall('<code>(https://.*?)</code>', r.text)[0]


def get_invite_num(cookies):
    """
    获取剩余邀请次数数量
    :param cookies:
    :return:
    """
    url = 'https://freeyes.xyz/user/invite'
    r = requests.get(url, headers=headers, cookies=cookies)
    return int(re.findall('<code>(.*?)</code>', r.text)[-3])


def buy_invite(cookies, num=1):
    """
    购买邀请次数
    :param cookies:
    :param num:
    :return:
    """
    url = 'https://freeyes.xyz/user/buy_invite'
    data = {'num': num}
    try:
        r = requests.post(url, headers=headers, cookies=cookies, data=data)
        return r.json()['invite_num']
    except:
        return False


def get_invite_code(cookies):
    """
    获取邀请码
    :param cookies:
    :return:
    """
    url = 'https://freeyes.xyz/user/invite'
    r = requests.get(url, headers=headers, cookies=cookies)
    return re.findall('value="(.*?)"', r.text)[0]
