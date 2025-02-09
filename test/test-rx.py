import time
from pySerialTransfer import pySerialTransfer as txfer


class Struct:
    z = ''
    y = 0.0


if __name__ == '__main__':
    try:
        testStruct = Struct

        link = txfer.SerialTransfer('/dev/ttyACM1')

        link.open()
        time.sleep(2)  # allow some time for the Arduino to completely reset

        while True:
            send_size = 0

            while not link.available():
                # A negative value for status indicates an error
                if link.status < 0:
                    if link.status == txfer.Status.CRC_ERROR:
                        print('ERROR: CRC_ERROR')
                    elif link.status == txfer.Status.PAYLOAD_ERROR:
                        print('ERROR: PAYLOAD_ERROR')
                    elif link.status == txfer.Status.STOP_BYTE_ERROR:
                        print('ERROR: STOP_BYTE_ERROR')
                    else:
                        print('ERROR: {}'.format(link.status.name))

            ###################################################################
            # Parse response data
            ###################################################################
            recSize = 0

            testStruct.z = link.rx_obj(obj_type='c', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['c']

            testStruct.y = link.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']

            ###################################################################
            # Display the received data
            ###################################################################
            print('{} {}'.format(testStruct.z, testStruct.y))


    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass

    except:
        import traceback

        traceback.print_exc()

        try:
            link.close()
        except:
            pass