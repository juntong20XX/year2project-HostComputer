"""

"""
from . import pingloop

from pySerialTransfer import pySerialTransfer as stf

import json
import os
import socket
import time
from typing import Optional
from pathlib import Path
from threading import Thread


def command(s: stf.SerialTransfer, code: int, target, wait_times=3, debug=False, result=None) -> bool:
    """
    发送指令并检查回放
    :param s:
    :param code:
    :param target:
    :param debug:  是否打印调试信息
    :param wait_times: 回放等待重试次数
    :param result: 若非 None 则调用其 append 方法记录执行结果
    :return:
    """
    # 发送指令
    tx_size = 0
    tx_size = s.tx_obj(code, tx_size)
    tx_size = s.tx_obj(target, tx_size)
    s.send(tx_size)
    if debug:
        print(time.time(), "command: get", code, target)
        print("waiting for repeat")

    # 等待回放
    ty = type(target)
    for _ in range(wait_times):
        time.sleep(0.3)
        if not s.available():
            continue
        msg_type: int = s.rx_obj(obj_type='i', start_pos=0)
        data: ty = s.rx_obj(obj_type=ty, start_pos=4, obj_byte_size=4)
        if debug:
            print(time.time(), "command: get repeat", msg_type, data)
        break
    else:
        # 未得到回放
        if debug:
            print(time.time(), "command: NOT get ANY repeat")
        return False
    if not (msg_type == -code and data == target):
        # 回放校验失败
        if debug:
            print(time.time(), "command: repeat check UNSUCCESSFULLY, want",
                  f"({-code}, {data}) get", (msg_type, data))
        return False
    # 发送校验成功消息
    if debug:
        print(time.time(), "command: repeat check SUCCESSFULLY")
    tx_size = 0
    tx_size = s.tx_obj(0x0012, tx_size)
    tx_size = s.tx_obj(0, tx_size)
    s.send(tx_size)
    # 等待执行结果
    if debug:
        print(time.time(), "command: waiting for execution results")
    t = time.time()
    while time.time() - t < 0.3 * wait_times:
        time.sleep(0.2)
        if not s.available():
            continue
        msg_type: int = s.rx_obj(obj_type='i', start_pos=0)
        data: ty = s.rx_obj(obj_type=ty, start_pos=4, obj_byte_size=4)
        if result is not None:
            result.append((msg_type, data))
        if msg_type == 0x0014:
            # 执行成功
            if debug:
                print(time.time(), "command: waiting for execution successfully")
            return True
        else:
            # 执行失败的代码是 0x0013 XXX: 应该有收到未知代码的解决方案
            if debug:
                print(time.time(), "command: waiting for execution results UNSUCCESSFULLY, get code", msg_type)
            return False
    # 超时喽
    if debug:
        print(time.time(), "command: waiting for execution results UNSUCCESSFULLY, TIMEOUT")
    return False


def servo_move(s: stf.SerialTransfer, target: int, debug=False) -> bool:
    """
    控制电机
    指令代码是 0x0131
    :param s:
    :param target: 舵机的目标度数, 应该在 0~180 之间
    :param debug:
    :return: bool 成功或失败
    :raise : ValueError: target not in [0, 180]
    """
    assert 0 <= target <= 180, ValueError('target must be between 0 and 180, get', target)
    return command(s, 0x0131, target, debug=debug)


def servo_get_angle(s: stf.SerialTransfer, debug=False) -> bool | int:
    """
    获取舵机当前角度
    指令代码是 0x0130
    :param s: SerialTransfer 实例
    :param debug: 是否开启调试模式
    :return: bool 成功或失败, int 舵机角度
    """
    result = []
    if command(s, 0x0130, 0, debug=debug, result=result):
        return result[-1][1]
    return False


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
                success = command(s, msg_type, data, debug=debug)
                if success is True:
                    return True
                elif success is False:
                    # 失败
                    command_list.insert(0, (msg_type, data))


def main(command_list: list[(int, str)], serial_path='/dev/ttyACM0', debug=False, stop_cond: Optional[callable] = None):
    link = stf.SerialTransfer(serial_path)
    try:
        if debug:
            print(time.time(), "main: opening serial port", serial_path)
        link.open()
        while stop_cond is None or stop_cond():
            match_and_call(link, command_list, debug=debug)
    finally:
        if debug:
            print(time.time(), "main: exit")
        link.close()


