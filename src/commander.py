"""

"""
from pySerialTransfer import pySerialTransfer as stf

import time


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

