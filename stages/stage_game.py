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
    def enter(self):
        t = Thread(target=self.__listen)
        t.start()
        color_print('进入对局！', EColor.EMPHASIS)
        super().enter()

    def default_cmd(self, cmd):
        chat(cmd)

    def __listen(self):
        while True:
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    self.carry_out(c)
            sleep(query_interval)

    def carry_out(self, cmd):
        from stages.stage_deck_edit import StageDeckEdit
        if cmd['op'] == 'chat':
            self.interrupt_input(cmd['args'] ,EColor.OP_PLAYER)
