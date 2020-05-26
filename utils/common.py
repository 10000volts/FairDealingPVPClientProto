import requests
import json
import traceback
from time import sleep
import os

server = 'http://47.113.95.132:8082/'
DEBUG = int(os.getenv('DEBUG', 1))


def __send_message(path, data=None, method='GET', request_retry_times=0,
                   request_time_out=120, request_break_time=0, check_status_code=True):
    url = "{}/{}".format(server, path)

    request_dict = dict()

    # 填装请求报文
    if method == 'POST':
        request_dict['data'] = data
    elif method == 'GET':
        # 都是params
        if data:
            request_dict['params'] = data
    elif method == 'PUT':
        if data:
            request_dict['data'] = data
    elif method == 'PATCH' or method == 'DELETE':
        # 都是 params
        if data:
            request_dict['data'] = data
    request_dict['timeout'] = request_time_out
    # 进入发送请求的逻辑
    try_times = 0
    while try_times <= request_retry_times:
        try:
            res = requests.request(method, url, **request_dict)
            if check_status_code and res.status_code >= 400:
                if DEBUG:
                    print("%d failed %s" % (res.status_code, res.text))
                return None
            # 返回
            return res
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            try_times += 1
            if DEBUG:
                print("sleep %d seconds and try %s again" % (request_break_time, url))
            sleep(request_break_time)
            continue
    raise Exception("%s %s request failed" % (url, method))


def login(user_name, pwd):
    """

    :param user_name:
    :param pwd: 密码明文。HTTPS协议下可确保链路安全。
    :return:
    """
    if __send_message(path='player/login/',
                      data={'user_name': user_name, 'pwd': pwd},
                      method='POST'):
        return True
    return False


def logout():
    __send_message(path='player/logout/')
