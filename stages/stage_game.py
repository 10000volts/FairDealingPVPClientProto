from stages.stage_base import StageBase
from utils.color import color, color_print, EColor
from utils.common import get_commands, chat, query_interval, answer
from utils.constants import game_phase, time_point, card_rank, location, ECardRank\
    , effect_desc, turn_phase, ELocation, ECardType, game_err, choice
from custom.msg_ignore import ignore_list

from threading import Thread
from time import sleep
import json


def adj_pos(x, y, sc=6):
    """
    生成临近的合法坐标。
    :param x:
    :param y:
    :param sc: scale 棋盘规模(边长)。
    :return:
    """
    p = y * sc + x
    r = list()
    if x > 0:
        r.append(p - 1)
    if x < sc - 1:
        r.append(p + 1)
    if y > 0:
        r.append(p - sc)
    if y < sc - 1:
        r.append(p + sc)
    return r



def _get_p(p):
    return color('对方', EColor.OP_PLAYER) if p == 0 else \
        color('您', EColor.PLAYER_NAME)


def _num_print(num, src_num):
    if num > src_num:
        return color(str(num), EColor.GREATER_THAN)
    elif num < src_num:
        return color(str(num), EColor.LESS_THAN)
    return color(str(num), EColor.EQUAL_TO)


def _card_intro_on_field(c: dict):
    """
    使用阶段时采用的格式。
    :param c:
    :return:
    """
    be = ''
    if len(c['buff_eff']):
        if len(c['buff_eff']) > 1:
            be = '(..., {})'.format(color(effect_desc[c['buff_eff'][-1]]), EColor.EMPHASIS)
        else:
            be = '({})'.format(color(effect_desc[c['buff_eff'][0]]), EColor.EMPHASIS)
    cover = '(盖放)' if c['cover'] else ''
    if c['whole']:
        if c['type'] == ECardType.EMPLOYEE:
            # 防御姿态
            if c['posture']:
                return '[{vid}]{name}{buff_eff}{cover}[DEF {p}]'.format(
                    name=c['name'], buff_eff=be, cover=cover, vid=c['vid'], p=_num_print(c['def'], c['src_def']))
            else:
                return '[{vid}]{name}{buff_eff}{cover}[ATK {p}]'.format(
                    name=c['name'], buff_eff=be, cover=cover, vid=c['vid'], p=_num_print(c['atk'], c['src_atk']))
        elif c['type'] == ECardType.STRATEGY:
            return '[{vid}]{name}{buff_eff}{cover}[EFF {p}]'.format(
                name=c['name'], buff_eff=be, cover=cover, vid=c['vid'], p=_num_print(c['atk'], c['src_atk']))
        elif c['type'] == ECardType.LEADER:
            return '领袖'
    else:
        return '[{vid}]？？？{buff_eff}{cover}[{adv}]'.format(
            buff_eff=be, vid=c['vid'], cover=cover, adv=_num_print(c['add_val'], 0))


def _card_intro_short(c: dict):
    """
    放置/取走阶段时采用的格式。
    :param c:
    :return:
    """
    if c['whole']:
        return '{name} {adv} '.format(name=c['name'], adv=_num_print(c['add_val'], 0))
    else:
        return '？？？ {adv} '.format(adv=_num_print(c['add_val'], 0))


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
    if c is None:
        return '(empty)'
    be = ''
    if len(c['buff_eff']):
        be = '({})'.format(color(effect_desc[c['buff_eff'][-1]]), EColor.EMPHASIS)
    if not c['whole']:
        return color('？？？{buff_eff}\n'
                     'vid: {vid}\n'
                     '影响力/附加值: {adv}\n'
                     '{loc}'.format(buff_eff=be, vid=c['vid'], adv=_num_print(c['add_val'], 0),
                                    loc=location[c['location']]), EColor.DEFAULT_COLOR)
    tk = ''
    if int(c['is_token']):
        tk = color('(衍生)', EColor.EMPHASIS)
    a = _num_print(c['atk'], c['src_atk'])
    d = _num_print(c['def'], c['src_def'])

    if c['type'] == ECardType.EMPLOYEE:
        return color('{name}{buff_eff}\n'
                     'vid: {vid}{tk}\n'
                     'ATK/{atk} DEF/{def_} 影响力/附加值: {adv}\n'
                     '{loc}'.format(name=c['name'], buff_eff=be, vid=c['vid'],
                                    tk=tk, atk=a, def_=d, adv=c['add_val'],
                                    loc=location[c['location']]), EColor.DEFAULT_COLOR)
    elif c['type'] == ECardType.STRATEGY:
        return color('{name}{buff_eff}\n'
                     'vid: {vid}{tk}\n'
                     'EFF/{atk} 影响力/附加值: {adv}\n'
                     '{loc}'.format(name=c['name'], buff_eff=be, vid=c['vid'],
                                    tk=tk, atk=a, adv=c['add_val'],
                                    loc=location[c['location']]), EColor.DEFAULT_COLOR)
    elif c['type'] == ECardType.LEADER:
        return color('领袖{buff_eff}\n'
                     'vid: {vid}\n'
                     '剩余生命力: {def_}\n'.format(buff_eff=be, vid=c['vid'],
                                              def_=d), EColor.DEFAULT_COLOR)


