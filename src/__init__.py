"""

"""
from . import pingloop, commander

from pySerialTransfer import pySerialTransfer as stf

import time


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
        link.open()
        while True:
            match_and_call(link, command_list, debug=debug)
    finally:
        link.close()
