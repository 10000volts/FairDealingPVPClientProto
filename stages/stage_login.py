from utils.color import color, color_print
from custom.e_color import EColor
import getpass
from hashlib import md5, sha256

from utils.common import login
from stages.stage_deck_edit import StageDeckEdit


class StageLogin:
    @staticmethod
    def enter():
        color_print('欢迎使用公平交易PVP原型版！操作小提示：'
                    '1、输入-h指令以获得帮助。')  # '2、在输入卡名时，用\"-\"替换掉卡名中的空格。')
        while True:
            user_name = input("请输入用户名：")
            pwd = getpass.getpass('输入密码：(完成后回车)')
            if login(user_name, pwd):
                color_print('{}，欢迎您的到来!'.format(color(user_name, EColor.PLAYER_NAME)))
                break
            else:
                color_print('用户名或密码错误orz', EColor.ERROR)
        stm = StageDeckEdit()
        stm.enter()
