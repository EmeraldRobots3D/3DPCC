import queue
import time
from threading import Thread
import serial
import serial.tools.list_ports
from enum import Enum
import MarlinGcode

time_out = 1.0
foo = b'Basement'


class CmdData:
    """ Data to send to the controller board """
    class CmdType(Enum):
        """ Enum for the type of command to send to the controller board """
        System = 0
        Gcode = 1

    def __init__(self, cmd_type, cmd_data: dict = {}):
        self.cmd_type = cmd_type
        self.cmd_data = cmd_data


class MarlinController(Thread):
    """ CLass for interacting with a Marlin-based 3D printer controller """
    def __init__(self, cmd_queue):
        Thread.__init__(self)
        self._port_name = ''
        self._ser = None
        self._baud = 115200
        self._cmd_queue = cmd_queue

        ports = serial.tools.list_ports.comports(True)
        self._port_names = [port.device for port in ports]
        self.get_ports()

    def run(self):
        while self.is_alive():
            # check queue for command
            try:
                while not self._cmd_queue.empty():
                    item = self._cmd_queue.get_nowait()

                    if item.cmd_type == CmdData.CmdType.System:
                        cmd = item.cmd_data['cmd']

                        if cmd == 'Connect':
                            auto_detect = True
                            if 'args' in item.cmd_data.keys():
                                auto_detect = item.cmd_data['args']['auto_detect']

                            self.connect(auto_detect)
                        elif cmd == 'Disconnect':
                            self.cleanup()
                    elif item.cmd_type == CmdData.CmdType.Gcode:
                        cmd = item.cmd_data['cmd']
                        self.send_cmd(cmd)

            except queue.Empty:
                pass

    def is_connected(self):
        return self._ser is not None and self._ser.is_open

    def get_ports(self):
        return self._port_names

    def set_port(self, port: str = ''):
        if port is not None and len(port) != 0:
            print(f'Setting port: {port}')
            self._port_name = port

    def _auto_detect_baud(self):
        baud_rates = list(serial.Serial.BAUDRATES)
        baud_rates.append(2500000)
        baud_rates = baud_rates[::-1]

        for baud in baud_rates:
            self._ser = serial.Serial(self._port_name, baud, timeout=time_out)
            print(f'Testing baud: {baud}')
            # with serial.Serial(self._port_name, baud, timeout=0) as ser:
            self._ser.write(bytes(MarlinGcode.cmd_test() + '\n', 'utf-8'))
            time.sleep(1)

            buffer = self._ser.readline()

            print(buffer)

            if b'start' in buffer or b'ok' in buffer:
                print('Correct baud')
                self._baud = baud
                return True

        return False

    def connect(self, auto_detect=True):
        print('Opening port: ' + self._port_name)
        connected = False
        try:
            if auto_detect:
                self._auto_detect_baud()
            else:
                self._ser = serial.Serial(self._port_name, self._baud, timeout=time_out)
        except serial.SerialException:
            print('Error Connecting to port')
            return False

        return True

    def send_cmd(self, cmd: str):
        if len(cmd) > 0 and self.is_connected():
            cmd += '\n'
            self._ser.write(bytes(cmd, 'utf-8'))

            buffer = ''

            read = b''
            while b'ok' not in read:
                try:
                    read = self._ser.read_until(bytes('\n', 'utf-8'))
                except serial.SerialTimeoutException:
                    pass

                if len(read) > 0:
                    buffer += bytes.decode(read, 'utf-8')

            return buffer

    def cleanup(self):
        if self._ser is not None and self._ser.is_open:
            self._ser.close()
            self._ser = None


if __name__ == '__main__':

    controller = MarlinController()
    controller.set_port('COM7')

    if controller.connect():
        data = controller.send_cmd(MarlinGcode.cmd_read_eeprom())
        print(data)

    controller.cleanup()
