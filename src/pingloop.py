"""
周期性测试连接
"""

import time
from pySerialTransfer import pySerialTransfer as stf


def check_ping(msg_type, data):
    return msg_type == 0x01 and data == "a1nn"


def send_ack(s: stf.SerialTransfer):
    s.tx_obj(0x0001, 0)
    s.tx_obj("-hc-", 4)

    s.send(8)


def ping_call(msg_type, data, s: stf.SerialTransfer):
    res = check_ping(msg_type, data)
    if res is True:
        send_ack(s)


if __name__ == '__main__':
    link = stf.SerialTransfer('/dev/ttyACM0')
    try:
        link.open()
        while True:
            if not link.available():
                continue
            ping_call(link.rx_obj(obj_type='i', start_pos=0),
                      link.rx_obj(obj_type=str, start_pos=4, obj_byte_size=4),
                      link)
            time.sleep(0.5)
    finally:
        link.close()
