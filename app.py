import locale

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

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

try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except Exception:
    locale.setlocale(locale.LC_ALL, "")


def buscar_dados_api():
    moedas_busca = "USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL,ARS-BRL,CAD-BRL,JPY-BRL,CHF-BRL"
    url = f"https://economia.awesomeapi.com.br/last/{moedas_busca}"
    dados = requests.get(url).json()

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


@app.route("/")
def home():
    topo, todas = buscar_dados_api()
    return render_template("cotador.html", moedas_topo=topo, moedas_todas=todas)


@app.route("/converter", methods=["POST"])
def converter():
    # 1. Captura Moeda de Origem
    origem_raw = request.form.get("moeda_origem", "1.0|Real|BRL")
    v_origem, n_origem, c_origem = origem_raw.split("|")
    v_origem = float(v_origem)

    # 2. Captura Moeda de Destino
    destino_raw = request.form.get("moeda_destino", "1.0|Real|BRL")
    v_destino, n_destino, c_destino = destino_raw.split("|")
    v_destino = float(v_destino)

    # 3. Captura Valor
    try:
        valor_raw = request.form.get("valor", "0")
        valor_input = float(valor_raw) if valor_raw.strip() else 0.0
    except ValueError:
        valor_input = 0.0

    # 4. Lógica de Conversão (Arbitragem via Real)
    # Primeiro: converte o valor de entrada para Reais
    valor_em_reais = valor_input * v_origem
    # Segundo: converte de Reais para a moeda de destino
    resultado_num = valor_em_reais / v_destino

    # 5. Formatação de Símbolos e Mensagem
    s_origem = SIMBOLOS.get(c_origem, "$")
    s_destino = SIMBOLOS.get(c_destino, "$")

    fmt_in = "%.8f" if c_origem == "BTC" else "%.2f"
    fmt_out = "%.8f" if c_destino == "BTC" else "%.2f"

    val_in_fmt = locale.format_string(fmt_in, valor_input, grouping=True)
    res_out_fmt = locale.format_string(fmt_out, resultado_num, grouping=True)

    msg = f"{s_origem} {val_in_fmt} ({n_origem}) equivalem a {s_destino} {res_out_fmt} ({n_destino})."

    topo, todas = buscar_dados_api()

    valor_para_input = locale.format_string("%.2f", valor_input)
    if c_origem == "BTC":
        valor_para_input = "{:.8f}".format(valor_input)
    else:
        valor_para_input = "{:.2f}".format(valor_input)

    return render_template(
        "cotador.html",
        moedas_topo=topo,
        moedas_todas=todas,
        resultado=True,
        mensagem_resultado=msg,
        valor_post=valor_para_input,  # Resolve as casas decimais após a vírgula
        moeda_origem_post=c_origem,
        moeda_destino_post=c_destino,
    )


if __name__ == "__main__":
    app.run(debug=True)
