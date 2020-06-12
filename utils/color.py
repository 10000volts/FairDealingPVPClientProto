from custom.e_color import EColor

_color = {EColor.DEFAULT_COLOR.value: '<dc--|{}>',
          EColor.PLAYER_NAME.value: '<em--|{}>',
          EColor.OP_PLAYER.value: '<op--|{}>',
          EColor.EMPHASIS.value: '<emn-|{}>',
          EColor.ERROR.value: '<err-|{}>',

          EColor.TRUMP_CARD.value: '<ct--|{}>',
          EColor.GOOD_CARD.value: '<cg--|{}>',
          EColor.COMMON_CARD.value: '<cc--|{}>',

          EColor.ATK.value: '<atk-|{}>',
          EColor.DEF.value: '<def-|{}>',
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
              }


def color_print(text: str, c=EColor.DEFAULT_COLOR, single=False):
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

    if single:
        print(res_text, end='\r')
    else:
        print(res_text)


def color(text: str, c=EColor.DEFAULT_COLOR):
    """
    上色。
    :param text:
    :param c:
    :return:
    """
    return _color[c.value].format(text)
