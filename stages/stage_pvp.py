from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import get_commands, logout, exit_pvp
from utils.common import query_interval

from time import sleep
import json
from threading import Thread


class StagePVP(StageBase):
    """
    匹配页面。
    """
    def __init__(self, did, code, status: list = None):
        super().__init__(status)
        self.did = did
        self.code = code
        self.matching = True

    def enter(self):
        color_print('正在寻找合适的对手...使用exit退出匹配', EColor.EMPHASIS)
        self.enter_status('匹配中')
        self.cmd_set['r'] = (self.refresh, '刷新。')
        self.cmd_set['exit'] = (self.exit, '退出匹配并返回卡组编辑页面。')

        t = Thread(target=self.__wait)
        t.start()

        super().enter()

    def refresh(self):
        pass
        # from stages.stage_game import StageGame
        # cs = get_commands()
        # if cs is not None:
        #     for c in cs:
        #         if c['op'] == 'pvp_ok':
        #             self.exit_status('匹配中')
        #             if self.matching:
        #                 self.next_stage = StageGame(self.status, cs)
        #                 self.interrupt_input('对局已找到，请使用r刷新并进入对局！', EColor.EMPHASIS)
        #                 self.matching = False

    def __wait(self):
        from stages.stage_game import StageGame
        f = True
        cs = list()
        while f and self.matching:
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    if c['op'] == 'pvp_ok':
                        f = False
            sleep(query_interval)
        self.exit_status('匹配中')
        if self.matching:
            self.next_stage = StageGame(self.status, cs)
            self.interrupt_input('对局已找到，请使用r刷新并进入对局！', EColor.EMPHASIS)

    def exit(self):
        from stages.stage_deck_edit import StageDeckEdit
        self.matching = False
        exit_pvp(self.did, self.code)
        self.next_stage = StageDeckEdit(self.status)