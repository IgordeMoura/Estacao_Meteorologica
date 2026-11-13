from main import app
from flask import render_template, jsonify
from datetime import datetime
from services.connect import consulta_banco

LOCAL = "Sua Localização"
LIMITE_GAS_ALERTA = 2000   
LIMITE_GAS_PERIGO = 4000   

def para_numero(valor):
    """Tenta converter para número. Se não der (ex.: 'ESCURO'), devolve None."""
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None

def formatar(valor, casas=0, unidade=""):
    """
    Transforma o valor em texto para a tela.
    - sem dado            -> '--'
    - número              -> '24.5°C', '1013 hPa'...
    - texto (ex.: 'ESCURO') -> 'Escuro' (aparece como está, sem unidade)
    """
    if valor is None:
        return "--"
    numero = para_numero(valor)
    if numero is None:
        return str(valor).capitalize()
    return f"{numero:.{casas}f}{unidade}"


def icone_temperatura(temperatura):
    """Escolhe o emoji e a descrição de acordo com a temperatura."""
    temperatura = para_numero(temperatura)
    if temperatura is None:
        return "🌡️", "Sem dados"
    if temperatura <= 10:
        return "🥶", "Frio"
    if temperatura <= 18:
        return "🌥️", "Fresco"
    if temperatura <= 27:
        return "🌤️", "Agradável"
    if temperatura <= 32:
        return "☀️", "Quente"
    return "🔥", "Muito quente"

def status_gas(gas):
    """Devolve o status do alerta ('ok', 'warn' ou 'danger') e o texto a mostrar."""
    gas = para_numero(gas)
    if gas is None:
        return "ok", "Gás / Fumaça: sem dados"
    leitura = f"{gas:.0f}"
    if gas >= LIMITE_GAS_PERIGO:
        return "danger", f"PERIGO: gás/fumaça detectado ({leitura})"
    if gas >= LIMITE_GAS_ALERTA:
        return "warn", f"Atenção: nível elevado de gás/fumaça ({leitura})"
    return "ok", f"Gás / Fumaça: normal ({leitura})"

def obter_dados():
    """
    Consulta o banco A CADA CHAMADA (assim os dados nunca ficam velhos)
    e separa o registro atual (ordem 1) dos dois anteriores (ordem 2 e 3).
    """
    atual = {}
    ultimos = []

    dados_consulta = consulta_banco()
    if dados_consulta:
        registros = []
        for id, registro in dados_consulta.items():
            ordem = registro.get("ordem")
            if ordem:
                data = datetime.strptime(ordem, "%Y-%m-%d %H:%M:%S")
                registros.append((data, registro))
        registros.sort(key=lambda x: x[0], reverse=True)
        atual = registros[0][1] if registros else {}
        ultimos = [registro for _, registro in registros[1:4]]

    ultimos.sort(key=lambda r: r["ordem"])  
    return atual, ultimos

def montar_dados():
    """Monta um dicionário com tudo já formatado, pronto para o HTML e para o JS."""
    atual, ultimos = obter_dados()

    alerta_status, alerta_texto = status_gas(atual.get("gas"))
    emoji, descricao = icone_temperatura(atual.get("temperatura"))

    linhas = []
    for registro in ultimos[:2]:
        linhas.append({
            "temperatura": formatar(registro.get("temperatura"), 1, "°C"),
            "pressao": formatar(registro.get("pressao"), 0, " hPa"),
            "umidade": formatar(registro.get("umidade"), 0, "%"),
        })
    
    while len(linhas) < 2:
        linhas.append({"temperatura": "--", "pressao": "--", "umidade": "--"})

    return {
        "local": LOCAL,
        "temperatura": formatar(atual.get("temperatura"), 1, "°C"),
        "pressao": formatar(atual.get("pressao"), 0, " hPa"),
        "umidade": formatar(atual.get("umidade"), 0, "%"),
        "luz": formatar(atual.get("luz"), 0, " lx"),
        "icone": emoji,
        "descricao": descricao,
        "alerta_status": alerta_status,
        "alerta_texto": alerta_texto,
        "ultimos": linhas,
    }

@app.route("/")
def pagina_home():
    hora = datetime.now().strftime("%H:%M")
    return render_template("index.html", d=montar_dados(), hora=hora)


@app.route("/api/dados")
def api_dados():
    
    return jsonify(montar_dados())