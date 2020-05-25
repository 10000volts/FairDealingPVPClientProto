from custom.e_color import EColor

_color = {EColor.DEFAULT_COLOR.value: '<dc--|{}>',
          EColor.PLAYER_NAME.value: '<pn--|{}>',

          EColor.TRUMP_CARD.value: '<ct--|{}>'}

_color_ind = {'<dc--|': EColor.DEFAULT_COLOR.value,
              '<pn--|': EColor.PLAYER_NAME.value,

              '<ct--|': EColor.TRUMP_CARD.value,}


def color_print(text: str):
    """
    上色并输出。最外层将自动涂上一层默认颜色。
    :param text:
    :return:
    """
    stack = list()

    text = color(text, EColor.DEFAULT_COLOR)
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

    print(res_text)


def color(text: str, c):
    """
    上色。
    :param text:
    :param c:
    :return:
    """
    return _color[c.value].format(text)
