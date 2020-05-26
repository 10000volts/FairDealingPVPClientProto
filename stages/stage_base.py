from custom.e_color import EColor
from utils.color import color, color_print
from utils.common import logout
import sys


class StageBase:
    def __init__(self):
        self.cmd_set = dict()
        self.cmd_set['-h'] = (self.print_help, '获取帮助。')
        self.cmd_set['exit'] = (self.logout_and_exit, '退出并注销登录。')
        self.next_stage: StageBase = None

    def enter(self):
        while self.next_stage is None:
            cmd = input("请输入指令。(键入-h获得帮助) ")
            el = cmd.split(' ')
            ins = el[0]
            if len(el) > 1:
                arg = el[1:]
                if ins in self.cmd_set:
                    try:
                        self.cmd_set[ins][0](*arg)
                    except Exception as ex:
                        color_print('错误的指令格式', EColor.ERROR)
            elif ins in self.cmd_set:
                try:
                    self.cmd_set[ins][0]()
                except Exception as ex:
                    color_print('错误的指令格式', EColor.ERROR)
        self.next_stage.enter()

    def print_help(self):
        for cmd in self.cmd_set.keys():
            color_print('{}: {}'.format(color(cmd, EColor.EMPHASIS), self.cmd_set[cmd][1]))

    def logout_and_exit(self):
        logout()
        sys.exit()
