"""
转动一下舵机
"""

from pySerialTransfer import pySerialTransfer as stf

import time


def ping_call(msg_type, data, s: stf.SerialTransfer):
    if msg_type == 0x01 and data == "a1nn":
        s.tx_obj(0x0001, 0)
        s.tx_obj("-hc-", 4)
        s.send(8)


def get_msg(s: stf.SerialTransfer) -> tuple[int, str] | bool:
    if not s.available():
        return False
    msg_type: int = s.rx_obj(obj_type='i', start_pos=0)
    data: str = s.rx_obj(obj_type=str, start_pos=4, obj_byte_size=4)
    return msg_type, data


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
    print("send cmd")
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
        print("no reply")
        return False
    print("Check reply", msg_type, data)
    if not (msg_type == -code and data == target):
        # 回放校验失败
        print("not pass")
        return False
    print("check passed")
    # 发送校验成功消息
    tx_size = 0
    tx_size = s.tx_obj(0x0012, tx_size)
    tx_size = s.tx_obj(0, tx_size)
    s.send(tx_size)
    return True


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


def degree_loop():
    while True:
        yield from [90, 130, 170, 130, 90, 50, 10, 40]


def match_and_call(s: stf.SerialTransfer, degrees):
    """
    获取输入, 然后根据输入
    :param s: SerialTransfer
    :param degrees:
    :return:
    """
    if not (msg := get_msg(s)):
        return False
    msg_type, data = msg
    print(time.time(), hex(msg_type)[2:].rjust(4, "0"), data)
    match msg_type:
        case 0x0001:
            # ping
            print("ping")
            ping_call(msg_type, data, s)
            time.sleep(0.3)
        case 0x0011:
            # wait
            d = next(degrees)
            print("wait", "servo_move to", d)
            servo_move(s, d)
            time.sleep(1)


def main(serial_path='/dev/ttyACM0'):
    link = stf.SerialTransfer(serial_path)
    degrees = degree_loop()
    try:
        link.open()
        while True:
            match_and_call(link, degrees)
    finally:
        link.close()


if __name__ == '__main__':
    main()
