from queue import SimpleQueue
import time

from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout

from enum import IntEnum

from kivymd.uix.menu import MDDropdownMenu

import Gamepad
import MarlinController


import MarlinGcode
from MarlinController import CmdData

MAX_AXIS_VALUE = 32767
STEPS_PER_MOVEMENT = 2
DEAD_ZONE = 32767*0.1
Z_MOVE_STEPS = 5


class PCC(FloatLayout):
    _controllers = ListProperty([""])
    _ports = ListProperty([])
    _x = NumericProperty(0.0)
    _y = NumericProperty(0.0)
    _z = NumericProperty(0.0)
    _bedX = NumericProperty(235)
    _bedY = NumericProperty(235)
    _printZ = NumericProperty(300)
    _heater_icon = StringProperty('fire')
    _heater_color = StringProperty('black')

    def __init__(self):
        FloatLayout.__init__(self)
        self._gamepad = None
        self._controller = None
        self._control_dropdown = None
        self._serial_dropdown = None
        self._connect_button = None
        self._connected = False
        self._controller_queue = SimpleQueue()  # items = dict {type, data}
        self._menu = None

    def start(self):
        self._controller = MarlinController.MarlinController(self._controller_queue)
        self._controller.setDaemon(True)
        self._controller.start()

        self._serial_dropdown = self.ids.SerialPortDropdown
        self._ports = [
            {
                "viewclass": "OneLineListItem",
                "text": item,
                "on_release": lambda x=item: self.set_item(x),
            } for item in self._controller.get_ports()
        ]
        self._menu = MDDropdownMenu(
            caller=self.ids.SerialPortDropdown,
            items=self._ports,
            width_mult=4,
            position="center",
        )

        self._connect_button = self.ids.ConnectButton
        self._connect_button.bind(on_release=self.toggle_connect)

        Window.bind(on_joy_button_down=self.on_controller_btn_input_down)
        Window.bind(on_joy_button_up=self.on_controller_btn_input_up)
        Window.bind(on_joy_axis=self.on_controller_axis_input)
        Window.bind(on_joy_hat=self.on_controller_hat_input)

    def set_item(self, text_item):
        self.ids.SerialPortDropdown.set_item(text_item)
        self._menu.dismiss()
        self.select_port(text_item)

    def select_port(self, port_name):
        print('on_select_port called')
        self._controller.set_port(port_name)

    def on_select_controller(self, obj=None, value=''):
        for i in range(0, len(obj.values)):
            if value in obj.values[i]:
                self._gamepad.set_gamepad(i)
                self._gamepad.start()

    def toggle_connect(self, obj='', value=None):
        state = value

        if value is None:
            state = self._connect_button.text

        cmd = CmdData(CmdData.CmdType.System, {'cmd': self._connect_button.text})
        self._controller_queue.put(cmd)

    def set_connect_status(self, connected):
        self._connected = connected
        self._serial_dropdown.disabled = connected

        self._x = 0
        self._y = 0
        self._z = 0

        if connected:
            self._connect_button.text = "Disconnect"
        else:
            self._connect_button.text = "Connect"

    def update(self, dt):
        connected = self._controller.is_connected()

        if self._connected != connected:
            self.set_connect_status(connected)

    def stop(self):
        self.disable_steppers()
        time.sleep(0.5)
        self.toggle_connect("disconnect")

    def on_controller_btn_input_down(self, win, stickid, buttonid):
        pass

    def on_controller_btn_input_up(self, win, stickid, buttonid):
        cmd_data = None
        if buttonid == Gamepad.Button.A.value:
            pass
        elif buttonid == Gamepad.Button.B.value:
            pass
        elif buttonid == Gamepad.Button.X.value:
            pass
        elif buttonid == Gamepad.Button.Y.value:
            cmd_data = MarlinGcode.cmd_auto_home()

            self._x = 0
            self._y = 0
            self._z = 0

        elif buttonid == Gamepad.Button.start.value:
            pass
        elif buttonid == Gamepad.Button.select.value:
            pass
        elif buttonid == Gamepad.Button.TR.value:
            new_z = self._z - Z_MOVE_STEPS

            if 0 <= new_z <= self._printZ:
                self._z = new_z
                cmd_data = MarlinGcode.cmd_linear_move(z=-Z_MOVE_STEPS)

        elif buttonid == Gamepad.Button.TL.value:
            new_z = self._z + Z_MOVE_STEPS

            if 0 <= new_z <= self._printZ:
                self._z = new_z
                cmd_data = MarlinGcode.cmd_linear_move(z=Z_MOVE_STEPS)
        elif buttonid == Gamepad.Button.thumbL.value:
            pass
        elif buttonid == Gamepad.Button.thumbR.value:
            pass

        if cmd_data is not None:
            cmd = CmdData(CmdData.CmdType.Gcode, {'cmd': cmd_data})
            self.send(cmd)

    def on_controller_axis_input(self, win, stickid, axisid, value):
        x_move = None
        y_move = None

        if abs(value) > DEAD_ZONE:
            if axisid == 0:  # left stick
                x_move = round(value / MAX_AXIS_VALUE * STEPS_PER_MOVEMENT, 2)
                new_x = self._x + x_move

                if 0 <= new_x <= self._bedX:
                    self._x += x_move
                else:
                    x_move = None

            elif axisid == 1:  # left stick
                y_move = -1 * round(value / MAX_AXIS_VALUE * STEPS_PER_MOVEMENT, 2)
                new_y = self._y + y_move

                if 0 <= new_y <= self._bedY:
                    self._y += y_move
                else:
                    y_move = None

            if axisid < 2:
                self.send_move(x_move, y_move)

    def on_controller_hat_input(self, win, hatid, axisid, values):
        if hatid == 0:
            x_move, y_move = values

            if x_move != 0 or y_move != 0:
                steps = float(self.ids.DPadStep.value)
                x_move *= steps
                y_move *= steps

                new_x = self._x + x_move
                new_y = self._y + y_move

                if 0 <= new_x <= self._bedX:
                    self._x += x_move
                else:
                    x_move = None

                if 0 <= new_y <= self._bedY:
                    self._y += y_move
                else:
                    y_move = None

                self.send_move(x_move, y_move)

    def send_move(self, x, y):
        cmd = CmdData(CmdData.CmdType.Gcode, {'cmd': MarlinGcode.cmd_set_rel_positioning()})
        self.send(cmd)

        cmd2 = CmdData(CmdData.CmdType.Gcode, {'cmd': MarlinGcode.cmd_linear_move(x=x, y=y)})
        self.send(cmd2)

    def on_emergency_stop_pressed(self, obj=None):
        cmd = CmdData(CmdData.CmdType.Gcode, {'cmd': MarlinGcode.cmd_emergency_stop()})
        self.send(cmd)

    def on_heat_pressed(self, obj=None):
        tmp = self.ids.ExtruderTemp.input
        cmd_hotend = CmdData(CmdData.CmdType.Gcode, {
            'cmd': MarlinGcode.cmd_set_hotend_temp(temp=int(tmp))
        })
        cmd_bed = CmdData(CmdData.CmdType.Gcode, {
            'cmd': MarlinGcode.cmd_set_bed_temp(temp=int(self.ids.BedTemp.input))
        })

        self.send(cmd_hotend)
        self.send(cmd_bed)

    def disable_steppers(self):
        cmd = CmdData(CmdData.CmdType.Gcode, {'cmd': MarlinGcode.cmd_disable_steppers()})
        self.send(cmd)

    def send(self, cmd):
        self._controller_queue.put(cmd)
