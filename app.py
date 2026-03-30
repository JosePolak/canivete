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
}

# Configura o padrão brasileiro para números e moedas
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except Exception:
    # Caso locale não esteja instalado, usa o padrão
    locale.setlocale(locale.LC_ALL, "")


def buscar_dados_api():
    """Função auxiliar para evitar repetição de código"""
    moedas_busca = "USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL,ARS-BRL,CAD-BRL,JPY-BRL,CHF-BRL"
    url = f"https://economia.awesomeapi.com.br/last/{moedas_busca}"
    dados = requests.get(url).json()

    lista_topo = []
    lista_completa = []

    for chave, info in dados.items():
        valor_venda = float(info["bid"])

        # Formata o valor com separador de milhar (.) e decimal (,)
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

    lista_completa = sorted(lista_completa, key=lambda x: x["nome"])
    return lista_topo, lista_completa


@app.route("/")
def home():
    topo, todas = buscar_dados_api()
    return render_template("cotador.html", moedas_topo=topo, moedas_todas=todas)


@app.route("/converter", methods=["POST"])
def converter():
    # 1. Captura e separa os dados enviados
    moeda_info = request.form.get("moeda_data", "1|Moeda|BRL")
    preco_moeda, nome_moeda, codigo_moeda = moeda_info.split("|")
    preco_moeda = float(preco_moeda)

    valor_input = float(request.form.get("valor", 0))
    direcao = request.form.get("direcao")

    # 2. Busca o símbolo (usa $ como padrão se não encontrar no dicionário)
    simbolo = SIMBOLOS.get(codigo_moeda, "$")

    # 3. Formatação Brasileira (Locale)
    val_in_fmt = locale.format_string("%.2f", valor_input, grouping=True)

    if direcao == "brl_to_ext":
        res_num = valor_input / preco_moeda
        res_fmt = locale.format_string(
            "%.8f" if codigo_moeda == "BTC" else "%.2f", res_num, grouping=True
        )

        msg = f"Com R$ {val_in_fmt} (Real), você compra {simbolo} {res_fmt} ({nome_moeda.title()})."
    else:
        res_num = valor_input * preco_moeda
        res_fmt = locale.format_string("%.2f", res_num, grouping=True)

        # Formata a entrada (moeda estrangeira) - 8 casas se for BTC
        val_in_fmt_ajustado = locale.format_string(
            "%.8f" if codigo_moeda == "BTC" else "%.2f", valor_input, grouping=True
        )

        msg = f"Para comprar {simbolo} {val_in_fmt_ajustado} ({nome_moeda.title()}), você precisará de R$ {res_fmt} (Real)."

    topo, todas = buscar_dados_api()

    return render_template(
        "cotador.html",
        moedas_topo=topo,
        moedas_todas=todas,
        resultado=True,  # Ativa o box
        mensagem_resultado=msg,
    )


if __name__ == "__main__":
    app.run(debug=True)
