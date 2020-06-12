from stages.stage_base import StageBase
from stages.stage_game import StageGame
from utils.color import color, color_print, EColor
from utils.common import get_commands


class StagePVP(StageBase):
    """
    匹配页面。
    """
    def enter(self):
        c = None
        i = 1
        f = True
        while f:
            color_print('正在寻找合适的对手' + '.' * i, EColor.EMPHASIS, True)
            i = i + 1 if i < 6 else 1
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    if c['op'] == 'pvp_ok':
                        f = False
        self.next_stage = StageGame()
        super().enter()
