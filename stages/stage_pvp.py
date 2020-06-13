from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import get_commands, logout, exit_pvp
from utils.common import query_interval

from time import sleep
import sys
from threading import Thread


class StagePVP(StageBase):
    t: Thread = None

    """
    匹配页面。
    """
    def enter(self):
        color_print('正在寻找合适的对手...', EColor.EMPHASIS)
        self.enter_status('匹配中')
        self.cmd_set['r'] = (self.refresh, '刷新。')
        self.cmd_set['exit'] = (self.exit, '退出匹配并终止游戏。')

        t = Thread(target=self.__wait)
        t.start()

        super().enter()

    def refresh(self):
        pass

    def __wait(self):
        from stages.stage_game import StageGame
        f = True
        while f:
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    if c['op'] == 'pvp_ok':
                        f = False
            sleep(query_interval)
        self.exit_status('匹配中')
        self.next_stage = StageGame(self.status)
        self.interrupt_input('对局已找到，请使用r刷新并进入对局！', EColor.EMPHASIS)

    def exit(self):
        exit_pvp()
        logout()
        sys.exit()