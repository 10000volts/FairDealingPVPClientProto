from stages.stage_base import StageBase
from stages.stage_deck_edit import StageDeckEdit
from utils.color import color, color_print, EColor
from utils.common import get_commands, chat

from multiprocessing import Process


class StageGame(StageBase):
    """
    游戏页面。
    """
    def enter(self):
        p = Process(target=self.__listen, args=())
        p.start()
        super().enter()

    def default_cmd(self, cmd):
        chat(cmd)

    def __listen(self):
        while True:
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    self.carry_out(c)

    def carry_out(self, cmd):
        if cmd['op'] == 'chat':
            color_print(cmd['args'] ,EColor.OP_PLAYER)
