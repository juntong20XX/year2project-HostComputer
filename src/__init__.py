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


def match_and_call(s: stf.SerialTransfer, command_list: list[(int, str)]):
    """
    获取输入, 然后根据输入
    :param s: SerialTransfer
    :param command_list:
    :return:
    """
    if not (msg := get_msg(s)):
        return False
    msg_type, data = msg
    match msg_type:
        case 0x0001:
            # ping
            pingloop.ping_call(msg_type, data, s)
            time.sleep(0.5)
        case 0x0011:
            # wait
            if not command_list:
                # 指令列表为空, 保持状态不动
                msg_type = 0x0020
                data = ""
            else:
                msg_type, data = command_list.pop()
            commander


def main(command_list: list[(int, str)], serial_path='/dev/ttyACM0'):
    link = stf.SerialTransfer(serial_path)
    try:
        link.open()
        while True:
            match_and_call(link, command_list)
    finally:
        link.close()
