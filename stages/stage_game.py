from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import get_commands, chat
from utils.common import query_interval

from threading import Thread
from time import sleep


class StageGame(StageBase):
    """
    游戏页面。
    """
    def __init__(self, st):
        super().__init__(st)
        self.running = True

    def enter(self):
        t = Thread(target=self.__listen)
        t.start()
        color_print('进入对局！输入非指令可以自由发言！', EColor.EMPHASIS)
        super().enter()

    def default_cmd(self, cmd):
        chat(cmd)

    def __listen(self):
        while self.running:
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    self.carry_out(c)
            sleep(query_interval)

    def carry_out(self, cmd):
        from stages.stage_deck_edit import StageDeckEdit
        if cmd['op'] == 'endm_force':
            self.running = False
            self.interrupt_input('服务器故障，对局被非正常关闭。输入任意内容回到卡组编辑页面。',
                                 EColor.ERROR)
            self.next_stage = StageDeckEdit(self.status)
        elif cmd['op'] == 'chat':
            self.interrupt_input(cmd['args'] ,EColor.OP_PLAYER)
