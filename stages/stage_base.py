from custom.e_color import EColor
from utils.color import color, color_print
from utils.common import logout
import sys


class StageBase:
    def __init__(self):
        self.cmd_set = dict()
        self.cmd_set['-h'] = (self.print_help, '获取帮助。')
        self.cmd_set['exit'] = (self.logout_and_exit, '退出并注销登录。')

    def enter(self):
        while True:
            cmd = input("请输入指令。(键入-h获得帮助)")
            if cmd in self.cmd_set:
                self.cmd_set[cmd][0]()

    def print_help(self):
        for cmd in self.cmd_set.keys():
            color_print('{}: {}'.format(color(cmd, EColor.EMPHASIS), self.cmd_set[cmd][1]))

    def logout_and_exit(self):
        logout()
        sys.exit()
