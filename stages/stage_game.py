from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import get_commands, chat, query_interval, answer
from utils.constants import game_phase, time_point, card_rank, location, ECardRank\
    , effect_desc
from custom.msg_ignore import ignore_list

from threading import Thread
from time import sleep
import json


def adj_pos(x, y):
    """
    生成临近的合法坐标。
    :param x:
    :param y:
    :return:
    """
    p = y * 6 + x
    if p == 0:
        return p + 1, p + 6
    elif p < 6:
        return p - 1, p + 1, p + 6
    elif p < 30:
        return p - 6, p - 1, p + 1, p + 6
    elif p < 35:
        return p - 6, p - 1, p + 1
    else:
        return p - 6, p - 1


def _get_p(p):
    return color('对方', EColor.OP_PLAYER) if p == 0 else \
        color('您', EColor.PLAYER_NAME)


def _num_print(num, src_num):
    if num > src_num:
        return color(str(num), EColor.GREATER_THAN)
    elif num < src_num:
        return color(str(num), EColor.LESS_THAN)
    return color(str(num), EColor.EQUAL_TO)


def _card_intro_short(c: dict):
    """
    放置/取走阶段时采用的格式。
    :param c:
    :return:
    """
    if c['whole']:
        return '{name} {adv}、'.format(name=c['name'], adv=_num_print(c['add_val'], 0))
    else:
        return '？？？ {adv}、'.format(adv=_num_print(c['add_val'], 0))


def _card_intro_add_val(c: dict):
    """
    展示附加值时采用的格式。
    :param c:
    :return:
    """
    be = ''
    if len(c['buff_eff']):
        if len(c['buff_eff']) > 1:
            be = '(..., {})'.format(color(effect_desc[c['buff_eff'][-1]]), EColor.EMPHASIS)
        else:
            be = '({})'.format(color(effect_desc[c['buff_eff'][0]]), EColor.EMPHASIS)
    if c['whole']:
        return '[{vid}]{name}{buff_eff}({adv})'.format(
            name=c['name'], buff_eff=be, vid=c['vid'], adv=_num_print(c['add_val'], 0))
    else:
        return '[{vid}]？？？{buff_eff}({adv})'.format(
            buff_eff=be, vid=c['vid'], adv=_num_print(c['add_val'], 0))


def _card_detail(c: dict):
    """
    呈现卡(约等于反序列化)。
    :param c:
    :return:
    """
    be = ''
    if len(c['buff_eff']):
        be = '({})'.format(color(c['buff_eff'][-1]), EColor.EMPHASIS)
    if not c['whole']:
        return color('???{buff_eff}\n'
                     'vid: {vid}\n'
                     '影响力/附加值: {adv}\n'
                     '{loc}'.format(buff_eff=be, vid=c['vid'], adv=_num_print(c['add_val'], 0),
                                    loc=location[c['location']]), EColor.DEFAULT_COLOR)
    tk = ''
    if int(c['is_token']):
        tk = color('(衍生)', EColor.EMPHASIS)
    a = _num_print(c['atk'], c['src_atk'])
    d = _num_print(c['def'], c['src_def'])

    return color('{name}{buff_eff}\n'
                 'vid: {vid}{tk}\n'
                 'ATK/{atk} DEF/{def_} 影响力/附加值: {adv}\n'
                 '{loc}'.format(name=c['name'], buff_eff=be, vid=c['vid'],
                                tk=tk, atk=a, def_=d, adv=c['add_val'],
                                loc=location[c['location']]), EColor.DEFAULT_COLOR)


class Player:
    def __init__(self):
        self.deck = list()
        self.side = list()
        self.hand = list()
        self.graveyard = list()
        self.exiled = list()
        # 场上
        self.in_field = list()
        self.leader: dict = None


