import requests
import json
import ntptime
import time
import network

def conexao_wifi():
    rede = 'aluno1234'
    senha = '4321onula'
    sessao = network.WLAN(network.STA_IF)
    sessao.active(True)
    sessao.connect(rede, senha)
    while not sessao.isconnected():
        time.sleep(0.5)

conexao_wifi()

link = 'https://estacaometeorologica-69028-default-rtdb.firebaseio.com/'

ntptime.settime()
def hora_brasilia():
    t = time.localtime(time.time() - 3 * 3600)
    return "%04d-%02d-%02d %02d:%02d:%02d" % t[0:6]

def registro_banco(temperatura, pressao, umidade, luz, gas):
    dados = {
        "ordem": hora_brasilia(),
        "temperatura": temperatura,
        "pressao": pressao,
        "umidade": umidade,
        "luz": luz,
        "gas": gas
    }

    requests.post(f'{link}/Registros/.json', data=json.dumps(dados), timeout=10)

def consulta_banco():
    parametros = {"orderBy": '"$key"', "limitToLast": 3}

    try:
        requisicao = requests.get(f'{link}/Registros/.json', params=parametros, timeout=10)
    except requests.exceptions.RequestException:
        return None

    if requisicao.status_code != 200:
        return None

    return requisicao.json()