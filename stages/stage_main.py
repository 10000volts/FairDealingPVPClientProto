from stages.stage_base import StageBase
from utils.color import color, color_print, EColor


class StageMain(StageBase):
    def enter(self):
        color_print('\n----主页面----')
        self.cmd_set['edit'] = (self.call_deck_editor, '跳转至卡组编辑页面。')
        super().enter()

    def call_deck_editor(self):
        from stages.stage_deck_edit import StageDeckEdit
        self.next_stage = StageDeckEdit(self.status)
