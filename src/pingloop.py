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
    # XXXX: skip check
    return msg_type == 0x01 and data == "a1nn"


def send_ack(s: stf.SerialTransfer):
    s.tx_obj(0x0001, 0)
    s.tx_obj(0, 4)

    s.send(8)


if __name__ == '__main__':
    link = stf.SerialTransfer('/dev/ttyACM0')
    try:
        link.open()
        while True:
            print(time.time(), check_ping(link))
            send_ack(link)
            time.sleep(1)
    finally:
        link.close()
