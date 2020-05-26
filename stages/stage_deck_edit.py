from stages.stage_base import StageBase


class StageDeckEdit(StageBase):
    def enter(self):
        # self.cmd_set['edit'] = (self.call_deck_editor, '跳转至卡组编辑页面。')
        super().enter()