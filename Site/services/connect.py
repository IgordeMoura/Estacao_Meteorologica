import requests
import json

link = 'https://estacaometeorologica-69028-default-rtdb.firebaseio.com/'

def atualizar_banco(id, dados):
    requisicao = requests.patch(f'{link}/Registros/{id}.json', data=json.dumps(dados))

def registro_banco(temperatura, pressao, umidade, luz, gas):
    contagem = 1
    dados = {
    "ordem": contagem,
    "temperatura": temperatura,        
    "pressao": pressao,            
    "umidade": umidade,              
    "luz": luz,                 
    "gas": gas   
    }

    dados_banco = consulta_banco()

    for id, registros in dados_banco.items():
        atualizar_banco(id, {'ordem':int(registros.get('ordem'))+contagem})

    requisicao = requests.post(f'{link}/Registros/.json', data=json.dumps(dados))


def consulta_banco():
    requisicao = requests.get(f'{link}/Registros/.json')
    return  requisicao.json()

# consulta_banco()