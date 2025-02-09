"""
周期性测试连接
"""

import time
from pySerialTransfer import pySerialTransfer as stf


def check_ping(s: stf.SerialTransfer):
    if not s.available():
        return s.status
    msg_type: int = s.rx_obj(obj_type='i', start_pos=0)
    data: str = s.rx_obj(obj_type=str, start_pos=4, obj_byte_size=4)
    print(msg_type, data)
    return msg_type == 0x01 and data == "a1nn"


def send_ack(s: stf.SerialTransfer):
    tx_size = 0
    tx_size = s.tx_obj(0x0001, tx_size)
    tx_size = s.tx_obj("-hc-", tx_size)

    s.send(tx_size)


if __name__ == '__main__':
    link = stf.SerialTransfer('/dev/ttyACM0')
    try:
        link.open()
        while True:
            res = check_ping(link)
            print(time.time(), res)
            if res is True:
                send_ack(link)
            time.sleep(0.5)
    finally:
        link.close()
