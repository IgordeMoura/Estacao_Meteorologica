import struct
import time

class BMP280:
    REG_ID = 0xD0
    REG_RESET = 0xE0
    REG_CTRL_MEAS = 0xF4
    REG_DADOS = 0xF7
    REG_CALIB = 0x88

    def __init__(self, i2c, endereco=None):
        self.i2c = i2c

        if endereco is None:
            encontrados = i2c.scan()
            endereco = next((e for e in (0x76, 0x77) if e in encontrados), None)

        if endereco is None:
            raise OSError("BMP280 nao encontrado no I2C")

        self.endereco = endereco

        self.chip_id = i2c.readfrom_mem(endereco, self.REG_ID, 1)[0]

        if self.chip_id != 0x58:
            raise OSError("BMP280: Chip ID inesperado: " + hex(self.chip_id))
        
        i2c.writeto_mem(endereco, self.REG_RESET, b"\xB6")
        time.sleep_ms(10)
        
        c = i2c.readfrom_mem(endereco, self.REG_CALIB, 24)

        (
            self.t1, self.t2, self.t3,
            self.p1, self.p2, self.p3, self.p4,
            self.p5, self.p6, self.p7, self.p8, self.p9
        ) = struct.unpack("<HhhHhhhhhhhh", c)

    def _compensar(self, adc_t, adc_p):

        v1 = (((adc_t >> 3) - (self.t1 << 1)) * self.t2) >> 11
        v2 = ((((adc_t >> 4) - self.t1) * ((adc_t >> 4) - self.t1) >> 12) * self.t3) >> 14
        t_fine = v1 + v2
        temperatura = ((t_fine * 5 + 128) >> 8) / 100
        v1 = t_fine - 128000
        v2 = v1 * v1 * self.p6
        v2 += (v1 * self.p5) << 17
        v2 += self.p4 << 35
        v1 = ((v1 * v1 * self.p3) >> 8) + ((v1 * self.p2) << 12)
        v1 = (((1 << 47) + v1) * self.p1) >> 33

        if v1 == 0:
            return temperatura, None

        p = 1048576 - adc_p
        p = (((p << 31) - v2) * 3125) // v1
        v1 = (self.p9 * (p >> 13) * (p >> 13)) >> 25
        v2 = (self.p8 * p) >> 19
        p = ((p + v1 + v2) >> 8) + (self.p7 << 4)
        pressao = p / 25600

        return temperatura, pressao

    def medir(self):    
        self.i2c.writeto_mem(self.endereco, self.REG_CTRL_MEAS, b"\x25")
        time.sleep_ms(15)
      
        d = self.i2c.readfrom_mem(self.endereco, self.REG_DADOS, 6)
        adc_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        adc_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)

        return self._compensar(adc_t, adc_p)