import locale

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

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
    valor_input = float(request.form.get("valor", 0))
    preco_moeda = float(request.form.get("moeda", 1))
    direcao = request.form.get("direcao")

    # Busca o nome da moeda selecionada para a mensagem (opcional)
    # Aqui pode-se passar o nome da moeda pelo form também se se quiser facilitar

    if direcao == "brl_to_ext":
        # Quanto de moeda estrangeira eu compro com X reais? (Divisão)
        resultado_num = valor_input / preco_moeda
        # simbolo = ""  # Aqui você pode mapear o símbolo da moeda se quiser
        msg = f"Com {locale.format_string('%.2f', valor_input, grouping=True)} Reais, você compra {locale.format_string('%.2f', resultado_num, grouping=True)} na moeda selecionada."
    else:
        # Quanto custa X de moeda estrangeira em reais? (Multiplicação)
        resultado_num = valor_input * preco_moeda
        msg = f"Para comprar {locale.format_string('%.2f', valor_input, grouping=True)} na moeda selecionada, você precisará de R$ {locale.format_string('%.2f', resultado_num, grouping=True)}."

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
