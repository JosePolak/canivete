import locale

import requests
from flask import Blueprint, render_template, request

from extensions import db
from models import Historico

bp_moedas = Blueprint("moedas", __name__)

# Configuração de locale para formatação brasileira
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except Exception:
    locale.setlocale(locale.LC_ALL, "")

SIMBOLOS = {
    "USD": "U$",
    "EUR": "€",
    "GBP": "£",
    "BTC": "₿",
    "ARS": "$",
    "CAD": "C$",
    "JPY": "¥",
    "CHF": "Fr",
    "BRL": "R$",
}


def buscar_dados_api():
    moedas_busca = "USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL,ARS-BRL,CAD-BRL,JPY-BRL,CHF-BRL"
    url = f"https://economia.awesomeapi.com.br/last/{moedas_busca}"
    try:
        dados = requests.get(url).json()
    except Exception:
        return [], []  # Evita que o app quebre se a API cair

    lista_topo = []
    lista_completa = []

    for _, info in dados.items():
        valor_venda = float(info["bid"])
        valor_formatado = locale.format_string("%.2f", valor_venda, grouping=True)

        moeda_obj = {
            "nome": info["name"].split("/")[0],
            "valor": valor_formatado,
            "valor_num": valor_venda,
            "codigo": info["code"],
        }
        lista_completa.append(moeda_obj)
        if info["code"] in ["USD", "EUR", "BTC"]:
            lista_topo.append(moeda_obj)

    return lista_topo, sorted(lista_completa, key=lambda x: x["nome"])


@bp_moedas.route("/")
def home():
    topo, todas = buscar_dados_api()
    historico = Historico.query.order_by(Historico.data_hora.desc()).limit(10).all()
    return render_template(
        "cotador.html", moedas_topo=topo, moedas_todas=todas, historico=historico
    )


@bp_moedas.route("/converter", methods=["POST"])
def converter():
    origem_raw = request.form.get("moeda_origem", "1.0|Real|BRL")
    v_origem, n_origem, c_origem = origem_raw.split("|")
    v_origem = float(v_origem)

    destino_raw = request.form.get("moeda_destino", "1.0|Real|BRL")
    v_destino, n_destino, c_destino = destino_raw.split("|")
    v_destino = float(v_destino)

    try:
        valor_raw = request.form.get("valor", "0")
        valor_input = float(valor_raw) if valor_raw.strip() else 0.0
    except ValueError:
        valor_input = 0.0

    valor_em_reais = valor_input * v_origem
    resultado_num = valor_em_reais / v_destino

    s_origem = SIMBOLOS.get(c_origem, "$")
    s_destino = SIMBOLOS.get(c_destino, "$")

    fmt_in = "%.8f" if c_origem == "BTC" else "%.2f"
    fmt_out = "%.8f" if c_destino == "BTC" else "%.2f"

    val_in_fmt = locale.format_string(fmt_in, valor_input, grouping=True)
    res_out_fmt = locale.format_string(fmt_out, resultado_num, grouping=True)

    msg = f"{s_origem} {val_in_fmt} ({n_origem}) equivalem a {s_destino} {res_out_fmt} ({n_destino})."

    # Persistência no banco
    nova_consulta = Historico(
        moeda_origem=n_origem,
        moeda_destino=n_destino,
        valor_entrada=valor_input,
        valor_saida=resultado_num,
    )
    db.session.add(nova_consulta)
    db.session.commit()

    topo, todas = buscar_dados_api()
    # BUSCA O HISTÓRICO NOVAMENTE PARA O TEMPLATE NÃO FICAR VAZIO
    historico = Historico.query.order_by(Historico.data_hora.desc()).limit(10).all()

    if c_origem == "BTC":
        valor_para_input = "{:.8f}".format(valor_input)
    else:
        valor_para_input = "{:.2f}".format(valor_input)

    return render_template(
        "cotador.html",
        moedas_topo=topo,
        moedas_todas=todas,
        historico=historico,  # Enviando o histórico atualizado
        resultado=True,
        mensagem_resultado=msg,
        valor_post=valor_para_input,
        moeda_origem_post=c_origem,
        moeda_destino_post=c_destino,
    )
