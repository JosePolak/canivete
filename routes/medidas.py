from flask import Blueprint, render_template

bp_medidas = Blueprint("medidas", __name__)


@bp_medidas.route("/medidas")
def home():
    return render_template("em_breve.html", titulo="Medidas")
