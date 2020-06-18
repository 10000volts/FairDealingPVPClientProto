from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import get_commands, chat, query_interval, answer
from utils.constants import game_phase, time_point, card_rank
from custom.msg_ignore import ignore_list

from threading import Thread
from time import sleep


def _get_p(p):
    return color('对方', EColor.OP_PLAYER) if p == 0 else \
        color('您', EColor.PLAYER_NAME)


def _card_detail(c: dict):
    """
    呈现卡(约等于反序列化)。
    :param c:
    :return:
    """
    be = ''
    tk = ''
    a = c['bsc_atk'] + c['buff_atk'] + c['halo_atk']
    d = c['src_def'] + c['buff_def'] + c['halo_def']
    if len(c['buff_eff']):
        be = '({})'.format(color(['buff_eff'][-1]), EColor.EMPHASIS)
    if int(c['is_token']):
        tk = color('(衍生)', EColor.EMPHASIS)

    if a > c['src_atk']:
        a = color(str(a), EColor.GREATER_THAN)
    elif a == c['src_atk']:
        a = color(str(a), EColor.EQUAL_TO)
    else:
        a = color(str(a), EColor.LESS_THAN)

    if d > c['src_def']:
        d = color(str(d), EColor.GREATER_THAN)
    elif d == c['src_def']:
        d = color(str(d), EColor.EQUAL_TO)
    else:
        d = color(str(d), EColor.LESS_THAN)

    return color('{name}{buff_eff}\n'
                 'gcid: {gcid}{tk}\n'
                 'ATK/{atk} DEF/{def_}\n'
                 '{loc}'.format(name=c['name'], buff_eff=be, gcid=c['gcid'],
                          tk=tk, atk=a, def_=d, loc=c['location']), EColor.DEFAULT_COLOR)


class StageGame(StageBase):
    """
    游戏页面。
    """
    def __init__(self, st):
        super().__init__(st)
        self.running = True

    def enter(self):
        self.cmd_set['ans'] = (self.answer, '响应服务器的请求。')
        t = Thread(target=self.__listen)
        t.start()
        super().enter()

    def default_cmd(self, cmd):
        chat(cmd)

    def answer(self, ans):
        answer(ans)

    def __listen(self):
        while self.running:
            cs = get_commands()
            if cs is not None:
                for c in cs:
                    self.carry_out(c)
            sleep(query_interval)

    def carry_out(self, cmd):
        from stages.stage_deck_edit import StageDeckEdit
        msg = ''
        col = EColor.DEFAULT_COLOR
        if cmd['op'] == 'endm_force':
            self.running = False
            msg = '服务器故障，对局被非正常关闭。输入任意内容回到卡组编辑页面。'
            col = EColor.ERROR
            self.next_stage = StageDeckEdit(self.status)
        elif cmd['op'] == 'endm':
            self.running = False
            res = '取得了胜利！' if int(cmd['args'][0]) else '遗憾地败北orz'
            msg = '您在与{}的交锋中{}\n'\
                  '输入任意内容回到卡组编辑页面。'.format(cmd['args'][1], res)
            col = EColor.EMPHASIS
            self.next_stage = StageDeckEdit(self.status)
        elif cmd['op'] == 'startm':
            msg = '进入对局！输入非指令可以自由发言！'
            col = EColor.EMPHASIS
        elif cmd['op'] == 'startg':
            msg = '游戏开始！'
            col = EColor.EMPHASIS
        elif cmd['op'] == 'eng':
            msg = '单局游戏结束orz'
            col = EColor.EMPHASIS
        elif cmd['op'] == 'ent_ph':
            msg = '进入阶段: {}'.format(game_phase[cmd['args'][0]])
        elif cmd['op'] == 'sp_decided':
            msg = '{}获得了先手！'.format(_get_p(cmd['sd']))
        elif cmd['op'] == 'req_shw_crd':
            msg = '请展示1张手牌中的{}卡。'.format(card_rank[cmd['args'][0]])
        elif cmd['op'] == 'req_chs_tgt_f' or cmd['op'] == 'req_chs_tgt':
            msg = '请选择{}个目标，输入ans 在卡名前方显示的序号: \n'.format(cmd['args'][1])
            i = 0
            for c in cmd['args'][0]:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) +\
                       _card_detail(c) + '\n'
                i += 1
        elif cmd['op'] == 'anu_tgt':
            msg = '{}选择了{}。'.format(_get_p(cmd['sd']), cmd['args'][0]['name'])
        elif cmd['op'] == 'ent_tp':
            msg = '进入时点: {}'.format(time_point[cmd['args'][0]])
        elif cmd['op'] == 'chat':
            msg = cmd['args']
            col = EColor.OP_PLAYER

        if cmd['op'] not in ignore_list:
            self.interrupt_input(msg, col)
