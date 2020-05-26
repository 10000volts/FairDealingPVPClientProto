from stages.stage_base import StageBase
from stages.stage_deck_edit import StageDeckEdit


class StageMain(StageBase):
    def enter(self):
        self.cmd_set['edit'] = (self.call_deck_editor, '跳转至卡组编辑页面。')
        super().enter()

    def call_deck_editor(self):
        self.next_stage = StageDeckEdit()
