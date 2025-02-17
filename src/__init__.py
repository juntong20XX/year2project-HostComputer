"""

"""
from . import pingloop, commander

from pySerialTransfer import pySerialTransfer as stf

import os
import json
import time
import socket
from threading import Thread


def get_msg(s: stf.SerialTransfer) -> tuple[int, str] | bool:
    if not s.available():
        return False
    msg_type: int = s.rx_obj(obj_type='i', start_pos=0)
    data: str = s.rx_obj(obj_type=str, start_pos=4, obj_byte_size=4)
    return msg_type, data


def match_and_call(s: stf.SerialTransfer, command_list: list[(int, str)], debug=False) -> tuple[int, str] | bool:
    """
    获取输入, 然后根据输入
    :param s: SerialTransfer
    :param command_list:
    :param debug:
    :return:
    """
    if not (msg := get_msg(s)):
        return False
    msg_type, data = msg
    if debug:
        print(time.time(), "before match:", f"msg_type: {msg_type}, data: {data}")
    match msg_type:
        case 0x0001:
            # ping
            if debug:
                print(time.time(), f"[{msg_type}]", "matched ping")
            pingloop.ping_call(msg_type, data, s)
            time.sleep(0.3)
        case 0x0011:
            # wait
            if debug:
                print(time.time(), f"[{msg_type}]", "matched ping")
            if not command_list:
                # 指令列表为空, 直接成功
                if debug:
                    print(time.time(), "command list is empty, exit")
                return True
            else:
                msg_type, data = command_list.pop(0)
                # 发送指令
                if debug:
                    print(time.time(), "send command", f"command_code {msg_type}, data: {data}")
                success = commander.command(s, msg_type, data, debug=debug)
                if success is True:
                    return True
                elif success is False:
                    # 失败
                    command_list.insert(0, (msg_type, data))


def main(command_list: list[(int, str)], serial_path='/dev/ttyACM0', debug=False):
    link = stf.SerialTransfer(serial_path)
    try:
        if debug:
            print(time.time(), "main: opening serial port", serial_path)
        link.open()
        while True:
            match_and_call(link, command_list, debug=debug)
    finally:
        if debug:
            print(time.time(), "main: exit")
        link.close()


class SerialServer:
    """串口服务器，管理串口通信线程和命令列表"""
    def __init__(self, socket_path="/tmp/serial_commander.sock", serial_path="/dev/ttyACM0", debug=False):
        self.socket_path = socket_path
        self.serial_path = serial_path
        self.debug = debug
        self.command_list = []
        self._thread = None
        self._sock = None

    def start(self):
        """启动服务器"""
        # 确保socket文件不存在
        try:
            os.unlink(self.socket_path)
        except OSError:
            if os.path.exists(self.socket_path):
                raise

        # 创建unix domain socket
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self.socket_path)
        self._sock.listen(1)

        # 启动串口通信线程
        self._thread = Thread(
            target=main,
            args=(self.command_list, self.serial_path),
            kwargs={"debug": self.debug},
            daemon=True
        )
        self._thread.start()

        # 处理客户端连接
        while True:
            conn, addr = self._sock.accept()
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    # 解析客户端请求
                    req = json.loads(data.decode())
                    if req["cmd"] == "get_commands":
                        # 返回当前命令列表
                        resp = {"commands": self.command_list}
                    elif req["cmd"] == "add_command":
                        # 添加新命令
                        self.command_list.append((req["type"], req["data"]))
                        resp = {"status": "ok"}
                    elif req["cmd"] == "stop":
                        # 停止服务器
                        resp = {"status": "ok"}
                        conn.send(json.dumps(resp).encode())
                        self.stop()
                        return
                    
                    conn.send(json.dumps(resp).encode())
            finally:
                conn.close()

    def stop(self):
        """停止服务器"""
        if self._sock:
            self._sock.close()
        os.unlink(self.socket_path)


class SerialClient:
    """串口客户端，用于向服务器发送命令"""
    def __init__(self, socket_path="/tmp/serial_commander.sock"):
        self.socket_path = socket_path

    def _send_request(self, req):
        """发送请求到服务器"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.socket_path)
            sock.send(json.dumps(req).encode())
            return json.loads(sock.recv(1024).decode())
        finally:
            sock.close()

    def get_commands(self):
        """获取当前命令列表"""
        return self._send_request({"cmd": "get_commands"})["commands"]

    def add_command(self, msg_type: int, data: int):
        """添加新命令"""
        return self._send_request({
            "cmd": "add_command",
            "type": msg_type,
            "data": data
        })

    def stop_server(self):
        """停止服务器"""
        return self._send_request({"cmd": "stop"})


def start_server_daemon(serial_path="/dev/ttyACM0", debug=False, daemon=True) -> SerialServer:
    """在后台启动串口服务器
    
    Args:
        serial_path: 串口路径，默认为 /dev/ttyACM0
        debug: 是否开启调试模式，默认为 False
        daemon: 是否在后台运行，默认为 True    

    Returns:
        server: 启动的服务器实例
    """
    server = SerialServer(serial_path=serial_path, debug=debug)
    server_thread = Thread(target=server.start, daemon=daemon)
    server_thread.start()
    return server

