from flask import Blueprint, render_template

bp_cep = Blueprint("cep", __name__)


@bp_cep.route("/cep")
def home():
    return render_template("em_breve.html", titulo="CEP")
