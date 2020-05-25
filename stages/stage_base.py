import custom.e_color

iset = dict()

class StageBase:
    def __init__(self):
        iset = {'-h': print_help}

    def enter(self):
        while True:
            cmd = input("请输入指令。(键入-h获得帮助)")
            if cmd == 'exit':
                break
            elif cmd in self.get_instruction_set():
                iset[cmd]()

    def get_instruction_set(self):
        return iset


def print_help():
    print('')
