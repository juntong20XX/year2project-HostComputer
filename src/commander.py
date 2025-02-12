"""

"""
from pySerialTransfer import pySerialTransfer as stf

import time


def command(s: stf.SerialTransfer, code: int, target, wait_times=3) -> bool:
    """
    发送指令并检查回放
    :param s:
    :param code:
    :param target:
    :param wait_times: 回放等待重试次数
    :return:
    """
    # 发送指令
    tx_size = 0
    tx_size = s.tx_obj(code, tx_size)
    tx_size = s.tx_obj(target, tx_size)
    s.send(tx_size)

    # 等待回放
    ty = type(target)
    for _ in range(wait_times):
        time.sleep(0.3)
        if not s.available():
            continue
        msg_type: int = s.rx_obj(obj_type='i', start_pos=0)
        data: ty = s.rx_obj(obj_type=ty, start_pos=4, obj_byte_size=4)
        break
    else:
        # 未得到回放
        return False
    if not (msg_type == -code and data == target):
        # 回放校验失败
        return False
    # 发送校验成功消息
    tx_size = 0
    tx_size = s.tx_obj(0x0012, tx_size)
    tx_size = s.tx_obj(0, tx_size)
    s.send(tx_size)
    return False


def servo_move(s: stf.SerialTransfer, target: int) -> bool:
    """
    控制电机
    指令代码是 0x0131
    :param s:
    :param target: 舵机的目标度数, 应该在 0~180 之间
    :return: bool 成功或失败
    :raise : ValueError: target not in [0, 180]
    """
    assert 0 <= target <= 180, ValueError('target must be between 0 and 180, get', target)
    return command(s, 0x0131, target)
