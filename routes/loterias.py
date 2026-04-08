from flask import Blueprint, render_template

bp_loterias = Blueprint("loterias", __name__)


@bp_loterias.route("/loterias")
def home():
    return render_template("em_breve.html", titulo="Loterias")
