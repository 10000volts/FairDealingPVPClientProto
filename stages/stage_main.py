from stages.stage_base import StageBase


class StageMain(StageBase):
    def __init__(self):
        super().__init__()
        self.cmd_set['edit'] = (self.call_deck_editor, '跳转至卡组编辑页面。')

    def call_deck_editor(self):
        pass
