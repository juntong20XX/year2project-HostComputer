"""

"""

from . import main

from threading import Thread


if __name__ == '__main__':
    print("input your Serial path:")
    path = input("[/dev/ttyACM0]:")

    command_like = []

    thread = Thread(target=main, args=(path, command_like), daemon=True)

    thread.start()

    while True:
        deg = input("a number for moving the servo, other for exit:")
        if deg.isdigit():
            print("update:", deg)
            command_like.append((0x0131, int(deg)))
        else:
            print("exit")
            exit(0)