class StageGame(StageBase):
    """
    游戏页面。
    """
    def __init__(self, st, cmd: list = None):
        super().__init__(st)
        # 对方玩家，使用当前终端的玩家。players[cmd['sd']]即表示指令的发送者。
        self.players = [Player(), Player()]
        self.p1 = self.players[1]
        self.p2 = self.players[0]
        # {vid: {...}, ...}
        # 记录视觉中的卡，洗牌后重置。
        self.visual_cards = dict()
        # game_phase
        self.phase = 0
        self.chessboard = [None for x in range(0, 36)]

        self.tmp_cmd = cmd
        self.running = True
        # 是否为先手玩家。
        self.sp = 0

    def reset(self):
        self.players = [Player(), Player()]
        self.p1 = self.players[1]
        self.p2 = self.players[0]
        self.visual_cards = dict()
        self.phase = 0
        self.chessboard = [None for x in range(0, 36)]
        self.sp = 0

    def enter(self):
        from stages.stage_deck_edit import detail
        self.cmd_set['ans'] = (self.answer, '(ans 文本)响应服务器的请求。')
        self.cmd_set['vid'] = (self.vid, '(vid 卡片vid)从已知的情报中，获取该vid对应的卡的最后可信信息'
                                         '(一些行为会重新生成vid)。')
        self.cmd_set['-d'] = (detail, '(-d 卡片名)显示指定卡的详细信息。')
        # self.cmd_set['r'] = (self.refresh, '刷新。')
        if self.tmp_cmd is not None:
            for c in self.tmp_cmd:
                self.carry_out(c)
        t = Thread(target=self.__listen)
        t.start()
        super().enter()

    def default_cmd(self, cmd):
        if self.running:
            chat(cmd)

    def refresh(self):
        cs = get_commands()
        if cs is not None:
            for c in cs:
                self.carry_out(c)

    def answer(self, *ans):
        if self.running:
            answer(' '.join(ans))

    def vid(self, v):
        v = int(v)
        if v in self.visual_cards:
            color_print(_card_detail(self.visual_cards[v]))
        else:
            color_print('不存在记录。', EColor.ERROR)

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
                  '输入任意内容回到卡组编辑页面。'.format(color(cmd['args'][1], EColor.OP_PLAYER), res)
            col = EColor.EMPHASIS
            self.next_stage = StageDeckEdit(self.status)
        elif cmd['op'] == 'startm':
            msg = '进入对局！输入非指令可以自由发言！'
            col = EColor.EMPHASIS
        elif cmd['op'] == 'startg':
            self.reset()
            msg = '游戏开始！'
            col = EColor.EMPHASIS
        elif cmd['op'] == 'endg':
            msg = '单局游戏结束，{}在单局中取胜。'.format(_get_p(cmd['sd']))
            col = EColor.EMPHASIS
        elif cmd['op'] == 'ent_ph':
            msg = '进入阶段: {}'.format(game_phase[cmd['args'][0]])
        elif cmd['op'] == 'sp_decided':
            self.sp = cmd['sd']
            msg = '{}获得了先手！'.format(_get_p(cmd['sd']))
        elif cmd['op'] == 'upd_vc':
            # 是否完整。
            c = cmd['args'][1]
            if cmd['args'][0] not in self.visual_cards:
                self.add_card(c)
            self.visual_cards[cmd['args'][0]] = cmd['args'][1]
            self.visual_cards[cmd['args'][0]]['whole'] = True
            col = EColor.DEFAULT_COLOR
            if ECardRank(c['rank']) == ECardRank.COMMON:
                col = EColor.COMMON_CARD
            elif ECardRank(c['rank']) == ECardRank.GOOD:
                col = EColor.GOOD_CARD
            elif ECardRank(c['rank']) == ECardRank.TRUMP:
                col = EColor.TRUMP_CARD
            self.visual_cards[cmd['args'][0]]['name'] = color(c['name'], col)
        elif cmd['op'] == 'upd_vc_ano':
            if cmd['args'][0] not in self.visual_cards:
                self.add_card(cmd['args'][1])
            self.visual_cards[cmd['args'][0]] = cmd['args'][1]
            self.visual_cards[cmd['args'][0]]['whole'] = False
        elif cmd['op'] == 'req_shw_crd':
            msg = '请展示1张手牌中的{}卡。'.format(card_rank[cmd['args'][0]])
        elif cmd['op'] == 'req_chs_tgt_f' or cmd['op'] == 'req_chs_tgt':
            i = 0
            for vid in cmd['args'][0]:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       _card_detail(self.visual_cards[vid]) + '\n'
                i += 1
            msg += '请选择{}个目标，输入\"ans 在卡名前方显示的序号\": \n'.format(cmd['args'][1])
        elif cmd['op'] == 'req_go':
            i = 0
            for c in self.p1.hand:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       _card_intro_add_val(c) + '\n'
                i += 1
            msg += '请选择1张手牌放置在棋盘的空位上。\n' \
                   '请输入\"ans 横坐标(0-5) 纵坐标(0-5) ' \
                   '放置的卡序号\"：'
        elif cmd['op'] == 'req_tk_crd':
            msg += '请取走棋盘上的筹码。单次可以取走相邻的2个。\n' \
                   '请输入\"ans 横坐标 纵坐标 ' \
                   '附带取走方向(0表示只取1个, 1表示顺带取走右侧的1个，6表示顺带取走下方的1个。)\"：'
        elif cmd['op'] == 'go':
            x = cmd['args'][0]
            y = cmd['args'][1]
            c = self.visual_cards[cmd['args'][2]]
            self.players[cmd['sd']].hand.remove(c)
            msg = '{}在({}, {})放置了{}。\n'.format(_get_p(cmd['sd']),
                                               x, y, _card_intro_add_val(c))
            self.chessboard[y * 6 + x] = c['vid']
            cs = adj_pos(x, y)
            for ac in cs:
                if self.chessboard[ac] is not None:
                    self.visual_cards[self.chessboard[ac]]['add_val'] += c['add_val']
            self.visual_cards[cmd['args'][2]]['add_val'] = 0
            msg += self._show_chessboard()
        elif cmd['op'] == 'tk_crd':
            x, y, d = cmd['args']
            a = ''
            if d == 1:
                a = '以及其右侧'
                csp = [y * 6 + x, y * 6 + x + 1]
            elif d == 6:
                a = '以及其下方'
                csp = [y * 6 + x, y * 6 + x + 6]
            else:
                csp = [y * 6 + x]
            msg += '{}取走了位于({}, {}){}的卡。\n'.format(_get_p(cmd['sd']), x, y, a)
            cs = list()
            for c in csp:
                cs.append(self.visual_cards[self.chessboard[c]])
                self.chessboard[c] = None
            msg += self._show_chessboard()
            for c in cs:
                self.players[cmd['sd']].hand.append(c)
            if cmd['sd']:
                msg += '您的当前手牌：\n'
                for c in self.p1.hand:
                    msg += _card_detail(c) + '\n'
        elif cmd['op'] == 'shw_crd':
            msg = '{}展示了{}。'.format(_get_p(cmd['sd']),
                                    _card_intro_add_val(self.visual_cards[cmd['args'][0]]))
        elif cmd['op'] == 'ent_tp':
            msg = '进入时点: {}'.format(time_point[cmd['args'][0]])
        elif cmd['op'] == 'shf':
            loc = cmd['args'][0]
            msg = '已洗牌，{}中原先存储的全部卡vid重新生成。'.format(location[loc])
            if location[loc] == '手牌':
                self.players[self._is_mine(loc)].hand = list()
            elif location[loc] == '场上':
                self.players[self._is_mine(loc)].in_field = list()
            elif location[loc] == '场下':
                self.players[self._is_mine(loc)].graveyard = list()
            elif location[loc] == '卡组':
                self.players[self._is_mine(loc)].deck = list()
            elif location[loc] == '备选卡组':
                self.players[self._is_mine(loc)].side = list()
            elif location[loc] == '移除':
                self.players[self._is_mine(loc)].exiled = list()
        elif cmd['op'] == 'lst_all_ano':
            for p in self.players:
                for c in p.hand:
                    msg += _card_intro_add_val(c) + '\n'
        elif cmd['op'] == 'in_err':
            msg = '错误或无效输入orz'
            col = EColor.ERROR
        elif cmd['op'] == 'chat':
            msg = cmd['args']
            col = EColor.OP_PLAYER

        if cmd['op'] not in ignore_list and msg != '':
            self.interrupt_input(msg, col)

    def add_card(self, c):
        if location[c['location']] == '手牌':
            self.players[self._is_mine(c['location'])].hand.append(c)
        elif location[c['location']] == '场上':
            self.players[self._is_mine(c['location'])].in_field.append(c)
        elif location[c['location']] == '场下':
            self.players[self._is_mine(c['location'])].graveyard.append(c)
        elif location[c['location']] == '卡组':
            self.players[self._is_mine(c['location'])].deck.append(c)
        elif location[c['location']] == '备选卡组':
            self.players[self._is_mine(c['location'])].side.append(c)
        elif location[c['location']] == '移除':
            self.players[self._is_mine(c['location'])].exiled.append(c)

    def _is_mine(self, c_loc):
        """
        判断给定的区域是否属于自己。
        :param c_loc:
        :return:
        """
        return (c_loc - self.sp) % 2 == 0

    def _show_chessboard(self):
        r = ''
        for y in range(0, 6):
            for x in range(0, 6):
                vid = self.chessboard[y * 6 + x]
                if vid is not None:
                    r += _card_intro_short(self.visual_cards[vid])
                else:
                    r += color('({}, {})'.format(x, y), EColor.EMPHASIS) + '    、'
            r += '\n'
        return r
