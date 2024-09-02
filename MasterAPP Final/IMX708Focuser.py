import time
import os


class Focuser:
    bus = None
    CHIP_I2C_ADDR = 0x0C

    def __init__(self, bus=6):
        self.focus_value = 0
        self.bus = bus
        
    def read(self):
        return self.focus_value

    def write(self, chip_addr, value):
        if value < 0:
            value = 0
        self.focus_value = value

        value = value & 0x03FF
        data1 = value >> 8
        data2 = value & 0xFF
        os.system("i2cset -y {} 0x{:02X} 0x03 {}".format(self.bus, chip_addr, data1))
        os.system("i2cset -y {} 0x{:02X} 0x04 {}".format(self.bus, chip_addr, data2))


    OPT_BASE    = 0x1000
    OPT_FOCUS   = OPT_BASE | 0x01
    OPT_ZOOM    = OPT_BASE | 0x02
    OPT_MOTOR_X = OPT_BASE | 0x03
    OPT_MOTOR_Y = OPT_BASE | 0x04
    OPT_IRCUT   = OPT_BASE | 0x05
    opts = {
        OPT_FOCUS : {
            "MIN_VALUE": 0,
            "MAX_VALUE": 1023,
            "DEF_VALUE": 439,
        },
    }
    def reset(self,opt,flag = 1):
        info = self.opts[opt]
        if info == None or info["DEF_VALUE"] == None:
            return
        self.set(opt,info["DEF_VALUE"])

    def get(self,opt,flag = 0):
        info = self.opts[opt]
        return self.read()

    def set(self,opt,value,flag = 1):
        info = self.opts[opt]
        if value > info["MAX_VALUE"]:
            value = info["MAX_VALUE"]
        elif value < info["MIN_VALUE"]:
            value = info["MIN_VALUE"]
        self.write(self.CHIP_I2C_ADDR, value)
        print("write: {}".format(value))



if __name__ == "__main__":

    focuser = Focuser(6)
    focuser.reset(Focuser.OPT_FOCUS)

    for i in range(439,-1,-1):
        focuser.set(Focuser.OPT_FOCUS, i)
        time.sleep(0.001)

    for i in range(0,1023+1):
        focuser.set(Focuser.OPT_FOCUS, i)
        time.sleep(0.001)