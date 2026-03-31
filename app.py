import os

from flask import Flask

from extensions import db
from routes.moedas import bp_moedas


def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "canivete.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Registra o blueprint das moedas
    app.register_blueprint(bp_moedas)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
