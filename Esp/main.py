from machine import Pin, ADC, I2C
import dht
import time
from bmp280 import BMP280
import network

def conexao_wifi():
    rede = 'aluno1234'
    senha = '4321onula'
    sessao = network.WLAN(network.STA_IF)
    sessao.active(True)
    sessao.connect(rede, senha)
    while not sessao.isconnected():
        time.sleep(0.5)

INTERVALO_S = 15
FATOR_DIVISOR = 2
LDR_DO_ALTO_E_ESCURO = True

sensor_dht = dht.DHT22(Pin(18))
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
pino_ldr = Pin(35, Pin.IN)
adc_gas = ADC(Pin(34))
adc_gas.atten(ADC.ATTN_11DB)
bmp = BMP280(i2c)

def ler_dht():
    try:
        sensor_dht.measure()
        return sensor_dht.temperature(), sensor_dht.humidity()
    except OSError:
        return None, None

def ler_bmp():
    try:
        return bmp.medir()
    except OSError:
        return None, None

def ler_luz():
    escuro = (pino_ldr.value() == 1) == LDR_DO_ALTO_E_ESCURO
    return "ESCURO" if escuro else "CLARO"

def ler_gas():
    soma = 0
    for _ in range(16):
        soma += adc_gas.read_u16()
        time.sleep_ms(5)
    bruto = soma // 16
    v_esp = bruto * 3.3 / 65535
    v_sensor = v_esp * FATOR_DIVISOR
    return bruto, round(v_sensor, 2)

from connect import registro_banco
print("Estacao meteorologica iniciada. Intervalo:", INTERVALO_S, "s")
n = 0
conexao_wifi()
while True:
    n += 1
    temp_dht, umid = ler_dht()
    temp_bmp, pressao = ler_bmp()
    luz = ler_luz()
    gas_bruto, gas_v = ler_gas()

    registro_banco(temp_bmp, pressao, umid, luz, gas_bruto)

    print("---- Leitura", n, "----")
    print("DHT22  | temperatura:", temp_dht, "C | umidade:", umid, "%")
    if pressao is None:
        print("BMP280 | falha na leitura")
    else:
        print("BMP280 | temperatura:", round(temp_bmp, 1), "C | pressao:", round(pressao, 1), "hPa")
    print("LDR    | ambiente:", luz)
    print("MQ-135 | bruto:", gas_bruto, "| tensao no sensor:", gas_v, "V")

    time.sleep(INTERVALO_S)