from main import app
from flask import render_template, jsonify
from services.connect import consulta_banco

LOCAL = "Sua Localização"
LIMITE_GAS_ALERTA = 300
LIMITE_GAS_PERIGO = 600


def para_numero(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None


def formatar(valor, casas, unidade):
    if valor is None:
        return "--"

    numero = para_numero(valor)
    if numero is None:
        return str(valor).capitalize()

    if casas == 0:
        return str(int(round(numero))) + unidade
    return str(round(numero, casas)) + unidade


def icone_temperatura(temperatura):
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
    gas = para_numero(gas)

    if gas is None:
        return "ok", "Gás / Fumaça: sem dados"
    if gas >= LIMITE_GAS_PERIGO:
        return "danger", f"PERIGO: gás/fumaça detectado ({gas:.0f} ppm)"
    if gas >= LIMITE_GAS_ALERTA:
        return "warn", f"Atenção: nível elevado de gás/fumaça ({gas:.0f} ppm)"
    return "ok", f"Gás / Fumaça: normal ({gas:.0f} ppm)"


def pegar_ordem(registro):
    return registro["ordem"]


def obter_dados():
    registros = []

    dados_consulta = consulta_banco()
    if dados_consulta:
        for chave in dados_consulta:
            registro = dados_consulta[chave]
            if isinstance(registro, dict) and isinstance(registro.get("ordem"), str):
                registros.append(registro)

    registros.sort(key=pegar_ordem, reverse=True)

    if len(registros) == 0:
        return {}, []

    atual = registros[0]
    ultimos = registros[1:3]
    return atual, ultimos


def montar_dados():
    atual, ultimos = obter_dados()

    emoji, descricao = icone_temperatura(atual.get("temperatura"))
    alerta_status, alerta_texto = status_gas(atual.get("gas"))

    linhas = []
    for registro in ultimos:
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
    return render_template("index.html", d=montar_dados())


@app.route("/api/dados")
def api_dados():
    return jsonify(montar_dados())