class FixedLengthList(list):
    def __init__(self, count):
        super().__init__([None for x in range(0, count)])

    def remove(self, obj) -> None:
        for i in range(0, len(self)):
            if self[i] == obj:
                self[i] = None

    def append(self, obj) -> None:
        assert False


class Player:
    def __init__(self):
        self.deck = list()
        self.side = list()
        self.hand = list()
        self.grave = list()
        self.exiled = list()
        # 场上
        self.on_field = FixedLengthList(6)
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
        self.chessboard = FixedLengthList(36)
        # 是否为先手玩家。
        self.sp = 0

        self.tmp_cmd = cmd
        self.running = True

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
        self.cmd_set['-d'] = (detail, '(-d 卡片名)根据卡名查询卡并显示其详细信息。')
        self.cmd_set['-l'] = (self.list_cards, '(-l 区域代码)查询指定区域中的全部卡。'
                                               '可选的区域代码: 5、6、9、10、17、18、33、34、65、66、129、130')
        self.cmd_set['play'] = (self.play, '(play 手牌序号 放置位置(0-2:雇员区域 3-5:策略区域)) '
                                           '雇员入场姿态(0为进攻姿态，1为防御姿态，策略不填此项))'
                                           '尝试使手牌中指定的雇员或策略登场。')
        self.cmd_set['act'] = (self.act, '获取我方可发动的主动非触发效果的列表。')
        self.cmd_set['set'] = (self.set, '(set 手牌序号 放置位置(0-2:雇员区域 3-5:策略区域))'
                               '从手牌盖放卡到场上。')
        self.cmd_set['cp'] = (self.cp, '(cp 自己场上的卡序号)尝试作指定雇员的姿态转换/发动盖放的指定策略。')
        self.cmd_set['atk'] = (self.attack, '(atk 想要发起攻击的雇员序号)尝试用指定的雇员发动攻击。')
        self.cmd_set['np'] = (self.np, '进入自己回合的下一个阶段(主要阶段1-战斗阶段-主要阶段2-回合结束)。')
        self.cmd_set['c'] = (self.cancel, '取消当前的非强制操作。')
        self.cmd_set['gg'] = (self.give, '在单局中认输。')
        if self.tmp_cmd is not None:
            for c in self.tmp_cmd:
                self.carry_out(c)
        t = Thread(target=self.__listen)
        t.start()
        super().enter()

    def default_cmd(self, cmd):
        if self.running:
            color_print('聊天消息已发送~')
            chat(cmd)

    def refresh(self):
        cs = get_commands()
        if cs is not None:
            for c in cs:
                self.carry_out(c)

    def answer(self, *ans):
        if self.running:
            answer(' '.join([str(a) for a in ans]))

    def play(self, *args):
        self.answer(0, *args)

    def act(self):
        self.answer(1, 0)

    def set(self, ind, f_ind):
        self.answer(2, ind, f_ind)

    def cp(self, ind):
        self.answer(6, ind)

    def attack(self, ind):
        self.answer(3, ind)

    def np(self):
        self.answer(4, 0)

    def give(self):
        self.answer(5, 0)

    def cancel(self):
        self.answer('cancel')

    def vid(self, v):
        v = int(v)
        if v in self.visual_cards:
            color_print(_card_detail(self.visual_cards[v]))
        else:
            color_print('不存在记录。', EColor.ERROR)

    def list_cards(self, loc):
        ls = self.get_from(int(loc))
        for i in range(0, len(ls)):
            if ls[i] is not None:
                color_print('[{}]{}'.format(color(i, EColor.EMPHASIS), _card_detail(self.visual_cards[ls[i]])))

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
            msg = '单局游戏结束，{}在单局中取胜。 获胜原因: {}'.format(_get_p(cmd['sd']), cmd['args'][0])
            col = EColor.EMPHASIS
        elif cmd['op'] == 'ent_ph':
            self.phase = cmd['args'][0]
            msg = '进入阶段: {}'.format(game_phase[cmd['args'][0]])
        elif cmd['op'] == 'sp_decided':
            self.sp = cmd['sd']
            msg = '{}获得了先手！'.format(_get_p(cmd['sd']))
        elif cmd['op'] == 'upd_vc':
            # 是否完整。
            c = cmd['args'][1]
            if c['type'] == ECardType.LEADER:
                if self.get_player(c['location']) is self.p1:
                    self.p1.leader = c
                else:
                    self.p2.leader = c
                self.visual_cards[cmd['args'][0]] = c
                self.visual_cards[cmd['args'][0]]['whole'] = True
            else:
                if cmd['args'][0] not in self.visual_cards:
                    self.add_card(c)
                # 已存在但位置不同时修改目前所处位置(使用阶段时)。
                else:
                    if self.phase == 7:
                        old = self.visual_cards[cmd['args'][0]]
                        if c['location'] != old['location']:
                            if self.get_from(old['location']) is not None and\
                                    old['vid'] in self.get_from(old['location']):
                                self.get_from(old['location']).remove(old['vid'])
                            self.add_card(c)
                # if c['location'] & ELocation.ON_FIELD:
                #     msg += self._show_field()
                self.visual_cards[cmd['args'][0]] = c
                self.visual_cards[cmd['args'][0]]['whole'] = True
                col = EColor.DEFAULT_COLOR
                if c['rank'] == ECardRank.COMMON:
                    col = EColor.COMMON_CARD
                elif c['rank'] == ECardRank.GOOD:
                    col = EColor.GOOD_CARD
                elif c['rank'] == ECardRank.TRUMP:
                    col = EColor.TRUMP_CARD
                self.visual_cards[cmd['args'][0]]['name'] = color(c['name'], col)
        elif cmd['op'] == 'upd_vc_ano':
            c = cmd['args'][1]
            if cmd['args'][0] not in self.visual_cards:
                self.add_card(c)
            # 已存在但位置不同时修改目前所处位置。
            else:
                old = self.visual_cards[cmd['args'][0]]
                if c['location'] != old['location']:
                    l = self.get_from(old['location'])
                    if l is not None:
                        l.remove(old['vid'])
                    self.add_card(c)
            self.visual_cards[cmd['args'][0]] = c
            self.visual_cards[cmd['args'][0]]['whole'] = False
        elif cmd['op'] == 'req_rct':
            if cmd['args'][0] is None:
                msg = '您有可以使用的主动效果，是否发动？'
            else:
                msg = '当前时点: {}\n您有效果可以连锁发动，是否连锁？'.format(time_point[cmd['args'][0]])
        elif cmd['op'] == 'req_yn':
            msg = '是/否？(回复\"ans 1或0\")'
        elif cmd['op'] == 'req_chs_eff':
            i = 0
            for ef in cmd['args'][0]:
                msg += '[{}]{}\n{}\n'.format(color(str(i), EColor.EMPHASIS),
                                           _card_intro_on_field(self.visual_cards[ef[0]]), effect_desc[ef[1]])
                i += 1
            msg += '请选择要发动的效果：(回复\"ans 效果序号\"或\"c\"取消)'
        elif cmd['op'] == 'req_shw_crd':
            msg = '请展示1张手牌中的{}卡。'.format(card_rank[cmd['args'][0]])
        elif cmd['op'] == 'req_shw_crd':
            msg = '请展示1张手牌中的{}卡。'.format(card_rank[cmd['args'][0]])
        elif cmd['op'] == 'req_chs_tgt_f' or cmd['op'] == 'req_chs_tgt':
            i = 0
            for vid in cmd['args'][0]:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       _card_detail(self.visual_cards[vid]) + '\n'
                i += 1
            msg += '请选择{}个目标，输入\"ans 在卡名前方显示的序号\": '.format(cmd['args'][1])
        elif cmd['op'] == 'req_chs' or cmd['op'] == 'req_chs_tgt':
            i = 0
            for ch in cmd['args'][0]:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       color(choice[ch], EColor.EMPHASIS) + '\n'
                i += 1
            msg += '请选择{}个选项，输入\"ans 在卡名前方显示的序号\": '.format(cmd['args'][1])
        elif cmd['op'] == 'req_go':
            i = 0
            for c in self.p1.hand:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       _card_intro_add_val(self.visual_cards[c]) + '\n'
                i += 1
            msg += '请选择1张手牌放置在棋盘的空位上。\n' \
                   '请输入\"ans 横坐标(0-5) 纵坐标(0-5) ' \
                   '放置的卡序号\"：'
        elif cmd['op'] == 'req_tk_crd':
            msg += '请取走棋盘上的筹码。单次可以取走相邻的2个。\n' \
                   '请输入\"ans 横坐标 纵坐标 ' \
                   '附带取走方向(0表示只取1个, 1表示顺带取走右侧的1个，6表示顺带取走下方的1个。)\"：'
        elif cmd['op'] == 'req_op':
            msg += '轮到您行动！使用-h查看帮助。'
        elif cmd['op'] == 'req_atk':
            i = 0
            for vid in cmd['args'][0]:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       _card_detail(self.visual_cards[vid]) + '\n'
                i += 1
            msg += '发起攻击！请输入\"ans 卡序号\"选择攻击目标！(输入\"c\"取消攻击)'
        elif cmd['op'] == 'req_blk':
            i = 0
            for vid in cmd['args'][0]:
                msg += '[{}]'.format(color(str(i), EColor.EMPHASIS)) + \
                       _card_detail(self.visual_cards[vid]) + '\n'
                i += 1
            msg += '您被直接攻击！输入\"ans 卡序号\"进行阻挡！(输入\"c\"取消阻挡)'
        elif cmd['op'] == 'req_pos':
            msg += '请输入\"ans 位置序号\"来指定位置。'
        elif cmd['op'] == 'req_pst':
            msg += '请输入\"ans 0(进攻姿态)或1(防御姿态)\"来指定雇员入场姿态。'
        elif cmd['op'] == 'req_num':
            msg += '请输入\"ans 一个在[{}, {}]的数字\"。'.format(cmd['args'][0], cmd['args'][1])
        elif cmd['op'] == 'go':
            x = cmd['args'][0]
            y = cmd['args'][1]
            c = self.visual_cards[cmd['args'][2]]
            self.players[cmd['sd']].hand.remove(c['vid'])
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
            pos, d = cmd['args']
            x = pos % 6
            y = int(pos / 6)
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
                cs.append(self.chessboard[c])
                self.chessboard[c] = None
            msg += self._show_chessboard()
            for c in cs:
                self.players[cmd['sd']].hand.append(c)
            if cmd['sd']:
                msg += '您的当前手牌：\n'
                for c in self.p1.hand:
                    msg += _card_detail(self.visual_cards[c]) + '\n'
        elif cmd['op'] == 'shw_crd':
            msg = '{}展示了{}。'.format(_get_p(cmd['sd']),
                                    _card_intro_add_val(self.visual_cards[cmd['args'][0]]))
        elif cmd['op'] == 'smn':
            vid = cmd['args'][0]
            method = '常规' if cmd['args'][1] else ''
            c = self.visual_cards[vid]
            posture = '防御姿态' if c['posture'] else '进攻姿态'
            msg = '{}的{}以{}{}入场！\n'.format(_get_p(cmd['sd']), _card_intro_add_val(c),
                                           posture, method)
            # 卡片位置的改变在upd_vc/upd_ano_vc中实现
            msg += self._show_field()
        elif cmd['op'] == 'act_stg':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}在位置{}发动了{}！\n'.format(_get_p(cmd['sd']), c['inf_pos'], _card_intro_on_field(c))
            # 卡片位置的改变在upd_vc/upd_ano_vc中实现
            msg += self._show_field()
        elif cmd['op'] == 'cst_eff':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}的{}效果发动中...\n'.format(_get_p(cmd['sd']), _card_intro_on_field(c))
        elif cmd['op'] == 'act_eff':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}的{}效果发动！\n'.format(_get_p(cmd['sd']), _card_intro_on_field(c))
        elif cmd['op'] == 'set_crd':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}在位置{}盖放了卡！\n'.format(_get_p(cmd['sd']), c['inf_pos'])
            # 卡片位置的改变在upd_vc/upd_ano_vc中实现
            msg += self._show_field()
        elif cmd['op'] == 'crd_dcd':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}的{}被丢弃！'.format(self.get_player_name(c), _card_intro_on_field(c))
            msg += self._show_field()
        elif cmd['op'] == 'crd_snd2hnd':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}的{}加入了手牌！'.format(self.get_player_name(c), _card_intro_on_field(c))
            msg += self._show_field()
        elif cmd['op'] == 'crd_snd2grv':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}的{}送去了场下！'.format(self.get_player_name(c), _card_intro_on_field(c))
            msg += self._show_field()
        elif cmd['op'] == 'crd_snd2exd':
            vid = cmd['args'][0]
            c = self.visual_cards[vid]
            msg = '{}的{}被移除！'.format(self.get_player_name(c), _card_intro_on_field(c))
            msg += self._show_field()
        elif cmd['op'] == 'atk':
            attacker = self.visual_cards[cmd['args'][0]]
            target = self.visual_cards[cmd['args'][1]]
            msg = '{}的{}对{}发起了攻击！'.format(self.get_player_name(attacker), _card_intro_on_field(attacker),
                                          _card_intro_on_field(target))
        elif cmd['op'] == 'blk':
            blocker = self.visual_cards[cmd['args'][0]]
            msg = '{}使用{}进行阻挡！'.format(self.get_player_name(blocker), _card_intro_on_field(blocker))
        elif cmd['op'] == 'dmg':
            c = self.visual_cards[cmd['args'][0]]
            dmg = cmd['args'][1]
            # todo: 当前版本中不存在拥有HP的雇员所以可以这么写，但是之后的版本中存在用HP代替DEF的合约雇员。
            msg = '{}受到了{}伤害！剩余生命力: {}'.format(self.get_player_name(c), dmg, _num_print(c['def'], 10000))
        elif cmd['op'] == 'hea':
            c = self.visual_cards[cmd['args'][0]]
            dmg = cmd['args'][1]
            # todo: 当前版本中不存在拥有HP的雇员所以可以这么写，但是之后的版本中存在用HP代替DEF的合约雇员。
            msg = '{}的生命力回复了{}！剩余生命力: {}'.format(self.get_player_name(c), dmg, _num_print(c['def'], 10000))
        elif cmd['op'] == 'hp_cst':
            c = self.visual_cards[cmd['args'][0]]
            dmg = cmd['args'][1]
            # todo: 当前版本中不存在拥有HP的雇员所以可以这么写，但是之后的版本中存在用HP代替DEF的合约雇员。
            msg = '{}支付了{}生命力！剩余生命力: {}'.format(self.get_player_name(c), dmg, _num_print(c['def'], 10000))
        elif cmd['op'] == 'crd_des':
            c = self.visual_cards[cmd['args'][0]]
            msg = '{}的{}被摧毁！'.format(self.get_player_name(c), _card_intro_on_field(c))
        elif cmd['op'] == 'crd_cp':
            c = self.visual_cards[cmd['args'][0]]
            msg = '{}的{}转换了姿态！'.format(self.get_player_name(c), _card_intro_on_field(c))
        elif cmd['op'] == 'ent_tp':
            msg = '进入时点: {}'.format(time_point[cmd['args'][0]])
        elif cmd['op'] == 'ent_tph':
            msg = '{}进入{}！'.format(_get_p(cmd['sd']), turn_phase[cmd['args'][0]])
        elif cmd['op'] == 'shf':
            loc = cmd['args'][0]
            msg = '已洗牌，{}中原先存储的全部卡vid重新生成。'.format(location[loc])
            if location[loc] == '手牌':
                self.get_player(loc).hand = list()
            elif location[loc] == '场上':
                self.get_player(loc).on_field = FixedLengthList(6)
            elif location[loc] == '场下':
                self.get_player(loc).grave = list()
            elif location[loc] == '卡组':
                self.get_player(loc).deck = list()
            elif location[loc] == '备选卡组':
                self.get_player(loc).side = list()
            elif location[loc] == '移除':
                self.get_player(loc).exiled = list()
        elif cmd['op'] == 'lst_all_ano':
            for p in self.players:
                for c in p.hand:
                    msg += _card_intro_add_val(self.visual_cards[c]) + '\n'
        elif cmd['op'] == 'in_err':
            msg = game_err[cmd['args'][0]] + '(您的输入: \"{}\")'.format(self.last_cmd)
            col = EColor.ERROR
        elif cmd['op'] == 'chat':
            msg = cmd['args']
            col = EColor.OP_PLAYER

        if cmd['op'] not in ignore_list and msg != '':
            self.interrupt_input(msg, col)

    def add_card(self, c) -> None:
        if c['location'] & ELocation.ON_FIELD:
            assert self.get_player(c['location']).on_field[c['inf_pos']] is None
            self.get_player(c['location']).on_field[c['inf_pos']] = c['vid']
        else:
            l = self.get_from(c['location'])
            if l is not None:
                l.append(c['vid'])

    def get_from(self, loc) -> list:
        if loc & ELocation.ON_FIELD:
            return self.get_player(loc).on_field
        elif loc & ELocation.HAND:
            return self.get_player(loc).hand
        elif loc & ELocation.DECK:
            return self.get_player(loc).deck
        elif loc & ELocation.SIDE:
            return self.get_player(loc).side
        elif loc & ELocation.GRAVE:
            return self.get_player(loc).grave
        elif loc & ELocation.EXILED:
            return self.get_player(loc).exiled
        return None

    def get_player(self, loc) -> Player:
        """
        判断给定的区域所属的玩家。
        :param loc:
        :return:
        """
        return self.players[loc % 2 == self.sp]

    def get_player_name(self, c):
        return _get_p(c['location'] % 2 == self.sp)

    def _show_chessboard(self):
        r = ''
        for y in range(0, 6):
            for x in range(0, 6):
                vid = self.chessboard[y * 6 + x]
                if vid is not None:
                    r += '[{}]{}'.format(color(x, EColor.EMPHASIS), _card_intro_short(self.visual_cards[vid]))
                else:
                    r += color('({}, {})'.format(x, y), EColor.EMPHASIS) + '      '
            r += '\n'
        return r

    op_ind_list = [3, 4, 5, 0, 1, 2]
    my_ind_list = [0, 1, 2, 3, 4, 5]
    def _show_field(self):
        """
        展示场上的情况。
        :return:
        """
        r = '\n{}剩余生命力: {}\n'.format(color('对方', EColor.OP_PLAYER), _num_print(self.p2.leader['def'], 10000))
        for i in self.op_ind_list:
            if self.p2.on_field[i] is not None:
                r += '[{}]{} '.format(i, _card_intro_on_field(self.visual_cards[self.p2.on_field[i]]))
            else:
                r += '[{}](empty)          '.format(i)
            if (i == 5) | (i == 2):
                r += '\n'
        r += '{}的剩余生命力: {}\n'.format(color('您', EColor.PLAYER_NAME), _num_print(self.p1.leader['def'], 10000))
        for i in self.my_ind_list:
            if self.p1.on_field[i] is not None:
                r += '[{}]{} '.format(color(i, EColor.EMPHASIS),
                                      _card_intro_on_field(self.visual_cards[self.p1.on_field[i]]))
            else:
                r += '[{}](empty)          '.format(color(i, EColor.EMPHASIS))
            if (i == 5) | (i == 2):
                r += '\n'
        return r
