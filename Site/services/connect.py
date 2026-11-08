from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import json

link = 'https://estacaometeorologica-69028-default-rtdb.firebaseio.com/'
FUSO = ZoneInfo("America/Sao_Paulo")


def registro_banco(temperatura, pressao, umidade, luz, gas):
    dados = {
        "ordem": datetime.now(FUSO).strftime("%Y-%m-%d %H:%M:%S"),
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
