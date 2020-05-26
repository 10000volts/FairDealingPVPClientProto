from utils.color import color, color_print
from custom.e_color import EColor
import getpass
from hashlib import md5, sha256

from utils.common import login
from stages.stage_main import StageMain


class StageLogin:
    @staticmethod
    def enter():
        while True:
            user_name = input("欢迎使用公平交易PVP原型版。请输入用户名：")
            pwd = getpass.getpass('输入密码：(完成后回车)')
            if login(user_name, pwd):
                color_print('{}，欢迎您的到来!'.format(color(user_name, EColor.PLAYER_NAME)))
                break
            else:
                color_print('用户名或密码错误orz', EColor.ERROR)
        stm = StageMain()
        stm.enter()
