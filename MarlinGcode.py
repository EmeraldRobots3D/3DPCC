# Marlin G-code commands from: https://marlinfw.org/meta/gcode/


def cmd_set_bed_temp(temp=0):
    return f'M140 S{temp}'


def cmd_set_hotend_temp(temp=0, index=None):
    cmd = f'M104 S{temp} '

    if index is not None:
        cmd += f'T{index}'

    return cmd


def cmd_set_rel_positioning():
    return 'G91'


def cmd_set_abs_positioning():
    return 'G90'


def cmd_set_position(x=None, y=None, z=None, extruder=None):
    cmd = 'G92'

    if x is not None:
        cmd += f' X{x}'
    if y is not None:
        cmd += f' Y{y}'
    if z is not None:
        cmd += f' Z{z}'
    if extruder is not None:
        cmd += f' E{extruder}'

    return cmd


def cmd_linear_move(x=None, y=None, z=None, extruder=None, feed_rate=None):
    cmd = 'G1'

    if x is not None:
        cmd += f' X{x}'
    if y is not None:
        cmd += f' Y{y}'
    if z is not None:
        cmd += f' Z{z}'
    if extruder is not None:
        cmd += f' E{extruder}'
    if feed_rate is not None:
        cmd += f' F{feed_rate}'

    return cmd


def cmd_auto_home(x=None, y=None, z=None):
    cmd = 'G28'

    if x is not None:
        cmd += f' X{x}'
    if y is not None:
        cmd += f' Y{y}'
    if z is not None:
        cmd += f' Z{z}'

    return cmd


def cmd_emergency_stop():
    return 'M112'


def cmd_read_eeprom():
    return 'M503'


# Taken from simply3D's test method
def cmd_test():
    return 'T0'


def cmd_disable_steppers():
    return 'M18'
