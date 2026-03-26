import locale

import requests
from flask import Flask, render_template, request

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

app = Flask(__name__)


@app.route("/")
def home():
    moedas_busca = "USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL,ARS-BRL,CAD-BRL,JPY-BRL,CHF-BRL,AUD-BRL,CNY-BRL"
    url = f"https://economia.awesomeapi.com.br/last/{moedas_busca}"

    resposta = requests.get(url)
    dados = resposta.json()

    lista_topo = []
    lista_completa = []

    for chave, info in dados.items():
        valor_venda = float(info["bid"])
        nome_limpo = info["name"].split("/")[0]

        moeda_obj = {
            "nome": nome_limpo,
            "valor": f"{valor_venda:.2f}",
            "valor_num": valor_venda,
            "codigo": info["code"],
        }

        lista_completa.append(moeda_obj)

        if info["code"] in ["USD", "EUR", "BTC"]:
            lista_topo.append(moeda_obj)

    lista_completa = sorted(lista_completa, key=lambda x: x["nome"])

    return render_template(
        "cotador.html", moedas_topo=lista_topo, moedas_todas=lista_completa
    )


@app.route("/converter", methods=["POST"])
def converter():
    # 1. Captura e Cálculo
    valor_brl = float(request.form.get("valor", 0))
    preco_moeda = float(request.form.get("moeda", 1))
    resultado_num = valor_brl / preco_moeda

    if preco_moeda > 10000:
        resultado_final = f"{resultado_num:.8f}.replace('.', ',')"
    else:
        resultado_final = locale.format_string('%.2f', resultado_num, grouping=True)

    # 2. Busca de dados
    moedas_busca = "USD-BRL,EUR-BRL,BTC-BRL,GBP-BRL,ARS-BRL,CAD-BRL,JPY-BRL,CHF-BRL"
    url = f"https://economia.awesomeapi.com.br/last/{moedas_busca}"
    dados = requests.get(url).json()

    lista_topo = []
    lista_completa = []

    for chave, info in dados.items():
        valor_venda = float(info["bid"])
        moeda_obj = {
            "nome": info["name"].split("/")[0],
            "valor": f"{valor_venda:.2f}",
            "valor_num": valor_venda,
            "codigo": info["code"],
        }
        lista_completa.append(moeda_obj)

        # Filtra os 3 do topo
        if info["code"] in ["USD", "EUR", "BTC"]:
            lista_topo.append(moeda_obj)

    # Ordena o menu de seleção por nome
    lista_completa = sorted(lista_completa, key=lambda x: x["nome"])

    # 3. Retorno com os nomes de variáveis que o HTML espera
    return render_template(
        "cotador.html",
        moedas_topo=lista_topo,
        moedas_todas=lista_completa,
        resultado=resultado_final,
        valor_origem=f"{valor_brl:.2f}",
    )
