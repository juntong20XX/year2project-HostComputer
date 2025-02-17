"""

"""

from . import start_server_daemon, SerialClient


if __name__ == '__main__':
    print("input your Serial path:")
    path = input("[/dev/ttyACM0]:")

    if not path:
        path = "/dev/ttyACM0"

    # 创建并启动服务器
    server = start_server_daemon(serial_path=path, debug=True)

    # 创建客户端
    client = SerialClient()

    try:
        while True:
            deg = input("a number for moving the servo, other for exit:")
            if deg.isdigit():
                print("update:", deg)
                client.add_command(0x0131, int(deg))
            else:
                print("exit")
                server.stop()
                exit(0)
    except KeyboardInterrupt:
        server.stop()
        print("server stopped")
        exit(0)
