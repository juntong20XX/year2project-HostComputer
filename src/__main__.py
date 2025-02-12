"""

"""

from . import main

from threading import Thread


if __name__ == '__main__':
    print("input your Serial path:")
    path = input("[/dev/ttyACM0]:")

    command_list = []

    thread = Thread(target=main, args=(command_list, path), daemon=True)

    thread.start()

    while True:
        deg = input("a number for moving the servo, other for exit:")
        if deg.isdigit():
            print("update:", deg)
            command_list.append((0x0131, int(deg)))
        else:
            print("exit")
            exit(0)
