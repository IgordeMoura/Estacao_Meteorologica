from main import app
from flask import render_template, jsonify
from datetime import datetime
from services.connect import consulta_banco

# ---------- Configurações simples (ajuste como quiser) ----------
LOCAL = "Sua Localização"
LIMITE_GAS_ALERTA = 300   # ppm: a partir daqui o alerta fica amarelo
LIMITE_GAS_PERIGO = 600   # ppm: a partir daqui o alerta fica vermelho


# ---------- Funções auxiliares ----------
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
    if gas >= LIMITE_GAS_PERIGO:
        return "danger", f"PERIGO: gás/fumaça detectado ({gas:.0f} ppm)"
    if gas >= LIMITE_GAS_ALERTA:
        return "warn", f"Atenção: nível elevado de gás/fumaça ({gas:.0f} ppm)"
    return "ok", f"Gás / Fumaça: normal ({gas:.0f} ppm)"

def pegar_ordem(registro):
    try:
        return datetime.strptime(registro.get("ordem"), "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return datetime.min

def tema_pela_luz(luz):
    if luz is None:
        return ""
    if str(luz).upper() == "CLARO":
        return "light"
    if str(luz).upper() == "ESCURO":
        return "dark"
    return ""


def obter_dados():
    registros = []

    dados_consulta = consulta_banco()

    if not isinstance(dados_consulta, dict):
        return {}, []

    for chave, registro in dados_consulta.items():

        if not isinstance(registro, dict):
            continue

        try:
            data = datetime.strptime(registro.get("ordem"), "%Y-%m-%d %H:%M:%S")
            registro_copia = registro.copy()
            registro_copia["_data_ordem"] = data
            registros.append(registro_copia)

        except (TypeError, ValueError):
            continue

    registros.sort(key=lambda r: r["_data_ordem"], reverse=True)

    if not registros:
        return {}, []

    atual = registros[0]
    ultimos = registros[1:3]
    atual.pop("_data_ordem", None)

    for registro in ultimos:
        registro.pop("_data_ordem", None)
    return atual, ultimos

def montar_dados():
    """Monta um dicionário com tudo já formatado, pronto para o HTML e para o JS."""
    atual, ultimos = obter_dados()

    emoji, descricao = icone_temperatura(atual.get("temperatura"))
    alerta_status, alerta_texto = status_gas(atual.get("gas"))

    linhas = []
    for registro in ultimos[:2]:
        linhas.append({
            "temperatura": formatar(registro.get("temperatura"), 1, "°C"),
            "pressao": formatar(registro.get("pressao"), 0, " hPa"),
            "umidade": formatar(registro.get("umidade"), 0, "%"),
        })
    # o protótipo sempre mostra 2 linhas; completa com '--' se faltar registro
    while len(linhas) < 2:
        linhas.append({"temperatura": "--", "pressao": "--", "umidade": "--"})

    return {
        "local": LOCAL,
        "temperatura": formatar(atual.get("temperatura"), 1, "°C"),
        "pressao": formatar(atual.get("pressao"), 0, " hPa"),
        "umidade": formatar(atual.get("umidade"), 0, "%"),
        "luz": formatar(atual.get("luz"), 0, " lx"),
        "tema": tema_pela_luz(atual.get("luz")),
        "icone": emoji,
        "descricao": descricao,
        "alerta_status": alerta_status,
        "alerta_texto": alerta_texto,
        "ultimos": linhas,
    }


# ---------- Rotas ----------
@app.route("/")
def pagina_home():
    hora = datetime.now().strftime("%H:%M")
    return render_template("index.html", d=montar_dados(), hora=hora)


@app.route("/api/dados")
def api_dados():
    # O JavaScript chama esta rota a cada 10 s para atualizar a tela sem recarregar
    return jsonify(montar_dados())