def serial_automatic_detection() -> dict[str, str]:
    """

    :return: {path: id}
    """
    ret = {}
    serial_byid = Path('/dev/serial/by-id')
    if not serial_byid.is_dir():
        # 当没有串口连接时, 该目录不存在
        return ret
    serials = os.listdir(serial_byid)
    for serial in serials:
        p = serial_byid / serial
        if p.is_symlink():
            ret[os.path.abspath(serial_byid / os.readlink(p))] = serial
    return ret


class SerialServer:
    """串口服务器，管理多个串口通信线程和命令列表"""

    def __init__(self, socket_path="/tmp/serial_commander.sock", debug=False):
        self.socket_path = socket_path
        self.debug = debug
        # 存储每个串口的命令列表和线程
        self.serial_threads = {}  # {serial_path: (thread, command_list)}
        self._sock = None
        self._detection_thread = None
        self._last_serials = set()
        self.serial_mapping = None

    def _detect_new_serials(self):
        """检测新的串口设备并启动对应的通信线程，同时关闭已移除的串口"""
        while self._sock is not None:
            self.serial_mapping = serial_automatic_detection()
            current_serials = set(self.serial_mapping)

            # 处理新增的串口
            if new_serials := current_serials - self._last_serials:
                if self.debug:
                    print(time.time(), "检测到新串口设备:", new_serials)
                for serial_path in new_serials:
                    # 为每个新串口创建命令列表和线程
                    command_list = []
                    thread = Thread(
                        target=main,
                        args=(command_list, str(serial_path)),
                        kwargs={"debug": self.debug, "stop_cond": self.is_alive},
                        daemon=True
                    )
                    thread.start()
                    self.serial_threads[str(serial_path)] = (thread, command_list)
                self._last_serials.update(new_serials)

            # 处理移除的串口
            if removed_serials := self._last_serials - current_serials:
                if self.debug:
                    print(time.time(), "检测到串口设备移除:", removed_serials)
                for serial_path in removed_serials:
                    # 从字典中移除对应的线程和命令列表
                    if str(serial_path) in self.serial_threads:
                        thread, _ = self.serial_threads.pop(str(serial_path))
                        # 线程会因为找不到串口因错误结束
                self._last_serials.difference_update(removed_serials)

            time.sleep(1)  # 每秒检测一次

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

        # 启动串口检测线程
        self._detection_thread = Thread(
            target=self._detect_new_serials,
            daemon=True
        )
        self._detection_thread.start()

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
                    match req["cmd"]:
                        case "get_commands":
                            # 返回所有串口的命令列表
                            resp = {
                                "commands": {
                                    path: command_list
                                    for path, (_, command_list) in self.serial_threads.items()
                                }
                            }
                        case "get_serial_mapping":
                            # 返回串口映射关系
                            resp = {
                                "mapping": self.serial_mapping
                            }
                        case "add_command":
                            # 添加新命令到指定串口
                            serial_path = req["serial_path"]
                            if serial_path in self.serial_threads:
                                _, command_list = self.serial_threads[serial_path]
                                command_list.append((req["type"], req["data"]))
                                resp = {"status": "ok"}
                            else:
                                resp = {"status": "error", "message": "串口不存在"}
                        case "stop":
                            # 停止服务器
                            resp = {"status": "ok"}
                            conn.send(json.dumps(resp).encode())
                            self.stop()
                            return
                        case _:
                            resp = {"status": "error"}

                    conn.send(json.dumps(resp).encode())
            finally:
                conn.close()

    def is_alive(self):
        return self._sock is not None

    def stop(self):
        """停止服务器"""
        if self._sock:
            self._sock.close()
            self._sock = None
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

    def get_serial_mapping(self):
        """获取路径和 ID 映射"""
        return self._send_request({"cmd": "get_serial_mapping"})["mapping"]

    def add_command(self, serial_path: str, msg_type: int, data: int):
        """
        添加新命令
        :param serial_path: 串口路径
        :param msg_type: 命令类型 
        :param data: 命令数据
        :rtype: dict
        """
        return self._send_request({
            "cmd": "add_command",
            "serial_path": serial_path,
            "type": msg_type,
            "data": data
        })

    def stop_server(self):
        """停止服务器"""
        return self._send_request({"cmd": "stop"})


def start_server_daemon(debug=False, daemon=True) -> SerialServer:
    """
    在后台启动串口服务器
    :param debug: 是否开启调试模式，默认为 False
    :param daemon: 是否在后台运行，默认为 True
    :return: 启动的服务器实例
    :rtype: SerialServer
    """
    server = SerialServer(debug=debug)
    server_thread = Thread(target=server.start, daemon=daemon)
    server_thread.start()
    return server
