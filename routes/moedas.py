import os

import requests
from flask import Blueprint, redirect, render_template, request, url_for

from extensions import db
from models import Historico

bp_moedas = Blueprint("moedas", __name__)

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


def formatar_br(valor, casas=2):
    """Transforma 1000.5 para '1.000,50' sem depender de configurações do sistema."""
    try:
        # Cria o padrão americano primeiro (1,000.50)
        fmt = f"{valor:,.{casas}f}"
        # Inverte os separadores para o padrão brasileiro
        return fmt.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00"


def buscar_dados_api():
    chave = os.getenv("HG_API_KEY")
    url = f"https://api.hgbrasil.com/finance?key={chave}"

    lista_topo = []
    lista_completa = []

    try:
        response = requests.get(url, timeout=10)
        dados = response.json()
        currencies = dados.get("results", {}).get("currencies", {})
        moedas_alvo = ["USD", "EUR", "BTC", "GBP", "ARS", "CAD", "JPY", "CHF"]

        for codigo in moedas_alvo:
            if codigo in currencies:
                info = currencies[codigo]
                valor_venda = float(info.get("buy", 0))

                moeda_obj = {
                    "nome": info.get("name"),
                    "valor": formatar_br(valor_venda),
                    "valor_num": valor_venda,
                    "codigo": codigo,
                }
                lista_completa.append(moeda_obj)
                if codigo in ["USD", "EUR", "BTC"]:
                    lista_topo.append(moeda_obj)
    except Exception as e:
        print(f"Erro na API: {e}")
        reserva = [
            {"nome": "Indisponível", "valor": "---", "valor_num": 0.0, "codigo": "ERR"}
        ]
        return reserva, reserva

    return lista_topo, sorted(lista_completa, key=lambda x: x["nome"])


@bp_moedas.route("/")
def home():
    topo, todas = buscar_dados_api()
    historico = Historico.query.order_by(Historico.data_hora.desc()).limit(10).all()
    return render_template(
        "cotador.html", moedas_topo=topo, moedas_todas=todas, historico=historico
    )


@bp_moedas.route("/converter", methods=["POST"])
def efetuar_conversao():
    origem_raw = request.form.get("moeda_origem", "1.0|Real|BRL")
    v_origem, n_origem, c_origem = origem_raw.split("|")
    v_origem = float(v_origem)

    destino_raw = request.form.get("moeda_destino", "1.0|Real|BRL")
    v_destino, n_destino, c_destino = destino_raw.split("|")
    v_destino = float(v_destino)

    try:
        valor_raw = request.form.get("valor", "0")
        # Limpa tudo: remove pontos de milhar e converte vírgula em ponto para o Python calcular
        valor_limpo = valor_raw.replace(".", "").replace(",", ".")
        valor_input = float(valor_limpo) if valor_limpo.strip() else 0.0
    except ValueError:
        valor_input = 0.0

    valor_em_reais = valor_input * v_origem
    resultado_num = valor_em_reais / v_destino

    s_origem = SIMBOLOS.get(c_origem, "$")
    s_destino = SIMBOLOS.get(c_destino, "$")

    casas_in = 8 if c_origem == "BTC" else 2
    casas_out = 8 if c_destino == "BTC" else 2

    # Formatações para a mensagem de texto
    val_in_fmt = formatar_br(valor_input, casas_in)
    res_out_fmt = formatar_br(resultado_num, casas_out)

    msg = f"{s_origem} {val_in_fmt} ({n_origem}) equivalem a {s_destino} {res_out_fmt} ({n_destino})."

    # Salva no Banco de Dados
    nova_consulta = Historico(
        moeda_origem=n_origem,
        moeda_destino=n_destino,
        valor_entrada=valor_input,
        valor_saida=resultado_num,
    )
    db.session.add(nova_consulta)
    db.session.commit()

    topo, todas = buscar_dados_api()
    historico = Historico.query.order_by(Historico.data_hora.desc()).limit(10).all()

    # AQUI ESTÁ A SOLUÇÃO: Forçamos a vírgula para voltar ao campo de texto (input)
    valor_para_input = formatar_br(valor_input, casas_in)

    return render_template(
        "cotador.html",
        moedas_topo=topo,
        moedas_todas=todas,
        historico=historico,
        resultado=True,
        mensagem_resultado=msg,
        valor_post=valor_para_input,  # Agora volta como '10.000,00'
        moeda_origem_post=c_origem,
        moeda_destino_post=c_destino,
    )


@bp_moedas.route("/limpar", methods=["POST"])
def limpar_historico():
    try:
        db.session.query(Historico).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("moedas.home"))
