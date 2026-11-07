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


def obter_dados():
    """
    Consulta o banco A CADA CHAMADA (assim os dados nunca ficam velhos)
    e separa o registro atual (ordem 1) dos dois anteriores (ordem 2 e 3).
    """
    atual = {}
    ultimos = []

    dados_consulta = consulta_banco()
    if dados_consulta:
        for id, registro in dados_consulta.items():
            ordem = registro.get("ordem")
            if ordem == 1:
                atual = registro
            elif ordem is not None and ordem <= 3:
                ultimos.append(registro)

    ultimos.sort(key=lambda r: r["ordem"])  # 2 antes do 3
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
