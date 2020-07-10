from custom.e_color import EColor

_color = {EColor.DEFAULT_COLOR: '<dc--|{}>',
          EColor.PLAYER_NAME: '<em--|{}>',
          EColor.OP_PLAYER: '<op--|{}>',
          EColor.EMPHASIS: '<emn-|{}>',
          EColor.ERROR: '<err-|{}>',

          EColor.TRUMP_CARD: '<ct--|{}>',
          EColor.GOOD_CARD: '<cg--|{}>',
          EColor.COMMON_CARD: '<cc--|{}>',

          EColor.ATK: '<atk-|{}>',
          EColor.DEF: '<def-|{}>',

          EColor.GREATER_THAN: '<gt0-|{}>',
          EColor.EQUAL_TO: '<equ-|{}>',
          EColor.LESS_THAN: '<lt0-|{}>',
          }

_color_ind = {'<dc--|': EColor.DEFAULT_COLOR.value,
              '<em--|': EColor.PLAYER_NAME.value,
              '<op--|': EColor.OP_PLAYER.value,
              '<emn-|': EColor.EMPHASIS.value,
              '<err-|': EColor.ERROR.value,

              '<ct--|': EColor.TRUMP_CARD.value,
              '<cg--|': EColor.GOOD_CARD.value,
              '<cc--|': EColor.COMMON_CARD.value,

              '<atk-|': EColor.ATK.value,
              '<def-|': EColor.DEF.value,

              '<gt0-|': EColor.GREATER_THAN.value,
              '<equ-|': EColor.EQUAL_TO.value,
              '<lt0-|': EColor.LESS_THAN.value,
              }


def color_print(text: str, c=EColor.DEFAULT_COLOR, cover=False):
    """
    上色并输出。最外层将自动涂上一层指定的颜色。
    :param text:
    :param c:
    :param single: 是否为单行输出。
    :return:
    """
    stack = list()

    text = color(text, c)
    stack.append(0)
    res_text = ''

    i = 0
    while i < len(text):
        if text[i] == '<':
            if text[i: i+6] in _color_ind.keys():
                # color
                c = _color_ind[text[i: i+6]]
                res_text += '\033[0;{}m'.format(c)
                stack.append(c)
                i += 5
            else:
                assert False
        elif text[i] == '>':
            stack.pop()
            c = stack[-1]
            res_text += '\033[0;{}m'.format(c)
        else:
            res_text += text[i]
        i += 1

    if cover:
        print('\r' + res_text)
    else:
        print(res_text)


def color(text, c=EColor.DEFAULT_COLOR):
    """
    上色。
    :param text:
    :param c:
    :return:
    """
    return _color[c].format(text)
